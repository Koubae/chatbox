import logging
import hashlib
import hmac
import secrets
import string


__all__ = ["generate_password_hash", "check_password_hash"]
SALT_CHARS: str = string.ascii_letters + string.digits + string.punctuation
DEFAULT_PBKDF2_ITERATIONS: int = 600000
HASH_SEPARATOR: str = "$&?¿"

_logger = logging.getLogger(__name__)


def gen_salt(length: int) -> str:
	"""Generate a random string of SALT_CHARS with specified ``length``."""
	if length <= 0:
		raise ValueError("Salt length must be at least 1.")

	return "".join(secrets.choice(SALT_CHARS) for _ in range(length))


def _hash_scrypt(password: bytes, salt: bytes, args: tuple) -> tuple[str, str]:
	if not args:
		n = 2 ** 15
		r = 8
		p = 1
	else:
		try:
			n, r, p = map(int, args)
		except ValueError:
			raise ValueError(f"'scrypt' takes 3 arguments., {len(args)} given.") from None

	maxmem = 132 * n * r * p  # ideally 128, but some extra seems needed
	return hashlib.scrypt(password, salt=salt, n=n, r=r, p=p, maxmem=maxmem).hex(), f"scrypt:{n}:{r}:{p}",


def _hash_pbkdf2(password: bytes, salt: bytes, args: tuple) -> tuple[str, str]:
	len_args = len(args)
	if len_args < 0 or len_args > 2:
		raise ValueError(f"'pbkdf2' takes 2 arguments, {len_args} given.")

	if len_args == 0:
		hash_name = "sha256"
		iterations = DEFAULT_PBKDF2_ITERATIONS
	elif len_args == 1:
		hash_name = args[0]
		iterations = DEFAULT_PBKDF2_ITERATIONS
	else:
		hash_name = args[0]
		iterations = int(args[1])

	return hashlib.pbkdf2_hmac(hash_name, password, salt, iterations).hex(), f"pbkdf2:{hash_name}:{iterations}",


def _hash_password(method: str, salt: str, password: str) -> tuple[str, str]:
	method, *args = method.split(":")
	salt = salt.encode("utf-8")
	password = password.encode("utf-8")

	if method == "scrypt":
		return _hash_scrypt(password, salt, args)
	elif method == "pbkdf2":
		return _hash_pbkdf2(password, salt, args)

	_logger.warning(f"_hash_password :: Using an unmapped hash method - {method}")
	return hmac.new(salt, password, method).hexdigest(), method


def generate_password_hash(password: str, method: str = "pbkdf2", salt_length: int = 16) -> str:
	"""hash a password.
		methods:
			-  pbkdf2: Default. The parameters are `hash_method` and `iterations` defaults to `pbkdf2:sha256:600000`
			- scrypt: more secure but not available on PyPy. The parameters are `n`, `r`, and `p`, the default is `scrypt:32768:8:1`

		Args:
			password (str): The plaintext password.
			method (str):   The key derivation function and parameters.
			salt_length (int): The number of characters to generate for the salt.

		Returns:
			str: Hashed password
	"""

	salt = gen_salt(salt_length)
	hash_value, actual_method = _hash_password(method, salt, password)
	return f"{actual_method}{HASH_SEPARATOR}{salt}{HASH_SEPARATOR}{hash_value}"


def check_password_hash(password_hash: str, password: str) -> bool:
	"""Check if password hash matches the given password

	Args:
		password_hash (str):
		password (str):

	Returns:
		bool
	"""
	try:
		method, salt, hash_value = password_hash.split(HASH_SEPARATOR, 2)
	except ValueError:
		return False

	return hmac.compare_digest(_hash_password(method, salt, password)[0], hash_value)
