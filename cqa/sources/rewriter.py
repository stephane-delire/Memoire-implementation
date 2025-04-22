"""
rewriter.py
-----------

Décide si CERTAINTY(q) ∈ FO pour une requête sjfBCQ¬ (self‑join‑free,
conjonctive + atomes négativés ET clés primaires) telle que définie
dans l’article Koutris & Wijsen (PODS 2018).

La procédure suit exactement le **Main Theorem 8** :

    –  Si NEGATION est *weakly‑guarded* **et**
       l’**attack‑graph** est acyclique  ➜  FO‑réécrivabilité.
    –  Sinon  ➜  aucune garantie ; on renvoie `None`.

Pour la partie « construction effective » du rewriting, on implémente
l’algorithme 1 du papier (section 6.3).  Le résultat est un *arbre FO*
facilement sérialisable en SQL.
"""
from __future__ import annotations
import itertools as it
from typing import List, Dict, Tuple, Set, Any, Iterable, Optional

# --------------------------------------------------------------------------- #
#  TYPES
# --------------------------------------------------------------------------- #
Atom      = Tuple[bool, str, int, Tuple[str, ...]]     # (neg, pred, pk_len, args)
FO        = Dict[str, Any]                             # nœud d’arbre

# --------------------------------------------------------------------------- #
#  API UNIQUE
# --------------------------------------------------------------------------- #
def rewrite(parsed: Dict[str, List[Atom]]) -> Optional[FO]:
    """
    :param parsed: sortie du parseur    {"database": …, "query": [Atom, …]}
    :return: arbre FO  (dict)  si F‑O rewritable, sinon  None
    """
    q_plus  = [a for a in parsed["query"] if not a[0]]
    q_minus = [a for a in parsed["query"] if     a[0]]

    # 1)  pré‑requis « weakly‑guarded negation »
    if not _is_weakly_guarded(q_plus, q_minus):
        return None

    # 2)  attack‑graph
    att_graph = _build_attack_graph(parsed["query"])
    if _has_cycle(att_graph):
        return None                                    # Th. 8(1)

    # 3)  construction effective de l’arbre FO (Sec. 6, Algorithme 1)
    return _build_rewriting(parsed["query"], att_graph)   # Th. 8(2)


# --------------------------------------------------------------------------- #
#  WEAKLY‑GUARDED NEGATION   (Def. 3 du papier)
# --------------------------------------------------------------------------- #
def _is_weakly_guarded(pos: List[Atom], neg: List[Atom]) -> bool:
    """
    Pour chaque atome N ∈ q⁻ et pour chaque paire (x,y) de variables de N,
    il doit exister un atome positif P contenant **x ET y**.
    """
    # table d’index : pour chaque variable  →  ensemble des positifs la contenant
    var2pos: Dict[str, Set[int]] = {}
    for idx, (_, _, _, args) in enumerate(pos):
        for v in args:
            var2pos.setdefault(v, set()).add(idx)

    for _, _, _, n_args in neg:
        vars_N = [v for v in n_args if v.islower()]
        for x, y in it.combinations(vars_N, 2):
            # au moins un positif doit contenir les deux
            if not (var2pos.get(x, set()) & var2pos.get(y, set())):
                return False
    return True


# --------------------------------------------------------------------------- #
#  ATTACK‑GRAPH   (Sec. 4 du papier)
# --------------------------------------------------------------------------- #
def _build_attack_graph(all_atoms: List[Atom]) -> Dict[int, Set[int]]:
    """
    Retourne un graphe orienté  atom‑index  →  set(atom‑index attaqués)
    Rq : on se contente d’une traduction directe de la *Definition 2*
         – Fermeture d’un ensemble de variables via les FD « clé→tout ».
         – Un arc  F→G  s’il existe  w∈key(F)  et  u∈key(G) tel que
           u est atteignable depuis w, et u ∉ key(F).
    
    FD : Foreign Dependency, c’est-à-dire une dépendance fonctionnelle
    entre une clé primaire et l’ensemble des autres attributs.
    
    """
    # ----  (1)  table des FD :   key(P)  ->   vars(P)  pour P ∈ q⁺  ----
    fds: List[Tuple[Set[str], Set[str]]] = []
    for neg, _, pk_len, args in all_atoms:
        if neg:                 # seules les positives donnent des FD
            continue
        key = set(args[:pk_len])
        fds.append((key, set(args)))

    def _closure(start: str) -> Set[str]:
        """fermeture de {start} via FD – BFS naïf ; suffisant car q est minuscule"""
        cl = {start}
        changed = True
        while changed:
            changed = False
            for left, right in fds:
                if left <= cl and not right <= cl:
                    cl |= right
                    changed = True
        return cl

    # ----  (2)  arcs ----
    graph: Dict[int, Set[int]] = {i: set() for i in range(len(all_atoms))}
    for i, (_, _, pk_i, a_i) in enumerate(all_atoms):
        key_i = set(a_i[:pk_i])
        for w in key_i:
            for j, (_, _, pk_j, a_j) in enumerate(all_atoms):
                if i == j:
                    continue
                for u in a_j[:pk_j]:
                    if u not in key_i and u in _closure(w):
                        graph[i].add(j)
                        break
    return graph


