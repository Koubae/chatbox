"""
@author: Federico Bau https://github.com/Koubae/chatbox/tree/master/apps/02_group_chat
TODO: Make docs
"""
import sys
from chatbox import launcher

def main(argv: tuple[str, ...] = tuple(), from_cli=True):
    launcher.run(argv, cli=from_cli)

if __name__ == '__main__':
    main(argv=tuple(sys.argv[1:]), from_cli=True)
