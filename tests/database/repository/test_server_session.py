import pytest
import time

from chatbox.app.database.repository.server_session import ServerSessionRepository, ServerSessionModel
from tests.conftest import BaseRunner


class TestUserRepository(BaseRunner):
	def _create_session(self, repository: ServerSessionRepository):
		session_id = ServerSessionModel.create_session_id()
		data = {"key1": "val1", "key2": ["value" for _ in range(10)], "key3": {"object": "helloworld"}}
		server_session: ServerSessionModel = repository.create_session(session_id, data)
		return session_id, server_session


	@pytest.mark.repo_server_session
	@pytest.mark.repository
	@pytest.mark.database
	def test_create_session(self):
		repository = ServerSessionRepository(self.db)

		session_id, server_session = self._create_session(repository)

		assert server_session.id is 1 and server_session.session_id == session_id and server_session.data.__class__ is dict

	@pytest.mark.repo_server_session
	@pytest.mark.repository
	@pytest.mark.database
	def test_get_session(self):
		repository = ServerSessionRepository(self.db)

		session_id, server_session = self._create_session(repository)

		session_get = repository.get_session(server_session.id)
		session_get_by_session_id = repository.get_session_by_session_id(session_id)

		assert server_session == session_get and server_session == session_get_by_session_id

	@pytest.mark.repo_server_session
	@pytest.mark.repository
	@pytest.mark.database
	def test_list_session(self):
		repository = ServerSessionRepository(self.db)

		sessions_ids = [ServerSessionModel.create_session_id() for i in range(10)]
		for session_id in sessions_ids:
			repository.create_session(session_id, {"key1": "val"})

		sessions = repository.list_session()
		assert sorted([s.session_id for s in sessions]) == sorted(sessions_ids)

	@pytest.mark.repo_server_session
	@pytest.mark.repository
	@pytest.mark.database
	def test_update_session(self):
		repository = ServerSessionRepository(self.db)

		session_id, server_session = self._create_session(repository)
		time.sleep(1)  # sleep so that the modified is 1 second on after

		data_new = server_session.data.copy()
		data_new["newKey"] = [123, 123, 123]

		session_updated = repository.update_session(server_session, data_new)

		assert (
				session_updated.id == server_session.id and
				session_updated.created == server_session.created and
				session_updated.modified != server_session.modified and
				"newKey" in session_updated.data and session_updated.data["newKey"] == [123, 123, 123]
		)

	@pytest.mark.repo_server_session
	@pytest.mark.repository
	@pytest.mark.database
	def test_delete_user(self):
		repository = ServerSessionRepository(self.db)

		session_id, server_session = self._create_session(repository)
		deleted = repository.delete_session(server_session.id)

		session_delete: None = repository.get_session(server_session.id)

		assert deleted and session_delete is None