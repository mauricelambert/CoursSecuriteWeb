#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This module implements the vulnerable web app with flags for the lab
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

from urllib.parse import urlparse, parse_qs, unquote
from functools import cache
from http import cookies
import socketserver
import http.server
import sqlite3
import base64
import json
import re

db = sqlite3.connect(":memory:", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

cursor.executemany(
    "INSERT INTO users(username,password) VALUES(?,?)",
    [
        ("%", "FLAG{sqlite_injection}"),
        ("alice", "alice123"),
        ("bob", "bob123"),
        ("charlie", "charlie123"),
    ]
)

db.commit()


def page(title, color, content):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} | Web Security Lab</title>
    <style>
        :root {{
            color-scheme: dark;
            --bg: #0b1120;
            --panel: #111c30;
            --border: #263650;
            --text: #e5edf8;
            --muted: #94a3b8;
            --accent: #22d3ee;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(ellipse at 50% 0%,
                    #152945 0%, transparent 60%),
                var(--bg);
            color: var(--text);
            font-family: Inter, system-ui, sans-serif;
            line-height: 1.6;
        }}

        header {{
            border-bottom: 1px solid var(--border);
            padding: 18px 6%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            background: rgba(11, 17, 32, .85);
        }}

        .brand {{
            color: white;
            font-size: 19px;
            font-weight: 800;
            letter-spacing: 2px;
        }}

        .brand span {{ color: var(--accent); }}

        nav {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }}

        nav a {{
            color: var(--muted);
            text-decoration: none;
            font-size: 13px;
        }}

        nav a:hover {{ color: var(--accent); }}

        main {{
            width: min(760px, calc(100% - 32px));
            margin: 70px auto;
        }}

        .eyebrow {{
            color: var(--accent);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 3px;
            text-transform: uppercase;
        }}

        h1 {{
            font-size: clamp(28px, 5vw, 42px);
            line-height: 1.2;
            margin: 12px 0 28px;
            overflow-wrap: anywhere;
        }}

        .content {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-top: 3px solid {color};
            border-radius: 14px;
            padding: clamp(20px, 5vw, 36px);
            box-shadow: 0 20px 60px #00000030;
            overflow-wrap: anywhere;
        }}

        input, textarea, select {{
            max-width: 100%;
            background: #0b1324;
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 11px 13px;
            font: inherit;
        }}

        input:focus, textarea:focus, select:focus {{
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }}

        button {{
            background: var(--accent);
            color: #08202a;
            border: 0;
            border-radius: 8px;
            padding: 12px 18px;
            font-weight: 800;
            cursor: pointer;
        }}

        button:hover {{ background: #a5f3fc; }}

        a {{ color: var(--accent); }}

        pre {{
            background: #080e19;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }}

        footer {{
            border-top: 1px solid var(--border);
            color: var(--muted);
            padding: 24px;
            text-align: center;
            font-size: 12px;
        }}

        @media (max-width: 600px) {{
            header {{ padding: 16px; }}
            nav {{ gap: 10px; }}
            main {{ margin: 36px auto; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand"><span>◆</span> WEB SECURITY LAB</div>
        <nav>
            <a href="/">Accueil</a>
            <a href="/challenge2">URL</a>
            <a href="/challenge3">HTTP</a>
            <a href="/challenge5">Bruteforce</a>
            <a href="/challenge6">Sessions</a>
            <a href="/challenge7">Injections</a>
            <a href="/demo1">Messagerie</a>
            <a href="/proxy-interface">Proxy</a>
        </nav>
    </header>

    <main>
        <div class="eyebrow">Laboratoire pédagogique</div>
        <h1>{title}</h1>
        <section class="content">
            {content}
        </section>
    </main>

    <footer>
        WEB SECURITY LAB · Environnement de test
    </footer>
</body>
</html>"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            background: #111;
            color: {color};
            font-family: monospace;
            text-align: center;
            margin-top: 100px;
        }}
        .flag {{
            font-size: 30px;
            border: 2px solid {color};
            display: inline-block;
            padding: 20px;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="flag">
        {content}
    </div>
</body>
</html>
"""

@cache
def attack_cache(path: str) -> str:
    r"""
    >>> s = socket()
    >>> s.connect(("127.0.0.1", 8080))
    >>> s.sendall(b'GET / HTTP/1.0\r\nHost: <script>alert("abc")</script>\r\n\r\n')
    >>> s.recv(4096)
    b'HTTP/1.0 200 OK\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Thu, 03 Sep 2026 18:17:52 GMT\r\nContent-type: text/html; charset=utf-8\r\n\r\n\n<!DOCTYPE html>\n<html>\n<head>\n    <title>404 - Page not found</title>\n    <style>\n        body {\n            background: #111;\n            color: yellow;\n            font-family: monospace;\n            text-align: center;\n            margin-top: 100px;\n        }\n        .flag {\n            font-size: 30px;\n            border: 2px solid yellow;\n            display: inline-block;\n            padding: 20px;\n            border-radius: 10px;\n        }\n    </style>\n</head>\n<body>\n    <h1>404 - Page not found</h1>\n    <div class="flag">\n        Welcome on <script>alert("abc")</script>, \'/\' doesn\'t exist.\n    </div>\n</body>\n</html>\n'
    >>> s.close()
    """

    return page(
        "404 - Page not found",
        "yellow",
        f"Welcome on {HOST}, {path!r} doesn't exist.",
    )

HOST = "localhost"
POST_404_PATH = {}

HTML_CHALLENGE1 = page(
    "Challenge 1",
    "#00ff00",
    "FLAG{server_http_localhost}"
).encode("utf-8")


HTML_CHALLENGE2_OK = page(
    "Challenge 2",
    "#00ff00",
    "FLAG{auth_admin_pass_validee}"
).encode("utf-8")

HTML_CHALLENGE2_FAIL = page(
    "Challenge 2",
    "red",
    "Authentication required"
).encode("utf-8")


HTML_CHALLENGE4_FAIL = page(
    "Challenge 4",
    "red",
    "Forbidden"
).encode("utf-8")

HTML_CHALLENGE5_OK = page(
    "Challenge 5",
    "#00ff00",
    "FLAG{basic_auth_bruteforce}"
).encode("utf-8")

HTML_CHALLENGE5_FAIL = page(
    "Challenge 5",
    "red",
    "Authentication required"
).encode("utf-8")

references = {
    "9": "FLAG{IDOR_simulation}"
}

id="9y9q6f"
messages = [
    ("admin", "Bienvenue sur la messagerie interne.")
]

sessions = {}


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        if self.content_length is not None:
            self.send_header("Content-Length", str(self.content_length))
            if self.headers.get("Connection") == "keep-alive":
                self.send_header("Connection", "keep-alive")
        super().end_headers()

    def send_html(self, html):
        if isinstance(html, str):
            html = html.encode("utf-8")
        self.content_length = len(html)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html)

    def challenge1(self):
        self.send_html(HTML_CHALLENGE1)

    def challenge2(self):
        parsed = urlparse(self.path)
        if "admin:pass" in parsed.query:
            self.send_html(HTML_CHALLENGE2_OK)
        else:
            self.send_html(HTML_CHALLENGE2_FAIL)

    def challenge3(self):
        page_content = page(
            "Challenge 3",
            "#00ff00",
            "Look at the HTTP data"
        ).encode("utf-8")
        self.content_length = len(page_content)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("X-Flag", "FLAG{hidden_in_http_headers}")
        self.end_headers()

        self.wfile.write(page_content)

    def challenge4(self):
        host = self.headers.get("Host")
        if host == "flag.local":
            self.send_html(
                page("Challenge 4", "#00ff00", "FLAG{custom_http_method}")
            )
        else:
            self.send_html(HTML_CHALLENGE4_FAIL)

    def challenge5(self):
        auth = self.headers.get("Authorization")
        expected = "Basic " + base64.b64encode(b"admin:noodlegirl").decode()
        if auth == expected:
            self.send_html(HTML_CHALLENGE5_OK)
        else:
            self.content_length = len(HTML_CHALLENGE5_FAIL)
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Challenge5"')
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CHALLENGE5_FAIL)

    def challenge6_login(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        params = dict(
            item.split("=", 1)
            for item in body.split("&")
            if "=" in item
        )

        if (
            params.get("username") == "admin"
            and params.get("password") == "pass"
        ):
            session = {
                "id": 1,
                "username": "admin"
            }

            cookie = base64.b64encode(
                json.dumps(session).encode()
            ).decode()

            self.send_response(302)
            self.send_header("Location", "/challenge6/home")
            self.send_header(
                "Set-Cookie",
                f"session={cookie}; Path=/"
            )
            self.content_length = 0
            self.end_headers()

        else:
            self.content_length = None
            self.send_response(403)
            self.end_headers()

    def challenge6(self):
        self.send_html(page(
            "Espace membre",
            "#22d3ee",
            """
            <p>Connectez-vous pour accéder à votre espace personnel.</p>

            <form method="POST" action="/challenge6/login">
                <label for="username">Nom d'utilisateur</label><br>
                <input id="username" name="username"
                       placeholder="Votre identifiant" required>
                <br><br>

                <label for="password">Mot de passe</label><br>
                <input id="password" name="password" type="password"
                       placeholder="Votre mot de passe" required>
                <br><br>

                <button type="submit">Se connecter →</button>
            </form>
            """
        ))
#         self.send_html(b"""
# <h1>Challenge 6</h1>

# <form method="POST" action="/challenge6/login">
#     <input name="username" placeholder="username"><br><br>
#     <input type="password" name="password" placeholder="password"><br><br>
#     <button>Login</button>
# </form>""")

    def challenge6_home(self):
        username = "guest"
        cookie = cookies.SimpleCookie(self.headers.get("Cookie"))

        if "session" in cookie:
            try:
                session = json.loads(
                    base64.b64decode(
                        cookie["session"].value
                    )
                )
                username = session.get("username", "guest")
            except Exception:
                pass

        html = f"<h1>Welcome {username}</h1>"
        if "<script>" in html.lower():
            html += "<hr><b>FLAG{xss_cookie_tampering}</b>"
        html += "<p><a href='/'>Retour à l'accueil</a></p>"
        self.send_html(page("Mon espace", "#22d3ee", html))

    def challenge7_post(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        name = params.get("name", [""])[0]
        if re.match(r"\w", name) is None:
            return self.challenge7("<h2>Invalid filter</h2>")

        query = (
            "SELECT username,password FROM users WHERE username LIKE"
            f" '%{name}%';"
        )

        output = "<h2>Generated query</h2>"
        output += f"<pre>{query}</pre>"

        try:
            rows = cursor.execute(query).fetchall()
            output += "<h2>Result</h2><pre>"
            if rows:
                for row in rows:
                    output += str(row) + "\n"
            else:
                output += "No result"
            output += "</pre>"
        except Exception as e:
            output += "<h2>SQLite error</h2>"
            output += f"<pre>{e}</pre>"

        self.challenge7(output)

    def challenge7(self, output=""):
        html = f"""
        <p>Recherchez un utilisateur dans l'annuaire interne.</p>

        <form method="POST" action="/challenge7">
            <label for="name">Nom à rechercher</label><br>
            <input id="name" name="name" value="alice"
                   placeholder="Rechercher un utilisateur" required>
            <button type="submit">Rechercher</button>
        </form>

        <hr style="border-color:#263650;margin:28px 0">

        {output}
        """

        self.send_html(page("Annuaire interne", "#22d3ee", html))
        # html = f"""
        # <html>
        # <body style="font-family: monospace">

        # <h1>Challenge 7 - SQL Injection</h1>

        # <form method="POST" action="/challenge7">
        #     Search user :
        #     <input name="name" value="alice">
        #     <button>Search</button>
        # </form>

        # <hr>

        # {output}

        # </body>
        # </html>
        # """

        # self.send_html(html)

    def demo1(self):
        self.send_html(page(
            "Messagerie interne",
            "#a78bfa",
            """
            <p>Identifiez-vous pour accéder à la messagerie.</p>

            <form method="POST" action="/demo1/login">
                <label for="username">Nom d'utilisateur</label><br>
                <input id="username" name="username"
                       placeholder="Votre nom" required>
                <br><br>

                <button type="submit">Accéder à la messagerie →</button>
            </form>
            """
        ))
    #     self.send_html("""
    # <html>
    # <body style="font-family: monospace">

    # <h1>Démonstration 1 - CSRF</h1>

    # <form method="POST" action="/demo1/login">
    #     Nom utilisateur :
    #     <input name="username">
    #     <button>Entrer</button>
    # </form>

    # </body>
    # </html>""")

    def demo1_login(self):
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        username = params.get("username", ["guest"])[0]
        cookie = base64.b64encode(username.encode()).decode()

        self.content_length = 0
        self.send_response(302)
        self.send_header("Location", "/demo1/messages")
        self.send_header("Set-Cookie", f"user={cookie}; Path=/")
        self.end_headers()

    def get_user(self):
        cookie = cookies.SimpleCookie(self.headers.get("Cookie"))
        if "user" in cookie:
            try:
                return base64.b64decode(cookie["user"].value).decode()
            except:
                pass
        return "anonymous"

    def demo1_messages(self):
        user = self.get_user()
        content = """
    <h1>Messages</h1>

    <h2>Historique</h2>
    <ul>
    """

        for author,msg in messages:
            content += (
                f"<li><b>{author}</b> : {msg}</li>"
            )

        content += f"""
    </ul>

    <h2>Envoyer un message</h2>

    <form method="POST" action="/demo1/send">
    <input name="message">
    <button>Send</button>
    </form>

    <hr>
    Utilisateur connecté :
    {user}
    """

        self.send_html(content)

    def demo1_send(self):
        user = self.get_user()
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        params = parse_qs(body)

        msg = params.get("message", [""])[0]

        messages.append((user, msg))

        self.content_length = 0
        self.send_response(302)
        self.send_header("Location", "/demo1/messages")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/challenge1":
            self.challenge1()
        elif path == "/challenge2":
            self.challenge2()
        elif path == "/challenge3":
            self.challenge3()
        elif path == "/challenge5":
            self.challenge5()
        elif path == "/challenge6":
            self.challenge6()
        elif path == "/challenge6/home":
            self.challenge6_home()
        elif path == "/challenge7":
            self.challenge7()
        elif path == "/proxy-interface":
            self.proxy_interface()
        elif path.startswith("/challenge"):
            self.send_html(f"<html><head></head><body><h1>{references.get(path[10:], "NOT A FLAG")}</h1></body></html>")
        elif path == "/demo1":
            self.demo1()
        elif path == "/demo1/messages":
            self.demo1_messages()
        else:
            HOST = self.set_HOST()
            page = attack_cache(path)
            if "<script>" in page and "<script>" not in HOST:
                self.send_html(page.replace('Welcome on', 'Welcome on FLAG{W3B_C4CHe_POIS0NN1nG}'))
            else:
                self.send_html(page)
            # self.send_error(404, "Challenge not found")

    def set_HOST(self, path: str = None) -> str:
        global HOST
        HOST = unquote(self.headers.get("Host", "localhost"))
        if path:
            POST_404_PATH[path] = HOST
        return HOST

    def proxy_interface(self):
        content = """
        <style>
            .forms {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 20px;
            }
            .form-card {
                background: #111c30;
                border: 1px solid #263650;
                border-radius: 14px;
                padding: 24px;
            }
            .form-card h2 {
                font-size: 18px;
                margin-top: 0;
            }
            .form-card p {
                font-size: 13px;
                color: #94a3b8;
            }
            .form-card input {
                width: 100%;
                margin-bottom: 12px;
            }
            .form-card button {
                width: 100%;
            }
            .method {
                color: #22d3ee;
                font-size: 11px;
                letter-spacing: 2px;
                font-weight: bold;
            }
        </style>

        <p>Interface de test des requêtes POST via le proxy HTTP.</p>

        <div class="forms">

            <section class="form-card">
                <span class="method">POST /challenge6/login</span>
                <h2>Connexion</h2>
                <p>Authentification de l'espace membre.</p>
                <form method="POST"
                      action="http://localhost:8000/proxy?path=%2Fchallenge6%2Flogin">
                    <label>Nom d'utilisateur</label>
                    <input name="username" value="admin" required>

                    <label>Mot de passe</label>
                    <input name="password" type="password"
                           placeholder="Mot de passe" required>

                    <button type="submit">Se connecter</button>
                </form>
            </section>

            <section class="form-card">
                <span class="method">POST /challenge7</span>
                <h2>Recherche utilisateur</h2>
                <p>Rechercher un compte dans l'annuaire.</p>
                <form method="POST"
                      action="http://localhost:8000/proxy?path=%2Fchallenge7">
                    <label>Nom à rechercher</label>
                    <input name="name" value="alice" required>

                    <button type="submit">Rechercher</button>
                </form>
            </section>

            <section class="form-card">
                <span class="method">POST /demo1/login</span>
                <h2>Connexion messagerie</h2>
                <p>Accéder à la messagerie interne.</p>
                <form method="POST"
                      action="http://localhost:8000/proxy?path=%2Fdemo1%2Flogin">
                    <label>Nom d'utilisateur</label>
                    <input name="username" value="student" required>

                    <button type="submit">Entrer</button>
                </form>
            </section>

            <section class="form-card">
                <span class="method">POST /demo1/send</span>
                <h2>Envoyer un message</h2>
                <p>Publier un message dans la messagerie.</p>
                <form method="POST"
                      action="http://localhost:8000/proxy?path=%2Fdemo1%2Fsend">
                    <label>Message</label>
                    <input name="message" placeholder="Votre message" required>

                    <button type="submit">Envoyer le message</button>
                </form>
            </section>

        </div>
        """

        self.send_html(page("Client POST du proxy", "#22d3ee", content))

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/challenge6/login":
            self.challenge6_login()
        elif path == "/challenge7":
            self.challenge7_post()
        elif path == "/demo1/login":
            self.demo1_login()
        elif path == "/demo1/send":
            self.demo1_send()
        else:
            flag = b''
            HOST = POST_404_PATH.get(path)
            if HOST is None:
                HOST = self.set_HOST(path)
            elif "<script>" in HOST:
                flag = b' FLAG{INJ3CtION_H11P}'
            
            content = b'404 Page not Found' + flag
            self.content_length = len(content)

            self.send_response(404)
            self.send_header('Host', HOST)
            self.end_headers()
            self.wfile.write(content)
            # self.send_error(404)

        r"""
        >>> payload
        'Connection%3A%20close%0D%0AContent-Type%3A%20text/html%3Bcharset%3Dutf-8%0D%0AContent-Length%3A%20441%0D%0A%0D%0A%3C%21DOCTYPE%20HTML%3E%0A%3Chtml%20lang%3D%22en%22%3E%0A%20%20%20%20%3Chead%3E%0A%20%20%20%20%20%20%20%20%3Cmeta%20charset%3D%22utf-8%22%3E%0A%20%20%20%20%20%20%20%20%3Cstyle%20type%3D%22text/css%22%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Aroot%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20color-scheme%3A%20light%20dark%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20%3C/style%3E%0A%20%20%20%20%20%20%20%20%3Ctitle%3EInfected%20page%3C/title%3E%0A%20%20%20%20%3C/head%3E%0A%20%20%20%20%3Cbody%3E%0A%20%20%20%20%20%20%20%20%3Ch1%3EInfected%20page%3C/h1%3E%0A%20%20%20%20%20%20%20%20%3Cscript%3Ealert%28%22Infected%20page%22%29%3C/script%3E%0A%20%20%20%20%20%20%20%20%3Cp%3EInfected%20by%20bad%20hacker%3C/p%3E%0A%20%20%20%20%20%20%20%20%3Cp%3EBlackhat%20is%20your%20nightmare%3C/p%3E%0A%20%20%20%20%3C/body%3E%0A%3C/html%3E%0A'
        >>> s = socket()
        >>> s.connect(("127.0.0.1", 8080))
        >>> s.sendall(b'POST / HTTP/1.0\r\nHost: test%0D%0A' + payload.encode() + b'%0D%0A%0D%0AHTTP/1.0 200 OK\r\n\r\n')
        >>> s.recv(4096)
        b'HTTP/1.0 404 Not Found\r\nServer: BaseHTTP/0.6 Python/3.14.2\r\nDate: Fri, 04 Sep 2026 06:06:39 GMT\r\nHost: test\r\nConnection: close\r\nContent-Type: text/html;charset=utf-8\r\nContent-Length: 423\r\n\r\n<!DOCTYPE HTML>\n<html lang="en">\n    <head>\n        <meta charset="utf-8">\n        <style type="text/css">\n            :root {\n                color-scheme: light dark;\n            }\n        </style>\n        <title>Infected page</title>\n    </head>\n    <body>\n        <h1>Infected page</h1>\n        <script>alert("Infected page")</script>\n        <p>Infected by bad hacker</p>\n        <p>Blackhat is your nightmare</p>\n    </body>\n</html>\n\r\n\r\nHTTP/1.0 200 OK\r\n\r\n404 Page not Found'
        >>> s.close()
        """

    def do_FLAG(self):
        path = urlparse(self.path).path
        if path == "/challenge4":
            self.challenge4()
        else:
            self.content_length = None
            self.send_error(404, "Challenge not found")


if __name__ == "__main__":
    setattr(Handler, "do_GET", Handler.do_GET)
    setattr(Handler, "do_FLAG", Handler.do_FLAG)
    setattr(Handler, "do_POST", Handler.do_POST)
    serveur = socketserver.TCPServer(("localhost", 8080), Handler)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        serveur.server_close()