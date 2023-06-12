import pygame, sys, time
from pygame.locals import *
from client import Client
import gamestate
from customlib import *

pygame.init()

client = Client(input("Server IPv4 Address: "))

# -- OPTIONS --

# Legend:
# - Window: the whole screen
# - Round rects: the three decorative round rect borders
# - Squares: the small squares containing the nine letters
# - Panel: the large square containing the nine small squares
# - Message: the thin display below the panel
# - Enterbox: the dark display below the message
# - Hourglass: the timer in the center
# - Scorecards: the rectangles containing player scores
# - Title: the label above the scorecards

# Dimensions

windowSize = (1300, 800)
windowBevel = 10

displaySurface = pygame.display.set_mode(windowSize)

roundRectRects = [(50, 50, 500, 700), (580, 50, 140, 700), (750, 50, 500, 700)]
roundRectRadius = 8

squareTLRect = (105, 105, 110, 110)
squareSpacing = 140
squareTextHeight = 6
squareShadowHeight = 10
squareRects = [(squareTLRect[0] + squareSpacing * (i%3), squareTLRect[1] + squareSpacing * int(i/3)) + squareTLRect[2:4] for i in range(9)]

panelRect = (75, 75, 450, 450)

messageRect = (75, 550, 450, 50)

enterboxRect = (75, 625, 450, 100)
enterboxBorder = 5

hourglassRect = (605, 75, 90, 650)
hourglassBorder1 = 5
hourglassBorder2 = 5

scorecardTRect = (775, 200, 450, 75)
scorecardSpacing = 85
scorecardBorder = 5
scorecardTextMarginLeft = 15
scorecardTextMarginRight = 15

titleRect = (775, 75, 450, 100)
titleTextHeight = 6

# Colors

windowColor = "#8766cc"
windowColorLight = "#a58cd9"
windowColorDark = "#693fc0"

roundRectColor = (110, 77, 178)

squareOffColor = "#a3b3c2"
squareOnColor = "#4747eb"
squareShadowOffColor = "#6c8193"
squareShadowOnColor = "#3333cc"
squareTextOffColor = "#141f1f"
squareTextOnColor = "#deeded"
squareTextShadowOffColor = "#677e7e"
squareTextShadowOnColor = "#8fa3a3"

panelColor = "#342673"

messageColor = "#563894"
messageTextStartColor = "#33eeff"
messageTextUniqueColor = "#33ff44"
messageTextTakenColor = "#ffcc33"
messageTextInvalidColor = "#ff4433"

enterboxColor = "#23194d"
enterboxBorderColor = "#342673"
enterboxTextColor = "#e9fbfb"

hourglassBorder1Color = "#563894"
hourglassBorder2Color = "#342673"

scorecardColor = "#23194d"
scorecardBorderNormalColor = "#342673"
scorecardBorderTopColor = "#cde052"
scorecardTextNameNormalColor = "#7466cc"
scorecardTextNameSelfColor = "#3df599"
scorecardTextScoreColor = "#e8e87d"

titleColor = "#4c3181"
titleTextUpperColor = "#f4f4f1"
titleTextLowerColor = "#bcbca9"

# Fonts

squareFont = loadFont("RosaSans-Black.ttf", 100)
messageFont = loadFont("RosaSans-SemiBold.ttf", 33)
enterboxFont = loadFont("RosaSans-Bold.ttf", 66)
scorecardNameFont = loadFont("RosaSans-SemiBold.ttf", 50)
scorecardScoreFont = loadFont("RosaSans-Bold.ttf", 58)
titleFont = loadFont("RosaSans-SemiBold.ttf", 66)

hourglassImage = loadImage("hourglass.png")

# Surfaces

backgroundSurface = pygame.Surface(windowSize, SRCALPHA).convert_alpha()
pygame.draw.polygon(backgroundSurface, windowColorLight, ((0, 0), (windowSize[0], 0), (windowSize[0] - windowBevel, windowBevel), (windowBevel, windowBevel), (windowBevel, windowSize[1] - windowBevel), (0, windowSize[1])))
pygame.draw.polygon(backgroundSurface, windowColorDark, ((windowSize[0], windowSize[1]), (0, windowSize[1]), (windowBevel, windowSize[1] - windowBevel), (windowSize[0] - windowBevel, windowSize[1] - windowBevel), (windowSize[0] - windowBevel, windowBevel), (windowSize[0], 0)))
pygame.draw.rect(backgroundSurface, windowColor, (windowBevel, windowBevel, windowSize[0] - windowBevel * 2, windowSize[1] - windowBevel * 2))
for rect in roundRectRects:
    drawRoundRectTopLeft(backgroundSurface, rect[0:2], rect[2:4], roundRectRadius, roundRectColor)
