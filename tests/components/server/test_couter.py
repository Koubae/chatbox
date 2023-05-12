import json

import pytest

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.server.router import RouterStopRoute
from chatbox.app.core.model.message import MessageDestination, MessageRole, ServerMessageModel

from tests.conftest import BaseRunner, TCPSocketMock


class TestRouter(BaseRunner):

	@pytest.mark.router
	@pytest.mark.components_server
	@pytest.mark.components
	def test_router_logout_raises(self, socket_create):
		client_conn, _ = TCPSocketMock.login_user(self.tcp_server, socket_create)

		logout_message = _c.make_message(_c.Codes.LOGOUT, json.dumps({"id": client_conn.user.id}))

		sender = MessageDestination(self.tcp_server.server_session.session_id, name=self.tcp_server.name, role=MessageRole.SERVER)
		to = MessageDestination(client_conn.user and client_conn.user.id or client_conn.user_id, name=client_conn.user_name, role=MessageRole.USER)
		message = ServerMessageModel.new_message(sender, sender, to, logout_message)

		with pytest.raises(RouterStopRoute) as _:
			self.tcp_server.router.route(client_conn, message)
