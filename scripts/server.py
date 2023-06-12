import threading, pygame, time
from easysocket import ServerSocket, EasySocket
from gamestate import GameState
from packages import PackageForClient

class Server:
    def __init__(self):
        self.clientSockets = []
        self.masterSocket = ServerSocket(9999)
        print("Server started: " + self.masterSocket.sockname)

        self.gameState = GameState()

        self.lock = threading.RLock()

        threading.Thread(target = self.acceptThread, daemon = True).start()
        threading.Thread(target = self.gameThread, daemon = True).start()

    def broadcast(self, recipients, package):
        for clientSocket in recipients:
            clientSocket.sendObject(package)

    def acceptThread(self):
        while True:
            clientSocket = EasySocket(self.masterSocket.accept())
            threading.Thread(target = self.clientThread, args = (clientSocket,), daemon = True).start()

    def clientThread(self, clientSocket):
        print("Connection received from " + clientSocket.peername)
        with self.lock:
            self.clientSockets.append(clientSocket)
        self.gameState.addPlayer(clientSocket.peername)

        while True:
            package = clientSocket.receiveObject()
            if package == None: break

            if package.packType == "username":
                self.broadcast([clientSocket], PackageForClient("username", usernameResponse = self.gameState.setUsername(clientSocket.peername, package.username)))
            elif package.packType == "ready":
                self.gameState.setReady(clientSocket.peername)
            elif package.packType == "word":
                self.broadcast([clientSocket], PackageForClient("word", word = package.word, wordResponse = self.gameState.playWord(clientSocket.peername, package.word)))
            else:
                print("Unrecognized package from " + clientSocket.peername)

        print("Connection terminated from " + clientSocket.peername)
        with self.lock:
            self.clientSockets.remove(clientSocket)
        self.gameState.removePlayer(clientSocket.peername)

    def gameThread(self):
        clock = pygame.time.Clock()
        refreshRate = 60
        previousClockTime = time.perf_counter()

        while True:
            currentTime = time.perf_counter()
            passedTime = currentTime - previousClockTime
            previousClockTime = currentTime

            self.gameState.updateClock(passedTime)
            self.broadcast(self.clientSockets, PackageForClient("state", truncatedGameState = self.gameState.truncated))

            clock.tick(refreshRate)

server = Server()
input("Press Enter to exit\n")