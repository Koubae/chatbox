TODOs
=====

_Collection of todos and idea for this project._


Main
----

- Add & search other similar projects, chats open-source/not open_source, tcp apps, etc..
- fix log & prints in terminal: add log error color 
- fix print when chat usage in cli, when writing and receiving a message and receive after wards. the receiving one is in the same line :/
- create bots test


Server
------

- Add colorama print (especially for cli usage)
- Create BroadCaster : should be a separate socket - class ? 

**Main Loop on client connection**

### Database

2. ~~Create Schema~~
4. ~~Create lower ORM (not using a library!)~~
5. Create ORM - Data Mapper ---> SQL implementations
5. Create models | Domain Model --> Business Logic
6. Create DTO | Representation of enties and model . Should it be same as model?

### Login

1. Create SQLite Database
2. Create user table
3. Check how to implement a basic auth
4. Save user password , username, info, and session
5. Request correct password to user
6. 

### Session

- Send session to client
- Session should expire
- Save session in db. 
- Session Data can be pickled object using shelf?


Client
------

- Make client input ">>>" as so, but will disappear and won't be printed in the terminal history
- Save session sent by server and save it somewhere; when client re-starts checks is current session. if still the same then can log in already
- When login for the first time (so basically when creating the user for the first time), change the text when re-questing the password to something like 'new user created, please enter password again'

Projects ideas
--------------

- echo server
- ping server
- heart beat server
- sniffer
- browser like server
- TCP chat 
- Send Database stuff via TCP server - client architecture
- CAN Network