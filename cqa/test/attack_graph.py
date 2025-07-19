from typing import List, Set, Tuple
from collections import defaultdict, deque

class Atom:
    def __init__(self, name: str, vars: List[str], key: Set[str], is_neg: bool):
        self.name, self.vars, self.key, self.is_neg = name, vars, key, is_neg

    def __repr__(self):
        return f"{'¬' if self.is_neg else ''}{self.name}({','.join(self.vars)}; key={{{','.join(self.key)}}})"

def compute_closure_via_keys(start_key: Set[str], atoms: List[Atom]) -> Set[str]:
    closure = set(start_key)
    changed = True
    while changed:
        changed = False
        for atom in atoms:
            if atom.key.issubset(closure):
                new = set(atom.vars)
                if not new.issubset(closure):
                    closure |= new
                    changed = True
    return closure

def attack_graph(atoms: List[Atom]) -> List[Tuple[Atom, Atom]]:
    edges = []
    for F in atoms:
        F_closure = compute_closure_via_keys(F.key, atoms)
        for G in atoms:
            if F is G:
                continue
            # Condition stricte de l'article :
            if any(x in F_closure for x in G.key):
                edges.append((F, G))
    return edges

# -- Exemple exact de l’article --
atoms = [
    Atom("Lives", ["p", "t"], {"p"}, False),
    Atom("Born",  ["p", "t"], {"p"}, True),
    Atom("Likes", ["p", "t"], {"p", "t"}, True),
]

for F, G in attack_graph(atoms):
    print(f"{F} → {G}")