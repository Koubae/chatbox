import json

import pytest

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.server.router import RouterStopRoute

from tests.conftest import BaseRunner, TCPSocketMock


class TestRouter(BaseRunner):

	@pytest.mark.router
	@pytest.mark.components_server
	@pytest.mark.components
	def test_router_logout_raises(self, socket_create):
		client_conn, _ = TCPSocketMock.login_user(self.tcp_server, socket_create)

		logout_message = _c.make_message(_c.Codes.LOGOUT, json.dumps({"id": client_conn.user.id}))

		with pytest.raises(RouterStopRoute) as _:
			self.tcp_server.router.route(client_conn, logout_message)
