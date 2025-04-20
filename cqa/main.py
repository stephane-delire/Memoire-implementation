from sources.parseur import parseur


with open("../base.cqa", "r") as f:
    text = f.read()

data = parseur.parse(text)
# print(data)
