import pytest

from chatbox.app.core.components.client.ui.commands import Command, Commands, Codes


class TestCommands:
	@pytest.mark.clientui
	def test_command_returns_default_command(self):
		user_message = "Some message"

		command: Command = Commands.read_command(user_message)

		assert command is Commands.DEFAULT_COMMAND

	@pytest.mark.clientui
	def test_command_reads_quit(self):
		user_message = "/quit some no imporant text"

		command: Command = Commands.read_command(user_message)

		expected_command = Command.QUIT
		assert command is expected_command

	@pytest.mark.clientui
	def test_command_is_stripped_and_lowered(self):
		user_message = " /SeND_to_Channel my_channel"

		command: Command = Commands.read_command(user_message)

		expected_command = Command.SEND_TO_CHANNEL
		assert command is expected_command

	@pytest.mark.clientui
	def test_get_server_code(self):
		command: Command = Command.QUIT

		code: Codes = Commands.get_server_code(command)

		assert code is Codes.QUIT
