import typing as t
import pytest
from dataclasses import dataclass

from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item
from tests.conftest import BaseRunner


@dataclass
class ConcreteModel:
	username: str
	password: str

class RepositoryConcrete(RepositoryBase):
	_table: t.Final[str] = "user"
	_name: t.Final[str] = "username"
	_model: ConcreteModel = ConcreteModel


	def create_user(self, username: str, password: str):
		self.create({"username": username, "password": password})

	def create_users(self, users: list[dict]):
		self.create(users)

	def get_user_by_name(self, username: str) -> dict:
		return self.get_by_name(username)

	def list_users(self) -> list[dict]:
		return self.get_many()

	def update_username(self, _id: int, username_new: str) -> t.Self:
		return self.update(_id, {"username": username_new})

	def delete_user(self, _id: int) -> t.Self:
		return self.delete(_id)

	def delete_users(self):
		self.db.delete("DELETE FROM user")  # noqa
		self.deleted = self.db.deleted
		return

	def _build_object(self, data: Item) -> t.Any:
		return data  # need to test raw data in here

class TestRepositoryBase(BaseRunner):
	@pytest.mark.db_abstract
	@pytest.mark.sqlite
	@pytest.mark.database
	def test_subclass_abstract_properties_implementation(self):
		repository = RepositoryConcrete(self.db)

		assert repository._table == "user" and repository._name == "username" and repository._columns == ["username", "password"]

	@pytest.mark.db_abstract
	@pytest.mark.sqlite
	@pytest.mark.database
	def test_subclass_crud_operations(self):
		repository = RepositoryConcrete(self.db)

		# CREATE
		repository.create_user("user1", "1234")
		assert repository.created is 1

		# CREATE Many
		total_users = 5
		repository.create_users([{"username": f"user{i}", "password": "1234"} for i in range(2, total_users + 2)])
		assert repository.created is total_users

		# READ
		user = repository.get_user_by_name("user1")
		assert user["username"] == "user1" and user["id"] is 1 and user["password"] == "1234"

		# LIST
		users = repository.list_users()
		assert [user["id"] for user in users] == list(range(1, 7))

		# UPDATE
		username_old = "user1"
		username_new = "user1-new"
		user_before_update = repository.get_user_by_name(username_old)
		repository.update_username(user_before_update["id"], username_new)
		user_after_update = repository.get_user_by_name(username_new)
		assert (
				repository.get_user_by_name("user1") is None and
				user_before_update["username"] == username_old and
				user_after_update["username"] == username_new and
				repository.updated is 1
		)

		# DELETE
		repository.delete_user(user_before_update["id"])
		use_after_delete = repository.get_user_by_name(username_old)
		assert use_after_delete is None and repository.deleted is 1

		repository.delete_users()
		users = repository.list_users()
		assert len(users) is 0 and repository.deleted is 5
