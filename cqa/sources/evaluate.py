# evaluate.py  ──────────────────────────────────────────────────────────────
"""
Boucle d'évaluation CQA.

Usage :
    >>> import evaluate, parser_module as P
    >>> parsed = P.parse(open("instance.txt").read())
    >>> res    = evaluate.certainty(parsed)      # True / False
"""

from __future__ import annotations
import itertools as it
from typing import List, Tuple, Dict, Any
from sources import rewriter, repairs

# ------------------------------------------------------------------ #
#  TYPES DE DONNÉES
# ------------------------------------------------------------------ #
Fact  = Tuple[str, int, Tuple[str, ...]]      # (pred, pk_len, args)
Atom  = Tuple[bool, str, int, Tuple[str, ...]]
Vars  = Dict[str, str]

# ------------------------------------------------------------------ #
#  API PRINCIPALE
# ------------------------------------------------------------------ #
def certainty(parsed: Dict[str, List[Any]]) -> bool:
    """
    Retourne True si la requête est *certaine* (vraie dans toutes
    les réparations), False sinon.
    """
    # 1) tentative FO rewriting
    fo = rewriter.rewrite(parsed)
    if fo is not None:
        return _eval_fo(fo, parsed["database"])

    # 2) fallback : énumération des réparations
    rep_info = repairs.prepare(parsed["database"])
    for rep in repairs.enumerate_repairs(rep_info):
        if not _eval_query(rep, parsed["query"]):
            return False                    # invalide dans cette réparation
    return True                             # valide dans *toutes* les réparations


# ------------------------------------------------------------------ #
#  ÉVALUATION D'UNE RÉÉCRITURE FO
# ------------------------------------------------------------------ #
def _eval_fo(node: Dict[str, Any], db: List[Fact], env: Vars | None = None) -> bool:
    """Évalue l’arbre FO produit par rewriter (existentiel + NOT‑EXISTS)."""
    if env is None:
        env = {}

    op = node["op"]

    # &&  nœud conjonctif
    if op == "and":
        return all(_eval_fo(child, db, env) for child in node["children"])

    # atom  P(x, y, …)
    if op == "atom":
        pred, args = node["pred"], node["args"]
        for _, _, tup in (f for f in db if f[0] == pred):
            new = _unify(args, tup, env)
            if new is not None:
                return True             # ∃ substitution satisfaisante
        return False                    # aucun fait ne matche

    # NOT EXISTS  corrélé
    if op == "not_exists":
        pred, eq = node["pred"], node["eq"]
        for _, _, tup in (f for f in db if f[0] == pred):
            # vérifie corrélations PK = valeurs déjà liées
            if all(tup_left == env.get(right, right) for tup_left, right in eq):
                return False            # un témoin existe → NOT EXISTS échoue
        return True                     # aucun témoin → passe

    raise ValueError(f"nœud FO inconnu : {op}")


# ------------------------------------------------------------------ #
#  ÉVALUATION DIRECTE SUR UNE (réparation de) BASE
# ------------------------------------------------------------------ #
def _eval_query(db: List[Fact], query_atoms: List[Atom]) -> bool:
    """Renvoie True s'il existe une substitution qui rend la conjonction vraie."""
    pos_atoms   = [a for a in query_atoms if not a[0]]
    neg_atoms   = [a for a in query_atoms if a[0]]
    if not pos_atoms:
        # requête sans positif : vraie s'il n'y a aucun témoin pour les neg
        return all(_no_match(db, a, {}) for a in neg_atoms)

    result_envs = [{}]
    for neg, pred, pk_len, args in pos_atoms + neg_atoms:
        new_envs = []
        for env in result_envs:
            if neg:
                if _no_match(db, (neg, pred, pk_len, args), env):
                    new_envs.append(env)         # garde env si neg satisfaite
            else:
                for fact in (f for f in db if f[0] == pred):
                    new = _unify(args, fact[2], env)
                    if new is not None:
                        new_envs.append(new)
        result_envs = new_envs
        if not result_envs:
            return False                         # early‑fail
    return bool(result_envs)


# ------------------------------------------------------------------ #
#  UTILITAIRES : unification & abs. de match
# ------------------------------------------------------------------ #
def _is_var(tok: str) -> bool:
    return tok and tok[0].islower()

def _unify(pat: Tuple[str, ...], tup: Tuple[str, ...],
           env: Vars) -> Vars | None:
    """Tente de prolonger env pour pat = tup ; None si échec."""
    new_env = env.copy()
    for p, t in zip(pat, tup):
        if _is_var(p):
            if p in new_env and new_env[p] != t:
                return None
            new_env[p] = t
        elif p != t:
            return None
    return new_env

def _no_match(db: List[Fact], atom: Atom, env: Vars) -> bool:
    """True si *aucun* fait ne satisfait le littéral (négation réussit)."""
    _, pred, _, args = atom
    for _, _, tup in (f for f in db if f[0] == pred):
        if _unify(args, tup, env) is not None:
            return False
    return True
