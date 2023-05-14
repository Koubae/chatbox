TODOs
=====

_Collection of todos and idea for this project._


Main
----

- Add & search other similar projects, chats open-source/not open_source, tcp apps, etc..
- fix log & prints in terminal: add log error color 
- create bots test
- Fix imports, should be absolute as ->  'chatbox' ... 


Server
------

- Add colorama print (especially for cli usage)
- Create BroadCaster : should be a separate socket - class ? 
- The object.Message probably will need to be moved into a Model and create a "Message Object!"
- fix error when multiple message are received in the same time, we need to add separator between messages!


Model 
-----

- BaseModel should implement to_json and to_jsona_related, but better, find better names and definitions with defaults from sub-class 
  on how to build the json


### Routes

- Create list of commands
  ~~- quit~~ 
  ~~- login (half done, need to create in separate loop so that, if logout, it goes inside the login again!)~~
  ~~- logout~~ 
  - send to
        ~~- send to : all~~
        ~~- send to : user~~ 
        - ~~send to : group~~
        - send to : channel
  - users:
    - list users
      - list users : all
      - list users : logged
      - list users : un-logged
  - group:
    - ~~list groups~~
    - ~~create group~~
    - ~~update group~~ 
    - ~~leave group~~ 
    - ~~delete group~~
  - channel:
    - list channels
      - ~~list channels : all~~
      - list channels : joined
      - list channels : un-joined
    - ~~create channel~~
    - ~~update channel~~
    - ~~delete channel~~
    - ~~leave channel~~
    - ~~join channel~~
    - add user to channel
  - messages:
    - list sent messages : me
    - list received messages : me
    - list all messages : group
    - list all messages : channel
    - delete message

- send_to:: send to "all" should be restricted to admin or super-user

### Database 

- get many by id
- get many by name

- message 
  - How save message on client side???? shelves??? probably just better create a "memory" mysql or an actualy db... 

- channel [Repository, Model]

#### User

- create user type admin QST??: how do we create a new "admin" ? <-- I think only 1 Admin can create other admin . so 1 admin should be created on data_base.sql too!


### Session

- Session Data can be pickled object using shelf? | still not even sure what we want to safe?


Client
------

- Make client input ">>>" as so, but will disappear and won't be printed in the terminal history
- Save session sent by server and save it somewhere; when client re-starts checks is current session. if still the same then can log in already
- When login for the first time (so basically when creating the user for the first time), change the text when re-quest
- chenge text shown when user logs in for the first time to something like 'new user created, please enter password again'

### UI

- Create a "ui" interface 
  - Terminal - terminal ui 
  - GUI - tkinter ui 

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


Done
====


Server
------


### Database

2. ~~Create Schema~~
4. ~~Create lower ORM (not using a library!)~~
5. ~~Create ORM - Data Mapper ---> SQL implementations~~
5. ~~Create models | Domain Model --> Business Logic~~
6. ~~Create DTO | Representation of enties and model . Should it be same as model?~~

#### User

- ~~create "data_base.sql" sql to populate the database if not exists!~~
- ~~create user type super | Add super user on the data.sql~~

### Login

1. ~~Create SQLite Database~~
2. ~~Create user table~~
3. ~~Check how to implement a basic auth~~
4. ~~Save user password , username, info, and session~~
5. ~~Request correct password to user~~
6. ~~send to client also the user id (that is, the database id!)~~
7. ~~Add the user into the session "data", then if user logs in and is inside. the user shouldn't log in again!~~
8. ~~Add login into a separate module?~~

### Session

- ~~Send session to client~~
- ~~Session should expire~~
- ~~Save session in db.~~ 


### Message

- ~~message [Repository, Model] . moved from object.Message to this new implementation~~

### Group

- ~~group [Repository, Model]~~

Client
------

### UI

- ~~fix print when chat usage in cli, when writing and receiving a message and receive after wards. the receiving one is in the same line :/~~