"""
-------------------------------------------------------------------------------
ngfo.py

Methodes pour déterminer si une requête est en NGFO, ou weakly-guarded.

Guarded Negation First Order : 
    - La négation complete d'un atome doit être gardée par un atome positif.

Weakly-guarded  : 
    - Chaque paire de variables dans un atome négatif doit être gardée par un atome positif.
    Ce n'est pas nécessaire que toutes les variables soient gardées ensemble,
    il suffit que chaque paire de variables soit quelque part gardée.


Lives(p,t)        ← positif
not Born(p,t)     ← négatif : variables (p,t) déjà présentes ensemble dans Lives  ✔ WG
not Likes(t,p)    ← (t,p) apparaissent aussi dans Lives                           ✔ WG

-------------------------------------------------------------------------------
"""

from itertools import combinations


def is_guarded(query):
    """
    Extracte les atomes positifs et négatifs d'une requête.
    Vérifie si la requête est en NGFO, ou weakly-guarded.
    Renvoie False si la requête n'est pas en NGFO, ou weakly-guarded.
    
    Exemple de requête :
    [(False, 'Likes', 2, ('p', 't')), (True, 'Lives', 1, ('p', 't')), (True, 'Mayor', 1, ('t', 'p'))]

    :param query: La requête à vérifier (parsée).
    :return: True si la requête est en NGFO, ou weakly-guarded, False sinon.
    
    """
    # Séparation des atomes positifs et négatifs
    q_plus = [a for a in query if not a[0]] # Atome positif
    q_minus = [a for a in query if a[0]] # Atome négatif

    # sjf
    if not _is_self_join_free(q_plus):
        return False, "not sjf"

    # NGFO
    if _is_ngfo(q_plus, q_minus):
        return True, "NGFO"

    # Weakly-guarded
    elif _is_weakly_guarded(q_plus, q_minus):
        return True, "WG"
    
    # La requête n'est pas en NGFO, ni weakly-guarded
    else:
        return False, None

# =============================================================================
# ------------------------------------------------------------------------ NGFO
def _is_ngfo(q_plus, q_minus):
    """
    Vérifie si la requête est en NGFO.
    En NGFO, peu importe l’ordre des variables, ce qui compte est que toutes 
    les variables de la formule négative soient groupées ensemble dans un seul 
    atome positif.
    
    :param q_plus: Liste des atomes positifs.
    :param q_minus: Liste des atomes négatifs.
    :return: True si la requête est en NGFO, False sinon.
    
    """
    args_plus = [set(a[3]) for a in q_plus]
    args_minus = [set(a[3]) for a in q_minus]

    # Vérifie si chaque atome négatif est gardé par un atome positif
    for neg in args_minus:
        if not any(neg <= pos for pos in args_plus):
            return False
    return True

# =============================================================================
# -------------------------------------------------------------- Weakly-guarded
def _is_weakly_guarded(q_plus, q_minus):
    """
    Vérifie si la requête est weakly-guarded.
    Pour chaque atome négatif, chaque paire de variables doit être couverte 
    ensemble dans un même atome positif.

    :param q_plus: Liste des atomes positifs.
    :param q_minus: Liste des atomes négatifs.
    :return: True si la requête est weakly-guarded, False sinon.
    """
    args_plus = [set(a[3]) for a in q_plus]
    args_minus = [set(a[3]) for a in q_minus]

    for neg in args_minus:
        vars_in_neg = [v for v in neg if v.islower()]
        # Si moins de 2 variables, pas de paires à vérifier... --> WG
        if len(vars_in_neg) < 2:
            return True

        for x, y in combinations(vars_in_neg, 2):  # Toutes les paires possibles dans le négatif
            pair_guarded = any({x, y}.issubset(pos) for pos in args_plus)
            if not pair_guarded:
                return False
    return True

# =============================================================================
# ------------------------------------------------------------------------- SJF
def _is_self_join_free(q_plus):
    """
    Vérifie si la requête est self-join free.
    Une requête est self-join free si elle ne contient pas de jointures sur 
    elle-même. (aucun prédicat positif n'apparait plus d'une fois).

    :param q_plus: Liste des atomes positifs.
    :return: True si la requête est self-join free, False sinon.
    """
    seen = set()
    for atom in q_plus:
        pred = atom[1]
        if pred in seen:
            return False
        seen.add(pred)
    return True
# =============================================================================