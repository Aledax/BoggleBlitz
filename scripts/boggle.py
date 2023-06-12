import random
from customlib import *

consonants = {"R":7.6, "T":7, "N":6.7, "S":5.7, "L":5.5, "C":4.5, "D":3.4, "P":3.2, "M":3, "H":3, "G":2.5, "B":2, "F":1.8, "Y":1.8, "W":1.3, "K":1.1, "V":1, "X":0.3, "Z":0.3, "J":0.2, "Q":0.2}
vowels = {"E":11.1, "A":8.5, "I":7.5, "O":7.2, "U":3.6}
rareConsonants = ["K", "V", "X", "Z", "J", "Q"]

adjacents = {
    0:[1,3,4],
    1:[0,2,3,4,5],
    2:[1,4,5],
    3:[0,1,4,6,7],
    4:[0,1,2,3,5,6,7,8],
    5:[1,2,4,7,8],
    6:[3,4,7],
    7:[3,4,5,6,8],
    8:[4,5,7]
}

class Board:
    def __init__(self):
        # A 3x3 matrix of the board's 9 capital letters.
        self.letters = makeBoard()
        self.flatLetters = flatten(self.letters)
        # A dictionaty containing all playable words from the board. Values, n/a by default, will be set to player socket names upon being submitted.
        self.playableWords = {word[:-1]:"n/a" for word in loadFile("newWords.txt", "r").readlines() if len(set(word)) == len(word) and all(c in self.flatLetters for c in word[:-1].upper()) and all(self.flatLetters.index(word[i+1].upper()) in adjacents[self.flatLetters.index(word[i].upper())] for i in range(len(word) - 2))}

def makeBoard():
    counts = {letter:0 for letter in [chr(i) for i in range(65, 91)]}
    letters = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
    vowelXs = [0, 1, 2]
    random.shuffle(vowelXs)

    for row in range(3):
        for col in range(3):
            if col == vowelXs[row]:
                addVowel(letters, counts, row, col)
            else:
                addConsonant(letters, counts, row, col)
    
    for row in range(3):
        if letters[row][1] in rareConsonants:
            swap(letters, row, 1, row, random.choice([0, 2]))

    return letters

def addVowel(letters, counts, row, col):
    addLetter(letters, counts, vowels, row, col)

def addConsonant(letters, counts, row, col):
    addLetter(letters, counts, consonants, row, col)

def addLetter(letters, counts, d, row, col):
    while True:
        letter = "-"
        val = random.uniform(0, sum(d.values()))
        for l in d:
            if val <= d[l]:
                letter = l
                break
            else:
                val -= d[l]
        if counts[letter] == 0 and not (l in rareConsonants and any(counts[rc] > 0 for rc in rareConsonants)):
            letters[row][col] = letter
            counts[l] += 1
            return

def swap(letters, r1, c1, r2, c2):
    letters[r1][c1], letters[r2][c2] = letters[r2][c2], letters[r1][c1]