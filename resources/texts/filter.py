allWordsFile = open("words.txt", "r")
filteredWordsFile = open("newWords.txt", "w")

allWords = allWordsFile.readlines()
filteredWords = []


for word in allWords:
    word = word[:-1] # remove the newline
    if len(word) > 9 or len(word) < 3: continue # length
    if not word.isalpha(): continue # hyphens
    if ord(word[0]) >= 65 and ord(word[0]) <= 90: continue # capitalization
    if word[-1] == "s" and word[:-1] in allWords: continue # plurals
    filteredWords.append(word)

for word in filteredWords:
    filteredWordsFile.write(word + "\n")

allWordsFile.close()
filteredWordsFile.close()