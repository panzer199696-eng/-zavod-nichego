#!/usr/bin/env python3
"""Минимальный HTTP/HTTPS(CONNECT) прокси на stdlib.

Назначение: дать Docker-контейнеру выход в интернет ЧЕРЕЗ сетевой стек хоста
(на хосте включён AmneziaWG → GitHub доступен, а внутри WSL2-контейнера нет).
Контейнер ходит на host.docker.internal:8899, прокси ретранслирует через хост.

Запуск:  python host_proxy.py 8899
Слушает 0.0.0.0, поэтому доступен из контейнера. Только для локальной отладки.
"""

import socket
import sys
import threading
import select

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
BUF = 65536


def pipe(a, b):
    try:
        while True:
            r, _, _ = select.select([a, b], [], [], 60)
            if not r:
                break
            for s in r:
                data = s.recv(BUF)
                if not data:
                    return
                (b if s is a else a).sendall(data)
    except OSError:
        pass


def handle(client):
    try:
        client.settimeout(30)
        req = b""
        while b"\r\n\r\n" not in req:
            chunk = client.recv(BUF)
            if not chunk:
                client.close()
                return
            req += chunk
        head = req.split(b"\r\n")[0].decode("latin1")
        method, target, _ = head.split(" ", 2)

        if method.upper() == "CONNECT":
            host, _, port = target.partition(":")
            port = int(port or 443)
            upstream = socket.create_connection((host, port), timeout=30)
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        else:
            # обычный HTTP: target = http://host[:port]/path
            no_scheme = target.split("://", 1)[-1]
            hostport, _, path = no_scheme.partition("/")
            host, _, port = hostport.partition(":")
            port = int(port or 80)
            upstream = socket.create_connection((host, port), timeout=30)
            # переписываем строку запроса в origin-form и шлём весь буфер
            new_head = f"{method} /{path} HTTP/1.1".encode("latin1")
            rest = req.split(b"\r\n", 1)[1]
            upstream.sendall(new_head + b"\r\n" + rest)

        upstream.settimeout(30)
        pipe(client, upstream)
    except Exception as e:  # noqa: BLE001
        try:
            sys.stderr.write(f"[proxy] {e}\n")
        except Exception:
            pass
    finally:
        try:
            client.close()
        except OSError:
            pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(128)
    print(f"[proxy] слушаю 0.0.0.0:{PORT}", flush=True)
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
