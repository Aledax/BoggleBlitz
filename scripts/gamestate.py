import threading
from customlib import *
from boggle import Board

playTime = 120
maxPlayers = 6
wordScores = {3:1, 4:3, 5:5, 6:7, 7:9, 8:11, 9:13}

class Player:
    def __init__(self):
        self.username = "n/a"
        self.ready = False
        self.playedWords = []
        
    @property
    def score(self):
        return sum([wordScores[len(word)] for word in self.playedWords])

class TruncatedGameState: # For sending to clients (can't pickle board or lock)
    def __init__(self, gameState):
        self.letters = gameState.board.letters
        self.players = gameState.players
        self.spectators = gameState.spectators
        self.phase = gameState.phase
        self.timer = gameState.timer

class GameState: # Represents one game
    def __init__(self):
        self.board = Board()
        self.players = {}
        self.spectators = {}

        self.phase = "idle" # idle / countdown / play / results
        self.timer = 0

        self.lock = threading.RLock()

    @property
    def truncated(self):
        return TruncatedGameState(self)

    @property
    def usernames(self):
        return [player.username for player in self.players.values()]

    @property
    def playedWords(self):
        return [word for word in self.board if self.board[word] != "n/a"]

    def updateClock(self, timePassed):
        with self.lock:
            if self.phase == "idle":
                if len(self.players) >= 2 and all(player.ready for player in self.players.values()):
                    self.phase = "countdown"
                    self.timer = 3
                    print("COUNTDOWN")
            elif self.phase == "countdown":
                self.timer = max(0, self.timer - timePassed)
                if self.timer == 0:
                    self.phase = "play"
                    self.timer = playTime
                    print("PLAY")
            elif self.phase == "play":
                self.timer = max(0, self.timer - timePassed)
                if self.timer == 0:
                    self.phase = "results"
            elif self.phase == "results":
                pass

    def addPlayer(self, peername): # Returns player / spectator
        with self.lock:
            if self.phase == "idle" and len(self.players) < maxPlayers:
                print(peername + " joined players")
                self.players[peername] = Player()
                return "player"
            else:
                print(peername + " joined spectators")
                self.spectators[peername] = Player()
                return "spectator"

    def removePlayer(self, peername):
        with self.lock:
            if peername in self.players:
                print("Removed player " + peername)
                del self.players[peername]
            elif peername in self.spectators:
                print("Removed spectator " + peername)
                del self.spectators[peername]
            else:
                print("Error removing player: " + peername + " nonexistent")

    def setUsername(self, peername, username): # Returns unique / taken
        with self.lock:
            if peername in self.players:
                if username not in self.usernames:
                    print("Renamed player " + self.players[peername].username + " (" + peername + ") to " + username)
                    self.players[peername].username = username
                    return "unique"
                else:
                    print(peername + " tried to rename to " + username + " but that username is taken")
                    return "taken"
            elif peername in self.spectators:
                if username not in self.usernames:
                    print("Renamed spectator " + self.players[peername].username + " (" + peername + ") to " + username)
                    self.spectators[peername].username = username
                    return "unique"
                else:
                    print(peername + " tried to rename to " + username + " but that username is taken")
                    return "taken"
            else:
                print("Error setting username: " + peername + " nonexistent")
            return "error"

    def setReady(self, peername):
        with self.lock:
            if peername in self.players:
                print(peername + " is ready")
                self.players[peername].ready = True
            elif peername in self.spectators:
                print("Error readying: " + peername + " is a spectator")
            else:
                print("Error readying: " + peername + " nonexistent")

    def playWord(self, peername, word): # Returns unique / taken / invalid
        with self.lock:
            if peername in self.players:
                if word in self.board.playableWords:
                    if self.board.playableWords[word] == "n/a":
                        print(peername + " played " + word)
                        self.board.playableWords[word] = peername
                        self.players[peername].playedWords.append(word)
                        return "unique"
                    else:
                        print(peername + " tried to play " + word + " but it was already played by " + self.board.playableWords[word])
                        return "taken"
                else:
                    print(peername + " tried to play " + word + " but it is not a valid word")
                    return "invalid"
            elif peername in self.spectators:
                print("Error playing word: " + peername + " is a spectator")
            else:
                print("Error playing word: " + peername + " nonexistent")
            return "error"