pygame.draw.rect(backgroundSurface, panelColor, panelRect)
pygame.draw.rect(backgroundSurface, messageColor, messageRect)
pygame.draw.rect(backgroundSurface, enterboxBorderColor, enterboxRect)
drawShrunkenRect(backgroundSurface, enterboxColor, enterboxRect, enterboxBorder)
pygame.draw.rect(backgroundSurface, hourglassBorder1Color, hourglassRect)
drawShrunkenRect(backgroundSurface, hourglassBorder2Color, hourglassRect, hourglassBorder1)
pygame.draw.rect(backgroundSurface, titleColor, titleRect)
blitRectCenter(backgroundSurface, titleFont.render("Boggle!", True, titleTextLowerColor), titleRect, (0, titleTextHeight / 2))
blitRectCenter(backgroundSurface, titleFont.render("Boggle!", True, titleTextUpperColor), titleRect, (0, titleTextHeight / -2))

# Input

adjacentIndices = {0:(1,3,4), 1:(0,2,3,4,5), 2:(1,4,5), 3:(0,1,4,6,7), 4:(0,1,2,3,5,6,7,8), 5:(1,2,4,7,8), 6:(3,4,7), 7:(3,4,5,6,8), 8:(4,5,7)}

class App:
    def __init__(self):
        self.client = client
        self.client.app = self

        self.clock = pygame.time.Clock()
        self.refreshRate = 60
        self.previousClockTime = time.perf_counter()

        self.displaySurface = displaySurface
        pygame.display.set_caption("Boggle!")

        self.squareSurfaces = [pygame.Surface(squareTLRect[2:4], SRCALPHA).convert_alpha() for i in range(9)]
        self.messageSurface = pygame.Surface(messageRect[2:4], SRCALPHA).convert_alpha()
        self.enterboxSurface = pygame.Surface(enterboxRect[2:4], SRCALPHA).convert_alpha()
        self.hourglassSurface = pygame.Surface(hourglassImage.get_size(), SRCALPHA).convert_alpha()
        self.scorecardSurfaces = []

        self.updateMessageSurface("start", ready = False)

        self.inputIndices = []
        self.inputWord = ""

        self.loop()

    def loop(self):
        while True:
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if self.client.state.phase == "idle":
                        if event.key == K_SPACE: # Space
                            self.updateMessageSurface("start", ready = True)
                            self.client.sendReady()
                    elif self.client.state.phase == "play":
                        if event.unicode.isalpha(): # Letter
                            self.addLetter(event.unicode.upper())
                        elif event.key == K_BACKSPACE: # Backspace
                            self.removeLetter()
                        elif event.key == K_RETURN: # Return
                            self.submitWord()

            self.displaySurface.blit(backgroundSurface, (0, 0))

            self.updateSquareSurfaces()
            for i in range(9): self.displaySurface.blit(self.squareSurfaces[i], squareRects[i][0:2])

            self.displaySurface.blit(self.messageSurface, messageRect)
            self.displaySurface.blit(self.enterboxSurface, enterboxRect)

            self.updateHourglassSurface()
            if self.client.state.phase == "play":
                self.displaySurface.blit(self.hourglassSurface, addVector(hourglassRect[0:2], unitVector(2, hourglassBorder1 + hourglassBorder2)))

            self.updateScorecardSurfaces()
            for i in range(len(self.scorecardSurfaces)): self.displaySurface.blit(self.scorecardSurfaces[i], addVector(scorecardTRect[0:2], (0, i * scorecardSpacing)))

            pygame.display.update()
            self.clock.tick(self.refreshRate)
                                
    def addLetter(self, key):
        # if self.inputIndices == [] or (index in adjacentIndices[self.inputIndices[-1]] and index not in self.inputIndices):
        #     self.inputIndices.append(index)
        #     self.inputWord += self.client.state.letters[int(index/3)][index%3]
        #     self.updateEnterboxSurface()
        if len(self.inputWord) < 9: self.inputWord += key
        self.updateEnterboxSurface()

    def removeLetter(self):
        # if self.inputIndices != []:
        #     self.inputIndices = self.inputIndices[:-1]
        #     self.inputWord = self.inputWord[:-1]
        #     self.updateEnterboxSurface()
        if self.inputWord != "": self.inputWord = self.inputWord[:-1]
        self.updateEnterboxSurface()

    def submitWord(self):
        # if len(self.inputIndices) >= 3:
        #     self.client.sendWord(self.inputWord.lower())
        #     self.inputIndices = []
        #     self.inputWord = ""
        #     self.updateEnterboxSurface()
        if len(self.inputWord) >= 3:
            self.client.sendWord(self.inputWord.lower())
            self.inputWord = ""
            self.updateEnterboxSurface()

    def updateSquareSurfaces(self):
        self.squareSurfaces = []
        for i in range(9):
            surface = pygame.Surface(squareTLRect[2:4], SRCALPHA).convert_alpha()

            if self.client.state.phase == "idle" or self.client.state.phase == "countdown":
                surface.fill(squareOffColor)
                pygame.draw.rect(surface, squareShadowOffColor, (0, 0, squareTLRect[2], squareShadowHeight))
            elif self.client.state.phase == "play" or self.client.state.phase == "results":
                letter = self.client.state.letters[int(i/3)][i%3]
                if i in self.inputIndices:
                    bgColor = squareOnColor
                    shadowColor = squareShadowOnColor
                    textTopColor = squareTextOnColor
                    textBotColor = squareTextShadowOnColor
                else:
                    bgColor = squareOffColor
                    shadowColor = squareShadowOffColor
                    textTopColor = squareTextOffColor
                    textBotColor = squareTextShadowOffColor
                surface.fill(bgColor)
                pygame.draw.rect(surface, shadowColor, (0, 0, squareTLRect[2], squareShadowHeight))
                blitSurfaceCenter(surface, squareFont.render(letter, True, textBotColor), (0, squareTextHeight / 2))
                blitSurfaceCenter(surface, squareFont.render(letter, True, textTopColor), (0, squareTextHeight / -2))
            
            self.squareSurfaces.append(surface)

    def updateMessageSurface(self, messageType, ready = False, word = "n/a"):
        if messageType == "start":
            color = messageTextStartColor
            if ready:
                text = "Waiting for other players..."
            else:
                text = "Press Space to start"
        elif messageType == "unique":
            color = messageTextUniqueColor
            text = word.upper() + ": +" + str(gamestate.wordScores[len(word)])
        elif messageType == "taken":
            color = messageTextTakenColor
            text = word.upper() + " has been played!"
        elif messageType == "invalid":
            color = messageTextInvalidColor
            text = word.upper() + " is an invalid word!"

        self.messageSurface.fill((0,0,0,0))
        blitSurfaceCenter(self.messageSurface, messageFont.render(text, True, color))

    def updateEnterboxSurface(self):
        self.enterboxSurface.fill((0,0,0,0))
        blitSurfaceCenter(self.enterboxSurface, enterboxFont.render(self.inputWord, True, enterboxTextColor))

    def updateHourglassSurface(self):
        self.hourglassSurface.fill((0,0,0,0))
        y = (hourglassRect[3] - 2 * (hourglassBorder1 + hourglassBorder2)) * (1 - self.client.state.timer / gamestate.playTime)
        self.hourglassSurface.blit(hourglassImage, (0, round(y)))

    def updateScorecardSurfaces(self):
        self.scorecardSurfaces = []
        data = [(player.username, player.score) for player in self.client.state.players.values()]
        data.sort(key = lambda x : x[1], reverse = True)

        for i in range(len(data)):
            surface = pygame.Surface(scorecardTRect[2:4], SRCALPHA).convert_alpha()

            if (i == 0): surface.fill(scorecardBorderTopColor)
            else: surface.fill(scorecardBorderNormalColor)
            drawShrunkenRect(surface, scorecardColor, (0, 0) + scorecardTRect[2:4], scorecardBorder)

            if (data[i][0] == self.client.username): blitSurfaceCenterX(surface, scorecardNameFont.render(data[i][0], True, scorecardTextNameSelfColor), scorecardTextMarginLeft)
            else: blitSurfaceCenterX(surface, scorecardNameFont.render(data[i][0], True, scorecardTextNameNormalColor), scorecardTextMarginLeft + scorecardBorder)
            scoreText = scorecardScoreFont.render(str(data[i][1]), True, scorecardTextScoreColor)
            blitSurfaceCenterX(surface, scoreText, scorecardTRect[2] - scoreText.get_width() - scorecardTextMarginRight - scorecardBorder)

            self.scorecardSurfaces.append(surface)

app = App()