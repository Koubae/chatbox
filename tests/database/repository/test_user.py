import pytest
import time

from chatbox.app.core.model.user import UserModel
from chatbox.app.database.repository.user import UserRepository
from tests.conftest import BaseRunner


class TestUserRepository(BaseRunner):

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_create_user(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create_new_user(username, "1234")

		assert user.username == username

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_get_user(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create_new_user(username, "1234")
		user_get: UserModel = repository.get_user(user.id)

		assert user.username == username and user_get.username == username

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_list_users(self):
		repository = UserRepository(self.db)

		users = [f"user{i}" for i in range(10)]
		for user in users:
			repository.create_new_user(user, "1234")

		users_from_db = repository.list_users()
		assert sorted([u.username for u in users_from_db]) == sorted(users)

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_update_user(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create_new_user(username, "1234")
		time.sleep(1)  # sleep so that the modified is 1 second on after

		username_new = username + "new"
		user_updated = repository.update_user(user, {"username": username_new})

		assert (
				user_updated.id == user.id and
				user_updated.created == user.created and
				user_updated.modified != user.modified and
				user_updated.username == username_new
		)

	@pytest.mark.repo_user
	@pytest.mark.repository
	@pytest.mark.database
	def test_delete_user(self):
		repository = UserRepository(self.db)

		username = "user1"
		user: UserModel = repository.create_new_user(username, "1234")
		deleted = repository.delete_user(user.id)

		user_after_delete: None = repository.get_user(user.id)

		assert deleted and user_after_delete is None