import pytest

from chatbox.app.core.model.user import UserModel, UserLoginModel
from chatbox.app.database.repository.user import UserRepository, UserLoginRepository
from chatbox.app.database.repository.server_session import ServerSessionRepository, ServerSessionModel
from tests.conftest import BaseRunner


class TestUserLoginRepository(BaseRunner):
	def _create_user_and_session(self, username: str) -> tuple[ServerSessionRepository, UserRepository, ServerSessionModel, UserModel]:
		server_repo = ServerSessionRepository(self.db)
		user_repo = UserRepository(self.db)

		data = {"key1": "val1", "key2": ["value" for _ in range(10)], "key3": {"object": "helloworld"}}
		server_session: ServerSessionModel = server_repo.create({"session_id":  ServerSessionModel.create_session_id(), "data": data})
		user: UserModel = user_repo.create({"username": username, "password": "1234"})

		return server_repo, user_repo, server_session, user

	@pytest.mark.repo_user_login
	@pytest.mark.repository
	@pytest.mark.database
	def test_create(self):
		repository = UserLoginRepository(self.db)

		_, _, server_session, user = self._create_user_and_session("user1")
		user_login: UserLoginModel = repository.create({"user_id": user.id, "session_id": server_session.id, "attempts": 1})

		assert user_login.user_id == user.id and user_login.session_id == server_session.id

	@pytest.mark.repo_user_login
	@pytest.mark.repository
	@pytest.mark.database
	def test_get(self):
		repository = UserLoginRepository(self.db)

		_, _, server_session, user = self._create_user_and_session("user1")
		user_login: UserLoginModel = repository.create({"user_id": user.id, "session_id": server_session.id, "attempts": 1})
		login_get: UserLoginModel = repository.get(user_login.id)

		assert login_get.id == user_login.id

	@pytest.mark.repo_user_login
	@pytest.mark.repository
	@pytest.mark.database
	def test_get_many(self):
		repository = UserLoginRepository(self.db)
		_, user_repo, server_session, user = self._create_user_and_session("user1")
		repository.create({"user_id": user.id, "session_id": server_session.id, "attempts": 1})

		users_from_db = [user]
		users = [f"user{i}" for i in range(2, 11)]
		for user in users:
			user_db: UserModel = user_repo.create({"username": user, "password": "1234"})
			users_from_db.append(user_db)
			repository.create({"user_id": user_db.id, "session_id": server_session.id, "attempts": 1})

		logins = repository.get_many()
		assert sorted([u.id for u in users_from_db]) == sorted([login.user_id for login in logins])

	@pytest.mark.repo_user_login
	@pytest.mark.repository
	@pytest.mark.database
	def test_update(self):
		repository = UserLoginRepository(self.db)

		_, _, server_session, user = self._create_user_and_session("user1")
		user_login: UserLoginModel = repository.create({"user_id": user.id, "session_id": server_session.id, "attempts": 1})

		with pytest.raises(RuntimeError):
			repository.update(user_login.id, {"user_id": 9999})

	@pytest.mark.repo_user_login
	@pytest.mark.repository
	@pytest.mark.database
	def test_delete(self):
		repository = UserLoginRepository(self.db)

		_, _, server_session, user = self._create_user_and_session("user1")
		user_login: UserLoginModel = repository.create({"user_id": user.id, "session_id": server_session.id, "attempts": 1})

		deleted = repository.delete(user_login.id)

		user_login_after_delete: None = repository.get(user_login.id)

		assert deleted and user_login_after_delete is None
