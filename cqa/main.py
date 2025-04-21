import pprint

from sources.parseur import Parseur
import sources.rewriter as rewriter
import sources.repairs as repairs
import sources.evaluate as evaluate

with open("../base.cqa", "r") as f:
# with open("../01-bool.cqa", "r") as f:
# with open("../02-args.cqa", "r") as f:
    text = f.read()

# Parse
data = Parseur.parse(text)

# Fo tree
fo_tree = rewriter.rewrite(data)
if fo_tree is None:
    print("La requête n'est pas réécrivable en F-O.")
else:
    print("La requête est réécrivable en F-O.")
    print(fo_tree)

# Repairs
info = repairs.prepare(data["database"])
print(f"Nombre total de réparations : {info['count']}")

gen = repairs.enumerate_repairs(info)
for i, rep in zip(range(10), gen):
    print(f"Réparation {i+1} : {rep}")
    pprint.pp(rep)

# Certainty
print(f"Certainty : {evaluate.is_certain(data)}")

# certain answer (attention none) Déconne...
print(evaluate.certain_answers(data))