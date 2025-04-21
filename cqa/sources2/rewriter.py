"""
--------------------------------------------------------------------------------
Rewritter

Permet de reformuler la requete en un arbre de décision F-O
pour la requête donnée.

Voir le théorème 8,
Voir algorithme 1 du papier Koutris & Wijsen (section 6.3).

    - Si la négation est weakly-guarded et que le graphe d'attaque est acyclique,
        alors la requête est réécrivable en F-O.
    - Sinon, aucune garantie, on renvoie None.

--------------------------------------------------------------------------------
"""

def rewrite(data):
    """
    :param data: sortie du parseur {"database": …, "query": [Atom, …]}
    :return: arbre FO (dict) si F-O rewritable, sinon None
    """
    q_plus  = [a for a in data["query"] if not a[0]]
    q_minus = [a for a in data["query"] if     a[0]]

    