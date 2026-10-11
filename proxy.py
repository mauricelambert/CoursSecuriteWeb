#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This module implements a proxy for the lab
#    Copyright (C) 2026  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##################

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote
from http.client import HTTPConnection
from threading import Lock
from socket import timeout

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8000

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 8080
UPSTREAM_TIMEOUT = 5.0

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "trailer",
    "upgrade",
}


class UpstreamConnection:
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.conn = None
        self.lock = Lock()

    def get(self):
        if self.conn is None:
            self.conn = HTTPConnection(
                self.host,
                self.port,
                timeout=self.timeout,
            )

        return self.conn

    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def reset(self):
        self.close()


UPSTREAM = UpstreamConnection(
    TARGET_HOST,
    TARGET_PORT,
    UPSTREAM_TIMEOUT,
)


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/proxy":
            self.send_error(404, "Not Found")
            return

        params = parse_qs(parsed.query, keep_blank_values=True)
        paths = params.get("path")
        if not paths:
            self.send_error(400, "Missing path parameter")
            return

        target_path = unquote(paths[0])
        if not target_path.startswith("/"):
            self.send_error(400, "path must start with /")
            return

        # https://datatracker.ietf.org/doc/rfc9112/ - 2022
        # 6.3.  Message Body Length
        # 3.  If a message is received with both a Transfer-Encoding and a Content-Length header field, the Transfer-Encoding overrides the Content-Length.
        transfer_encoding = self.headers.get("Transfer-Encoding")
        content_length = self.headers.get("Content-Length")
        is_chunked = transfer_encoding is not None and "chunked" in transfer_encoding.lower()

        if not is_chunked and content_length is None:
            self.send_error(411, "Length Required")
            return

        if not is_chunked:
            try:
                content_length = int(content_length)
            except (TypeError, ValueError):
                self.send_error(400, "Invalid Content-Length")
                return

            if content_length < 0:
                self.send_error(400, "Invalid Content-Length")
                return

        response_started = False

        with UPSTREAM.lock:
            conn = UPSTREAM.get()
            try:
                conn.putrequest("POST", target_path, skip_host=True, skip_accept_encoding=True)
                for key, value in self.headers.items():
                    if key.lower() in HOP_BY_HOP_HEADERS:
                        continue
                    # if key.lower() in {"content-length", "transfer-encoding"}:
                    #     continue
                    conn.putheader(key, value)

                client_ip = self.client_address[0]
                previous_xff = self.headers.get("X-Forwarded-For")

                if previous_xff:
                    xff = f"{previous_xff}, {client_ip}"
                else:
                    xff = client_ip

                conn.putheader("X-Forwarded-For", xff)
                conn.putheader("Connection", "keep-alive")
                # if is_chunked:
                #     conn.putheader("Transfer-Encoding", "chunked")
                # else:
                #     conn.putheader("Content-Length", str(content_length))
                conn.endheaders()

                if is_chunked:
                    self._relay_chunked_body(conn)
                else:
                    self._relay_content_length(conn, content_length)

                response = conn.getresponse()
                self.send_response(response.status, response.reason)
                response_started = True
                for key, value in response.getheaders():
                    if key.lower() not in HOP_BY_HOP_HEADERS:
                        self.send_header(key, value)
     
                self.end_headers()
                self._relay_response(response)
                response.length = 0
                conn._HTTPConnection__response = None
            except (timeout, TimeoutError):
                UPSTREAM.reset()
                if not response_started:
                    self._send_gateway_error(504, "Gateway Timeout")
            except (BrokenPipeError, ConnectionResetError):
                UPSTREAM.reset()
            except Exception as exc:
                UPSTREAM.reset()
                if not response_started:
                    self._send_gateway_error(502, f"Bad Gateway: {exc}")
            # finally:
            #     conn.close()

    def _relay_content_length(self, conn, length):
        remaining = length
        while remaining:
            chunk = self.rfile.read(min(64 * 1024, remaining))
            if not chunk:
                raise ConnectionError("Client closed connection before Content-Length was received")
            conn.send(chunk)
            remaining -= len(chunk)

    def _relay_chunked_body(self, conn):
        while True:
            line = self.rfile.readline()
            if not line:
                raise ConnectionError("Client closed connection during chunked body")

            conn.send(line)
            try:
                size_text = line.split(b";", 1)[0].strip()
                size = int(size_text, 16)
            except ValueError:
                raise ConnectionError("Invalid chunk size")

            if size == 0:
                self._relay_chunked_trailers(conn)
                break

            remaining = size
            while remaining:
                chunk = self.rfile.read(min(64 * 1024, remaining))
                if not chunk:
                    raise ConnectionError("Client closed connection during chunk")

                conn.send(chunk)
                remaining -= len(chunk)

            crlf = self.rfile.read(2)
            if crlf != b"\r\n":
                raise ConnectionError("Invalid chunk terminator")

            conn.send(crlf)

    def _relay_chunked_trailers(self, conn):
        while True:
            line = self.rfile.readline()
            if not line:
                raise ConnectionError("Client closed connection during trailers")
            conn.send(line)
            if line == b"\r\n":
                break

    def _relay_response(self, response):
        status = response.status
        if (100 <= status < 200 or status == 204 or status == 304):
            return

        fp = response.fp
        transfer_encoding = response.getheader("Transfer-Encoding")
        content_length = response.getheader("Content-Length")

        if transfer_encoding is not None:
            encodings = [value.strip().lower() for value in transfer_encoding.split(",")]
            if encodings[-1] != "chunked":
                raise ConnectionError(f"Unsupported Transfer-Encoding: {transfer_encoding}")
            self._relay_chunked_response(fp)

        elif content_length is not None:
            try:
                remaining = int(content_length)
            except ValueError:
                raise ConnectionError(f"Invalid Content-Length: {content_length}")

            if remaining < 0:
                raise ConnectionError(f"Invalid Content-Length: {content_length}")
            self._relay_fixed_response(fp, remaining)
        # else:
        #     self._relay_eof_response(fp)

    def _relay_fixed_response(self, fp, length):
        remaining = length
        while remaining:
            chunk = fp.read(min(64 * 1024, remaining))
            if not chunk:
                raise ConnectionError("Upstream closed before Content-Length bytes")
            self.wfile.write(chunk)
            remaining -= len(chunk)

    def _relay_eof_response(self, fp):
        while True:
            chunk = fp.read(64 * 1024)
            if not chunk:
                break
            self.wfile.write(chunk)

    def _relay_chunked_response(self, fp):
        while True:
            line = fp.readline()
            if not line:
                raise ConnectionError("Upstream closed during chunk size")
            if not line.endswith(b"\r\n"):
                raise ConnectionError("Invalid chunk-size line")

            size_line = line[:-2]
            size_text = size_line.split(b";", 1)[0].strip()
            if not size_text:
                raise ConnectionError("Empty chunk size")

            try:
                size = int(size_text, 16)
            except ValueError:
                raise ConnectionError(f"Invalid chunk size: {size_text!r}")

            self.wfile.write(line)
            if size == 0:
                self._relay_request_chunked_trailers(fp)
                return

            remaining = size
            while remaining:
                chunk = fp.read(min(64 * 1024, remaining))
                if not chunk:
                    raise ConnectionError("Upstream closed during chunk data")
                self.wfile.write(chunk)
                remaining -= len(chunk)

            crlf = fp.read(2)
            if crlf != b"\r\n":
                raise ConnectionError("Invalid chunk terminator")
            self.wfile.write(crlf)


    def _relay_request_chunked_trailers(self, fp):
        while True:
            line = fp.readline()
            if not line:
                raise ConnectionError("Upstream closed during trailers")
            self.wfile.write(line)

            if line == b"\r\n":
                return
            if not line.endswith(b"\r\n"):
                raise ConnectionError("Invalid trailer line")

    def _send_gateway_error(self, status, message):
        try:
            self.send_error(status, message)
        except (BrokenPipeError, ConnectionResetError):
            pass


class ProxyServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    server = ProxyServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler)

    print(f"Proxy listening on http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"Forwarding POST requests to http://{TARGET_HOST}:{TARGET_PORT}")
    print(f"Upstream timeout: {UPSTREAM_TIMEOUT}s")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        server.server_close()
