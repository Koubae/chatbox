import typing as t
import pytest
import os

from chatbox.app.constants import DIR_APP
from chatbox.app.database.orm.sqlite_conn import SQLITEConnectionException, SQLITEConnection
from tests.conftest import BaseRunner


class TestSQLITEConnection(BaseRunner):
	@pytest.mark.sqlite
	@pytest.mark.database
	def test_init_schema_not_exists_raises(self):
		with pytest.raises(SQLITEConnectionException) as error:
			SQLITEConnection(":memory:", schema=os.path.join(DIR_APP, "database", "schema", "no-existing-schema.sql"))

		assert SQLITEConnectionException.ERROR_SCHEMA_INIT_NOT_FOUND.split("]")[0] in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_call_to_unmapped_execution_type_raises_query(self):
		with pytest.raises(SQLITEConnectionException) as _:
			self.db("SELECT * FROM user", execution_type=-1)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_sqlite_connection_exception_raises_on_operation_not_mapped(self):
		with pytest.raises(TypeError) as _:
			SQLITEConnectionException.error_type(-1)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_call_executes_query(self):
		self.db("SELECT * FROM user")
		fetch_one = self.db.cursor.fetchall()

		self.db("SELECT * FROM user WHERE username = :username", {"username": "user1"})
		fetch_two = self.db.cursor.fetchall()

		assert fetch_one.__class__ is list and fetch_two.__class__ is list

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_call_returns_cursor(self):
		db = self.db("SELECT * FROM user")
		assert db is self.db

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_get_throws_sql_connection_exception(self):
		with pytest.raises(SQLITEConnectionException) as error:
			self.db.get("SELECT * FROM tablewhatever")

		assert SQLITEConnectionException.ERROR_GET in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_get_return_none_when_not_found(self):
		user = self.db.get("SELECT * FROM user WHERE username = :username", {"username": "random-guy"})
		assert user is None

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_create_and_get_items(self):
		user = {"username": "user1", "password": "1234"}

		result: t.Any = (
			self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", [user, ])
			.get("SELECT * FROM user")
		)

		assert {"username": result["username"], "password": result["password"]} == user and self.db.created is 1

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_list_return_empty_list_when_not_found(self):
		users = self.db.get_many("SELECT * FROM user WHERE username = :username", {"username": "random-guy"})
		assert len(users) is 0 and users == []

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_list_throws_sql_connection_exception(self):
		with pytest.raises(SQLITEConnectionException) as error:
			self.db.get_many("SELECT * FROM tablewhatever")

		assert SQLITEConnectionException.ERROR_GET_MANY in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_create_throws_sql_connection_exception(self):
		with pytest.raises(SQLITEConnectionException) as error:
			self.db.create("INSERT INTO tablewhatever (username, password) VALUES (:username, :password)", {"username": "ops", "password": None})

		assert SQLITEConnectionException.ERROR_CREATE in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_create_and_list_items(self):
		users = (
			{"username": "user1", "password": "1234"},
			{"username": "user2", "password": "1234"},
			{"username": "user3", "password": "1234"},
		)

		result: t.Any = (
			self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", users)
			.get_many("SELECT * FROM user")
		)

		assert [{"username": user["username"], "password": user["password"]} for user in result] == list(users) and self.db.created is len(users)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_update_throws_sql_connection_exception(self):
		with pytest.raises(SQLITEConnectionException) as error:
			self.db.update("UPDATE tablewhatever SET password = :password_new WHERE username LIKE 'user%'", {"password_new": "somepass"})

		assert SQLITEConnectionException.ERROR_UPDATE in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_update_items(self):
		old_password = "1234"
		user_before_update: list = (
			self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", (
				{"username": "user1", "password": old_password},
				{"username": "user2", "password": old_password},
				{"username": "user3", "password": old_password},
			))
			.get_many("SELECT * FROM user")
		)

		new_password = "4321"
		user_after_update: list = (
			self.db.update("UPDATE user SET password = :password_new WHERE username LIKE 'user%'", {"password_new": new_password})
			.get_many("SELECT * FROM user")
		)

		results = [before["password"] == old_password and after["password"] == new_password for before, after in zip(user_before_update, user_after_update)]
		assert all(results) and self.db.updated == len(user_after_update)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_update_items_updated_is_0_if_nothing_was_updated(self):
		self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", (
			{"username": "user1", "password": "1234"},
			{"username": "user2", "password": "1234"},
			{"username": "user3", "password": "1234"},
		))
		self.db.update("UPDATE user SET password = :password_new WHERE username = :username", {"password_new": "4321", "username": "random-guy"})

		assert self.db.updated is 0

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_delete_throws_sql_connection_exception(self):
		with pytest.raises(SQLITEConnectionException) as error:
			self.db.delete("DELETE FROM tablewhatever")  # noqa

		assert SQLITEConnectionException.ERROR_DELETE in str(error.value)

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_delete(self):
		user = {"username": "user1", "password": "1234"}
		user_created: t.Any = self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", [user, ]) \
			.get("SELECT * FROM user")

		user_after_delete = self.db.delete("DELETE FROM user").get("SELECT * FROM user")  # noqa

		assert user_created["username"] == user["username"] and user_after_delete is None and self.db.deleted is 1

	@pytest.mark.sqlite
	@pytest.mark.database
	def test_delete_deleted_is_0_if_nothing_was_deleted(self):
		self.db.create("INSERT INTO user (username, password) VALUES (:username, :password)", (
			{"username": "user1", "password": "1234"},
			{"username": "user2", "password": "1234"},
			{"username": "user3", "password": "1234"},
		))
		self.db.delete("DELETE FROM user WHERE username = :username", {"username": "random-guy"})

		assert self.db.deleted is 0
