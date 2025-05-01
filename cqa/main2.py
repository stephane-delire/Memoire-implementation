from sources2.parseur import parse

from sources2.ngfo import is_guarded

from sources2.attack_graph import build_attack_graph, detect_cycle, print_attack_graph
from sources2.attack_graph import draw_attack_graph

from sources2.IsCertain import is_certain_core




# with open("../good_one.cqa", "r") as f:
with open("../03-false-certainty.cqa", "r") as f:
    text = f.read()

# Parse
data = parse(text)
# print(data)

# NGFO
guarded = is_guarded(data["query"])
# print(f"Guarded: {guarded}")

# Attack graph
att_graph = build_attack_graph(data["query"])
# print_attack_graph(att_graph)
# Cycle
cycle = detect_cycle(att_graph)
# print(f"Cycle: {cycle}")
# draw attack graph
# draw_attack_graph(att_graph, "attack_graph")


# isCertain
result = is_certain_core(data["query"], data["database"])
# print(f"IsCertain: {result}")

from sources2.certainty import certainty
data, guarded, graph, cycle, certain = certainty(text, graph_png=False)
print(f"Data: {data}")
print(f"Guarded: {guarded}")
print(f"Graph: {graph}")
print(f"Cycle: {cycle}")
print(f"Certain: {certain}")