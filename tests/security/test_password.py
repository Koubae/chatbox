import pytest

from chatbox.app.core.security.password import generate_password_hash, check_password_hash


class TestPassword:

	@pytest.mark.password
	@pytest.mark.security
	def test_generate_password_hash_matches_check(self):
		my_password = "myUniquePassword"

		password_hash_methods = ("scrypt", "pbkdf2")
		for hash_method in password_hash_methods:
			password_hash = generate_password_hash(my_password, hash_method)
			check_pass = check_password_hash(password_hash, my_password)

			assert check_pass is True
