import time
from boggle import Board

board = Board()

input("Press Enter to start")

print("")
for row in board.letters:
    print("  " + " ".join(row))

time.sleep(120)

print("\n\n\n\n\n\n\n\n\n\nDone!")