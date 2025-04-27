from sources2.parseur import parse
from sources2.ngfo import is_guarded
from sources2.attack_graph import build_attack_graph, detect_cycle, print_attack_graph
from sources2.attack_graph import draw_attack_graph

from sources2.rewriter import rewrite

# with open("../base.cqa", "r") as f:
# with open("../01-bool.cqa", "r") as f:
# with open("../02-args.cqa", "r") as f:
# with open("../03-not weakly guarded.cqa", "r") as f:
# with open("../04-attack.cqa", "r") as f:
with open("../05 - test.cqa", "r") as f:
    text = f.read()

# Parse
data = parse(text)
print(data)

# NGFO
guarded = is_guarded(data["query"])
print(f"Guarded: {guarded}")

# Attack graph
att_graph = build_attack_graph(data["query"])
print_attack_graph(att_graph)
# Cycle
cycle = detect_cycle(att_graph)
print(f"Cycle: {cycle}")
# draw attack graph
draw_attack_graph(att_graph, "attack_graph")