import pytest
import time

from chatbox.app.core.model.user import UserModel
from chatbox.app.database.repository.user import UserRepository
from tests.conftest import BaseRunner


class TestUserRepository(BaseRunner):

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_create(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create({"username": username, "password": "1234"})

		assert user.username == username

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_get(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create({"username": username, "password": "1234"})
		user_get: UserModel = repository.get(user.id)

		assert user.username == username and user_get.username == username

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_get_many(self):
		repository = UserRepository(self.db)

		users = [f"user{i}" for i in range(10)]
		for user in users:
			repository.create({"username": user, "password": "1234"})

		users_from_db = repository.get_many()
		assert sorted([u.username for u in users_from_db]) == sorted(users)

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_update(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create({"username": username, "password": "1234"})
		time.sleep(1)  # sleep so that the modified is 1 second on after

		username_new = username + "new"
		user_updated = repository.update(user.id, {"username": username_new})

		assert (
				user_updated.id == user.id and
				user_updated.created == user.created and
				user_updated.modified != user.modified and
				user_updated.username == username_new
		)

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_delete(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create({"username": username, "password": "1234"})
		deleted = repository.delete(user.id)

		user_after_delete: None = repository.get(user.id)

		assert deleted and user_after_delete is None

