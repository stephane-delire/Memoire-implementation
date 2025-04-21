from sources2.parseur import parse


with open("../base.cqa", "r") as f:
# with open("../01-bool.cqa", "r") as f:
# with open("../02-args.cqa", "r") as f:
    text = f.read()

# Parse
data = parse(text)
print(data)