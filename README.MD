chatbox
=======

_chatbox a Python Chat Apps using socket/TCP_


Apps
----


Related and other documentations
-------------------------------

* **Koubae: ** [Programming-CookBook/Programming Languages/Python/Socket/chat/](https://github.com/Koubae/Programming-CookBook/tree/master/Programming%20Languages/Python/Socket/chat)
* [Structuring Your Project](https://docs.python-guide.org/writing/structure/)


Credits and Related Projects
------

_This is a list of project where I took some code, or which I found interesting to look up for development and learning purposes_

* [Github Serched](https://github.com/topics/chat-application?l=python&o=desc&s=stars)

* [UsmanJafri/PyconChat](https://github.com/UsmanJafri/PyconChat)
* [KetanSingh11/SimpleChatApp](https://github.com/KetanSingh11/SimpleChatApp)
* [EugenHotaj/talko](https://github.com/EugenHotaj/talko)
* [Hash-Studios/Kivy-Chat-App](https://github.com/Hash-Studios/Kivy-Chat-App)
* [f0lg0/pyChat](https://github.com/f0lg0/pyChat)
* [kraanzu/gupshup](https://github.com/kraanzu/gupshup)
* [NeuralNine/vidstream](https://github.com/NeuralNine/vidstream)

* [pklaus/ping.py|A pure python ping implementation using raw socket. ](https://gist.github.com/pklaus/856268)


* **[Terminal Text Credit: patorjk.com](https://patorjk.com/software/taag/#p=display&h=0&f=Alpha&t=Chatbox)**


### Related

* [zhouchangxun/loadbalancer.py](https://gist.github.com/zhouchangxun/5750b4636cc070ac01385d89946e0a7b)
* [kata198/PumpkinLB](https://github.com/kata198/PumpkinLB)
* [DevDungeon/NanoPot](https://github.com/DevDungeon/NanoPot)
* [Python 2.7 TCP/IP Client and Server](http://pymotw.com/2/socket/tcp.html)

Learn
-----

* [RFC 2616 rfc2616 - section-4](https://www.rfc-editor.org/rfc/rfc2616#section-4)
* [w3.cs.jmu.edu TCPSockets.html](https://w3.cs.jmu.edu/kirkpams/OpenCSF/Books/csf/html/TCPSockets.html)
* [cs.uaf.edu | Network Protocols](https://www.cs.uaf.edu/2016/spring/cs441/lecture/03_24_network_protocol.html)

StackOverflow
------------

* [Python Socket Receive/Send Multi-threading](https://stackoverflow.com/questions/51104534/python-socket-receive-send-multi-threading) <-- Really Really good!
* Check this out: https://stackoverflow.com/questions/43355800/select-thread-multiclient-server-in-python-hangs-after-receiving-first-message
* [PATH issue with pytest 'ImportError: No module named YadaYadaYada'](https://stackoverflow.com/questions/10253826/path-issue-with-pytest-importerror-no-module-named-yadayadayada)

Projects ideas / TODO
----

See [TODO](./TODO.md)

Framework lib references
------------------------

### Standard Library

* socketserver.py

### urllib3

* urllib3/util/connection.py
* urllib3/connection.py
* urllib3/contrib/socks.py

Check `urllib3/connection.py in request_chunked between 261 - 278` to see how to send chunk data with lengh at its start

### distlib

* distlib/util.py <-- Good for certificates

```` 
# run targeted script
pytest -rP -k 'test_to_run'
# Run specific Class 
pytest -rP  tests/tcp/test_socket_tcp_server.py::TestSocketTCPServer
# Run Specific method
pytest -rP  tests/tcp/test_socket_tcp_server.py::TestSocketTCPServer::test_hello
# Run with marker 
pytest -rP -m tcp_core
 
````


### run client recipes
```bash 

make up.client user=--user=bot_1 password=--password=1234
make up.client user=--user=bot_2 password=--password=1234
make up.client user=--user=bot_3 password=--password=1234
make up.client user=--user=bot_4 password=--password=1234

```