def _has_cycle(g: Dict[int, Set[int]]) -> bool:
    """Détection DFS (acyclic -> FO)"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in g}

    def dfs(v):
        color[v] = GRAY
        for nxt in g[v]:
            if color[nxt] == GRAY:
                return True          # cycle
            if color[nxt] == WHITE and dfs(nxt):
                return True
        color[v] = BLACK
        return False

    return any(dfs(v) for v in g if color[v] == WHITE)


# --------------------------------------------------------------------------- #
#  BUILD FO REWRITING   (Algorithme 1 de Koutris‑Wijsen, § 6.3)
# --------------------------------------------------------------------------- #
def _build_rewriting(all_atoms: List[Atom],
                     att_graph: Dict[int, Set[int]]) -> FO:
    """
    – Si tous les atomes positifs sont « all‑key » → la conjonction brute suffit
      (cas le plus simple du théorème 8).
    – Sinon on choisit un atome positif F qui (i) n’est PAS all‑key et
      (ii) n’est attaqué par personne, puis on construit :

          F(x)                    ← l’atome pivot
        ∧ ¬∃y [ F(y) ∧ samePK ∧ diffNonKey ]
        ∧   (chaque littéral négatif devient NOT‑EXISTS corrélé sur la PK)
    """
    # ─────────────────── 1.  choisir le pivot F  ────────────────────────────
    pivot_idx = None
    for idx, (neg, _, pk_len, args) in enumerate(all_atoms):
        if neg:
            continue
        if pk_len != len(args) and not any(idx in succ for succ in att_graph.values()):
            pivot_idx = idx
            break

    # cas « tout all‑key » : rewriting trivial
    if pivot_idx is None:
        return {'op': 'and',
                'children': [_atom_node(a) for a in all_atoms]}

    pos_atom = all_atoms[pivot_idx]
    pred, pk_len, full_args = pos_atom[1], pos_atom[2], pos_atom[3]
    pk_vars    = full_args[:pk_len]                     # x₁,…,x_k
    nonpk_vars = full_args[pk_len:]                     # x_{k+1},…

    # ─────────────────── 2.  nœud principal + filtre anti‑doublon ───────────
    atom_node = _atom_node(pos_atom)

    dup_filter = {
        'op'      : 'not_exists_dup',
        'pred'    : pred,
        'pk_vars' : pk_vars,            # variables de clé
        'nvars'   : nonpk_vars,         # variables hors‑clé
        'pk_len'  : pk_len
    }

    # ─────────────────── 3.  NOT‑EXISTS pour chaque littéral négatif ────────
    neg_nodes = []
    for neg, p2, pk2, args2 in all_atoms:
        if not neg:
            continue
        eq_pairs = [(args2[i], pk_vars[i]) for i in range(pk2)]
        neg_nodes.append({
            'op'  : 'not_exists',
            'pred': p2,
            'eq'  : eq_pairs
        })

    return {'op': 'and', 'children': [atom_node, dup_filter, *neg_nodes]}


# --------------------------------------------------------------------------- #
#  PETITES UTILS
# --------------------------------------------------------------------------- #
def _atom_node(atom: Atom) -> FO:
    return {'op': 'atom', 'pred': atom[1], 'args': atom[3]}
