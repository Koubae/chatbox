import socket
import threading
import pickle
import os
import sys
import json

from ..utils import create_tcp_socket
from ..constants import APP_NAME, SERVER_CONNECTIONS, BOT_ADMIN_NAME, SERVER_ENCODING

groups = {}
fileTransferCondition = threading.Condition()


class Group:
    def __init__(self, name: str, admin, client: socket.socket):
        self.name: str = name
        self.admin = admin
        self.client: socket.socket = client
        self.clients: dict = {}
        self.offlineMessages: dict = {}
        self.allMembers: set = set()
        self.onlineMembers: set = set()
        self.joinRequests: set = set()
        self.waitClients: dict = {}

        self.init()

    def init(self):
        print("New Group:", self.name, "| Admin: ", self.admin)
        self.clients[self.admin] = self.client
        self.allMembers.add(self.admin)
        self.onlineMembers.add(self.admin)

    def connect(self, username, client):
        self.onlineMembers.add(username)
        self.clients[username] = client

        message: str = f"{username} Connected to {self.name}"
        print(message)
        self.broadcast(message, BOT_ADMIN_NAME)

    def join_request(self, client: socket.socket, username: str):
        self.joinRequests.add(username)
        self.waitClients[username] = client
        message: str = f"{username} has requested to join the group {self.name}"
        print(message)
        self.broadcast(message, BOT_ADMIN_NAME)

    def disconnect(self, client: socket.socket, username):
        if username in self.onlineMembers:
            self.onlineMembers.remove(username)  # remove username from set
        if username in self.clients:
            del self.clients[username]  # remove client and free up space

        # Close socket connections
        client.close()

        message = f'[< {username} > ({self.name})] left the chat!'
        print(message)
        self.broadcast(message, BOT_ADMIN_NAME)

    def broadcast(self, message, username):
        for member in self.onlineMembers:
            if member != username:
                self.clients[member].send(bytes(username + ": " + message, SERVER_ENCODING))


