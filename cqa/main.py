from sources.certainty import certainty

# with open("../good_one.cqa", "r") as f:
with open("../03-false-certainty.cqa", "r") as f:
    text = f.read()

data, guarded, graph, cycle, certain = certainty(text, graph_png=False)
