"""
-------------------------------------------------------------------------------
Implémentation de l'algorithme certainty
dans le cadre du Consistent Query Answering (CQA) with conjunctive queries
and negated atoms.

Delire Stéphane.
-------------------------------------------------------------------------------
"""

from sources.certainty import certainty

# with open("examples/good_one.cqa", "r") as f:
with open("examples/03-false-certainty.cqa", "r") as f:
    text = f.read()

data, guarded, graph, cycle, certain = certainty(text, graph_png=False)
