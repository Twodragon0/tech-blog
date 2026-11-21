"""conftest.py blocks every socket connection to another machine.

Some scripts under test post to live services: buttondown_notify.py mails every
subscriber. A test that forgets its fake must fail instead of sending, so
conftest.py patches the socket layer that requests, urllib and http.client all
end in. Connections to this machine stay allowed for local test servers.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest
import requests

# TEST-NET-1 (RFC 5737) is reserved for documentation and never routed, so even
# with the guard broken these tests reach nobody.
REMOTE = ("192.0.2.1", 443)


def _blocked_log() -> list:
    """conftest.py's record of blocked attempts (loaded under pytest's name)."""
    target = Path(__file__).with_name("conftest.py").resolve()
    conftest = next(
        m
        for m in list(sys.modules.values())
        if (path := getattr(m, "__file__", None)) and Path(path).resolve() == target
    )
    return conftest._BLOCKED_CONNECTIONS


def _create_connection() -> None:
    socket.create_connection(REMOTE, timeout=0.1).close()


def _socket_connect() -> None:
    with socket.socket() as sock:
        sock.connect(REMOTE)


def _socket_connect_ex() -> None:
    with socket.socket() as sock:
        sock.connect_ex(REMOTE)


def _requests_get() -> None:
    with requests.Session() as session:
        session.trust_env = False  # connect directly, not via an env proxy
        session.get(f"http://{REMOTE[0]}/", timeout=0.1)


@pytest.mark.parametrize(
    "connect", [_create_connection, _socket_connect, _socket_connect_ex, _requests_get]
)
def test_connections_to_other_hosts_are_blocked(connect) -> None:
    blocked = _blocked_log()
    with pytest.raises(RuntimeError, match="fake the client instead"):
        connect()
    # Recorded too, so code that swallows the exception still fails its test.
    assert blocked and "192.0.2.1" in blocked[0]
    blocked.clear()  # this attempt was the point of the test


def test_loopback_connections_still_work() -> None:
    with socket.create_server(("127.0.0.1", 0)) as server:
        with socket.create_connection(server.getsockname(), timeout=5):
            conn, _ = server.accept()
            conn.close()
    assert not _blocked_log()
