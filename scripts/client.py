import threading, sys
from easysocket import EasySocket
from gamestate import TruncatedGameState
from packages import PackageForServer

class Client:
    def __init__(self, hostname):
        self.app = None # To be set later
        self.socket = EasySocket()
        
        if not self.socket.connect(hostname, 9999):
            print("Failed to connect to server")
            sys.exit()
        print("Connected to " + self.socket.peername)

        self.pickedUsername = False
        self.username = "n/a"
        self.pendingUsernameResponse = False
        self.state = None

        threading.Thread(target = self.receiverThread, daemon = True).start()
        
        while not self.pickedUsername:
            self.username = input("\nChoose username (10 chars max, alpha only): ")
            if len(self.username) >= 1 and len(self.username) <= 10 and self.username.isalpha():
                self.sendUsername(self.username)
                self.pendingUsernameResponse = True

                # Block until receiver thread receives response
                while self.pendingUsernameResponse: pass
            else:
                print("\nUsername does not follow guidelines")

        # ... Return main thread to App

    def receiverThread(self):
        while True:
            package = self.socket.receiveObject()
            if package == None: break

            if package.packType == "username":
                self.pendingUsernameResponse = False
                if package.usernameResponse == "unique":
                    self.pickedUsername = True
                    print("Welcome, " + self.username + "!")
                elif package.usernameResponse == "taken":
                    print("Username already taken!")
                else:
                    print("Error: Unrecognized package received")
            elif package.packType == "word":
                if package.wordResponse == "unique":
                    print("Unique word!")
                    self.app.updateMessageSurface("unique", word = package.word)
                elif package.wordResponse == "taken":
                    print("Already taken!")
                    self.app.updateMessageSurface("taken", word = package.word)
                elif package.wordResponse == "invalid":
                    print("Invalid word!")
                    self.app.updateMessageSurface("invalid", word = package.word)
                else:
                    print("Error: Unrecognized package received")
            elif package.packType == "state":
                self.state = package.truncatedGameState
            else:
                print("Error: Unrecognized package received")
                
    def send(self, package):
        self.socket.sendObject(package)

    def sendUsername(self, username):
        self.send(PackageForServer("username", username = username))

    def sendReady(self):
        self.send(PackageForServer("ready"))

    def sendWord(self, word):
        self.send(PackageForServer("word", word = word))