def pyconChat(client, username, groupname):
    while True:
        try:
            msg = client.recv(1024)
            if not msg:
                groups[groupname].disconnect(client, username)
                break
            msg = msg.decode(SERVER_ENCODING)
        except (ConnectionResetError, Exception) as error:
            print(f'Error occurred -> {str(error)}')
            groups[groupname].disconnect(client, username)
            break

        if msg == "/viewRequests":
            client.send(b"/viewRequests")
            client.recv(1024).decode(SERVER_ENCODING)
            if username == groups[groupname].admin:
                client.send(b"/sendingData")
                client.recv(1024)
                client.send(pickle.dumps(groups[groupname].joinRequests))
            else:
                client.send(b"You're not an admin.")
        elif msg == "/approveRequest":
            client.send(b"/approveRequest")
            client.recv(1024).decode(SERVER_ENCODING)
            if username == groups[groupname].admin:
                client.send(b"/proceed")
                usernameToApprove = client.recv(1024).decode(SERVER_ENCODING)
                if usernameToApprove in groups[groupname].joinRequests:
                    groups[groupname].joinRequests.remove(usernameToApprove)
                    groups[groupname].allMembers.add(usernameToApprove)
                    if usernameToApprove in groups[groupname].waitClients:
                        groups[groupname].waitClients[usernameToApprove].send(b"/accepted")
                        groups[groupname].connect(usernameToApprove, groups[groupname].waitClients[usernameToApprove])
                        del groups[groupname].waitClients[usernameToApprove]
                    print("Member Approved:", usernameToApprove, "| Group:", groupname)
                    client.send(b"User has been added to the group.")
                else:
                    client.send(b"The user has not requested to join.")
            else:
                client.send(b"You're not an admin.")
        elif msg == "/disconnect":
            client.send(b"/disconnect")
            client.recv(1024).decode(SERVER_ENCODING)
            groups[groupname].disconnect(client, username)
            break
        elif msg == "/messageSend":
            client.send(b"/messageSend")
            message = client.recv(1024).decode(SERVER_ENCODING)
            groups[groupname].broadcast(message, username)
        elif msg == "/waitDisconnect":
            client.send(b"/waitDisconnect")
            del groups[groupname].waitClients[username]
            print("Waiting Client:", username, "Disconnected")
            break
        elif msg == "/allMembers":
            client.send(b"/allMembers")
            client.recv(1024).decode(SERVER_ENCODING)
            client.send(pickle.dumps(groups[groupname].allMembers))
        elif msg == "/onlineMembers":
            client.send(b"/onlineMembers")
            client.recv(1024).decode(SERVER_ENCODING)
            client.send(pickle.dumps(groups[groupname].onlineMembers))
        elif msg == "/changeAdmin":
            client.send(b"/changeAdmin")
            client.recv(1024).decode(SERVER_ENCODING)
            if username == groups[groupname].admin:
                client.send(b"/proceed")
                newAdminUsername = client.recv(1024).decode(SERVER_ENCODING)
                if newAdminUsername in groups[groupname].allMembers:
                    groups[groupname].admin = newAdminUsername
                    print("New Admin:", newAdminUsername, "| Group:", groupname)
                    client.send(b"Your adminship is now transferred to the specified user.")
                else:
                    client.send(b"The user is not a member of this group.")
            else:
                client.send(b"You're not an admin.")
        elif msg == "/whoAdmin":
            client.send(b"/whoAdmin")
            groupname = client.recv(1024).decode(SERVER_ENCODING)
            client.send(bytes("Admin: " + groups[groupname].admin, SERVER_ENCODING))
        elif msg == "/kickMember":
            client.send(b"/kickMember")
            client.recv(1024).decode(SERVER_ENCODING)
            if username == groups[groupname].admin:
                client.send(b"/proceed")
                usernameToKick = client.recv(1024).decode(SERVER_ENCODING)
                if usernameToKick in groups[groupname].allMembers:
                    groups[groupname].allMembers.remove(usernameToKick)
                    if usernameToKick in groups[groupname].onlineMembers:
                        groups[groupname].clients[usernameToKick].send(b"/kicked")
                        groups[groupname].onlineMembers.remove(usernameToKick)
                        del groups[groupname].clients[usernameToKick]
                    print("User Removed:", usernameToKick, "| Group:", groupname)
                    client.send(b"The specified user is removed from the group.")
                else:
                    client.send(b"The user is not a member of this group.")
            else:
                client.send(b"You're not an admin.")
        elif msg == "/fileTransfer":
            client.send(b"/fileTransfer")
            filename = client.recv(1024).decode(SERVER_ENCODING)
            if filename == "~error~":
                continue
            client.send(b"/sendFile")
            remaining = int.from_bytes(client.recv(4), 'big')
            f = open(filename, "wb")
            while remaining:
                data = client.recv(min(remaining, 4096))
                remaining -= len(data)
                f.write(data)
            f.close()
            print("File received:", filename, "| User:", username, "| Group:", groupname)
            for member in groups[groupname].onlineMembers:
                if member != username:
                    memberClient = groups[groupname].clients[member]
                    memberClient.send(b"/receiveFile")
                    with fileTransferCondition:
                        fileTransferCondition.wait()
                    memberClient.send(bytes(filename, SERVER_ENCODING))
                    with fileTransferCondition:
                        fileTransferCondition.wait()
                    with open(filename, 'rb') as f:
                        data = f.read()
                        dataLen = len(data)
                        memberClient.send(dataLen.to_bytes(4, 'big'))
                        memberClient.send(data)
            client.send(bytes(filename + " successfully sent to all online group members.", SERVER_ENCODING))
            print("File sent", filename, "| Group: ", groupname)
            os.remove(filename)
        elif msg == "/sendFilename" or msg == "/sendFile":
            with fileTransferCondition:
                fileTransferCondition.notify()
        else:
            print("UNIDENTIFIED COMMAND:", msg, " Closing connection with peer... ")
            groups[groupname].disconnect(client, username)


def tcp_accept(client):
    error = ""

    username = ""
    groupname = ""
    try:
        response = client.recv(1024)
        if response:
            response = response.decode(SERVER_ENCODING)
            user = json.loads(response)
            username = user["username"]
            groupname = user["groupname"]
    except (json.JSONDecodeError, KeyError) as error:
        error = str(error)
        username = ""
        groupname = ""

    if not username or not groupname:
        message = f'ERROR:: {error and error or "client did not respond with user name or group name!"} Error during tcp_accept....!'
        print(message)
        client.close()
        return

    if groupname in groups:
        if username in groups[groupname].allMembers:
            groups[groupname].connect(username, client)
            client.send(b"/ready")
        else:
            groups[groupname].member_request(client, username)
            client.send(b"/wait")

    else:
        groups[groupname] = Group(groupname, username, client)

    thread = threading.Thread(target=pyconChat, args=(client, username, groupname,))
    thread.daemon = True
    thread.start()

    client.send(b"/adminReady")



def run(address: tuple[str, int]):
    server = create_tcp_socket(address, "server")
    server.listen(SERVER_CONNECTIONS)
    print(f"{APP_NAME} is running at {address[0]}:{address[1]} ...")

    while True:

        try:
            client, _ = server.accept()
            thread = threading.Thread(target=tcp_accept, args=(client,))
            thread.daemon = True
            thread.start()
        except KeyboardInterrupt as _:
            print(f'[(interrupted by signal 2: SIGINT)] Closing server ....')
            break
        except Exception as exception:
            print(f'[{str(exception)}] Exception Occurred Closing  ....')
            break
        except BaseException as base_exception:
            print(f'[{str(base_exception)}] Base Exception Occurred Closing ....')
            break
