# repairs.py  ────────────────────────────────────────────────────────────────
"""
Outils pour :
    • construire les *ensembles de conflit* (tuples qui partagent la même PK)
    • calculer le NOMBRE de réparations
    • parcourir paresseusement (generator) TOUTES les réparations

Interface principale
--------------------
>>> import repairs, parser_module as P
>>> parsed   = P.parse(raw_text)
>>> info     = repairs.prepare(parsed["database"])
>>> info["count"]            # nombre total de réparations (int ou ∞)
>>> next(repairs.enumerate_repairs(info))   # 1ʳᵉ réparation (list de tuples)
"""

from __future__ import annotations
from collections import defaultdict
from itertools import product
from math import prod, inf
from typing import Dict, List, Tuple, Iterable, Generator, Any

Fact   = Tuple[str, int, Tuple[str, ...]]     # (pred, pk_len, args)
Key    = Tuple[str, ...]                     # identifiant unique de la PK
Repair = List[Fact]


# --------------------------------------------------------------------------- #
#  ÉTAPE 1 – pré‑calcul (groupes de conflit)
# --------------------------------------------------------------------------- #
def prepare(database: List[Fact]) -> Dict[str, Any]:
    """
    :return: dict {
        "groups": {key: [fact,…]},              # toutes les PK
        "singles": [fact,…],                    # pas de conflit
        "count":   int | inf                    # ∏ |groups[key]|   (∞ si trop gros)
    }
    """
    by_key: Dict[Key, List[Fact]] = defaultdict(list)
    for pred, pk_len, args in database:
        key = (pred,) + args[:pk_len]           # clé = prédicat + PK
        by_key[key].append((pred, pk_len, args))

    singles   = [facts[0] for facts in by_key.values() if len(facts) == 1]
    conflicts = {k: v for k, v in by_key.items() if len(v) > 1}

    # calcul (borné) du nombre de réparations
    try:
        n_repairs = prod(len(v) for v in conflicts.values())
    except OverflowError:
        n_repairs = inf

    return {"groups": conflicts, "singles": singles, "count": n_repairs}


# --------------------------------------------------------------------------- #
#  ÉTAPE 2 – générateur paresseux de réparations
# --------------------------------------------------------------------------- #
def enumerate_repairs(info: Dict[str, Any]) -> Generator[Repair, None, None]:
    """
    Generator qui énumère *une* réparation à la fois
    (attention : peut être exponentiel).
    """
    groups   = list(info["groups"].values())     # list[list[fact]]
    singles  = info["singles"]

    if not groups:                               # base déjà cohérente
        yield singles
        return

    # produit cartésien : pour chaque groupe on choisit 1 tuple
    for choice in product(*groups):
        yield singles + list(choice)


# --------------------------------------------------------------------------- #
#  VERSION   « CERTAIN »  (arrêter dès qu’un doublon est vu)
# --------------------------------------------------------------------------- #
def is_certain(predicate, key_tuple, info: Dict[str, Any]) -> bool:
    """
    Renvoie True s’il N’EXISTE AUCUNE réparation
    dans laquelle le couple (predicate, key_tuple) est absent.
    Utile pour vérifier rapidement qu’un tuple est *certain*.
    """
    key_full = (predicate,) + tuple(key_tuple)
    if key_full in info["groups"] and len(info["groups"][key_full]) > 1:
        # plusieurs choix possibles pour cette PK  →  incertain
        return False
    # sinon le tuple est soit unique, soit absent de la DB
    return True
