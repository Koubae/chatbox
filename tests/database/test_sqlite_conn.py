import pytest

from tests.conftest import BaseRunner


class TestSQLITEConnection(BaseRunner):

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
	def test_call_returns_self(self):
		db = self.db("SELECT * FROM user")

		assert db is self.db
