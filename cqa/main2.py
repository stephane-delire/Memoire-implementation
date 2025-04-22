from sources2.parseur import parse
from sources2.rewriter import rewrite

# with open("../base.cqa", "r") as f:
# with open("../01-bool.cqa", "r") as f:
# with open("../02-args.cqa", "r") as f:
# with open("../03-not weakly guarded.cqa", "r") as f:
with open("../04-attack.cqa", "r") as f:
    text = f.read()

# Parse
data = parse(text)
print(data)

rewritted = rewrite(data)
