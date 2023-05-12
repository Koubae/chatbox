from chatbox.app.constants import COMMAND_TOKEN


def get_command_target(message: str) -> str:
	target = message.split(COMMAND_TOKEN)[-1].strip()
	if target.startswith("/"):
		return ""
	return target
