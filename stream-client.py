#!/usr/bin/env python3
"""Relay frames from the blinken.org stream to the local UDP driver.

The server streams the current show over a WebSocket as 400-byte frames,
the same format udp-driver accepts. This connects to the stream, forwards
each frame to udp-driver, and reconnects whenever the connection drops.

Requires websocket-client (apt install python3-websocket).
"""

import argparse
import socket
import time

import websocket

DEFAULT_URL = 'wss://blinken.org/api/0/stream'
DEFAULT_PORT = 1337
FRAME_LEN = 400

# Reconnect if no frame arrives for this long. The server sends a frame
# on every step of the running show, so silence means a dead connection.
RECV_TIMEOUT = 120

RETRY_MIN = 1
RETRY_MAX = 60


def relay(url: str, dest, sock: socket.socket):
    ws = websocket.create_connection(url, timeout=RECV_TIMEOUT)
    print(f'Connected to {url}', flush=True)
    try:
        while True:
            frame = ws.recv()
            if isinstance(frame, bytes) and len(frame) == FRAME_LEN:
                sock.sendto(frame, dest)
    finally:
        ws.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('-u', '--url', default=DEFAULT_URL,
                        help=f'stream URL (default {DEFAULT_URL})')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help=f'udp-driver port on localhost (default {DEFAULT_PORT})')
    args = parser.parse_args()

    dest = ('127.0.0.1', args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    delay = RETRY_MIN
    while True:
        started = time.monotonic()
        try:
            relay(args.url, dest, sock)
        except (websocket.WebSocketException, OSError) as e:
            print(f'Stream error: {e}', flush=True)

        # Back off while the server is unreachable, but reconnect quickly
        # after a connection that had been working
        if time.monotonic() - started > RETRY_MAX:
            delay = RETRY_MIN
        time.sleep(delay)
        delay = min(delay * 2, RETRY_MAX)


if __name__ == '__main__':
    main()
