class PackageForServer:
    def __init__(self, packType, username = "n/a", word = "n/a"):
        self.packType = packType # username / ready / word

        self.username = username
        self.word = word

class PackageForClient:
    def __init__(self, packType, truncatedGameState = None, usernameResponse = "n/a", word = "n/a", wordResponse = "n/a"):
        self.packType = packType # state / username / word

        self.truncatedGameState = truncatedGameState
        self.usernameResponse = usernameResponse
        self.word = word
        self.wordResponse = wordResponse