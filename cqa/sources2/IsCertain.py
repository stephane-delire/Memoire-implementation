"""
--------------------------------------------------------------------------------
Algorithm 1 

Implémentation de l'algorithme "IsCertain" présent a la page 216.
Il prend en entrée une requête et une base de données. 

Si la requête est weakly-guarded, et son graphe d'attaque acyclique,
alors il renvoie True.

--------------------------------------------------------------------------------
"""

def is_all_key(q):
    """
    Vérifie si tous les atomes de q sont all-key.
    Un atome est all-key si toutes ses variables sont couvertes par la clé primaire.
    """
    for neg, pred, pk_len, args in q:
        pk_vars = set(args[:pk_len])
        all_vars = set(args)
        if not all_vars.issubset(pk_vars):
            return False
    return True

def valuation_satisfies(atom, db):
    """
    Vérifie s'il existe une instanciation (valuation) de l'atome dans la base db.
    """
    pred = atom[1]
    pk_len = atom[2]
    args = atom[3]
    
    if pred not in db:
        return False

    facts = db[pred]
    for fact in facts:
        if len(fact) != len(args):
            continue
        # On pourrait ici ajouter plus de contrôles de variables
        return True
    return False

def is_certain(q, db):
    """
    Implémente l'algorithme IsCertain(q, db) de l'article.
    """
    if not q:
        # Cas trivial : requête vide est certaine
        return True

    if is_all_key(q):
        # Si chaque atome est all-key
        for atom in q:
            if not valuation_satisfies(atom, db):
                return False
        return True

    # Choisir un atome non all-key et non-attaqué
    f = select_non_all_key_atom(q)

    # Cas où clé(f) ≠ ∅
    neg, pred, pk_len, args = f
    if pk_len > 0:
        # Il existe une valuation sur key(F) telle que IsCertain(θ(q), db)
        valuations = find_key_valuations(f, db)
        for theta in valuations:
            new_q = apply_valuation(q, theta)
            if not is_certain(new_q, db):
                return False
        return True
    else:
        # Cas clé vide
        if neg:
            # sous-cas : atome négatif
            new_q = [atom for atom in q if atom != f]
            return is_certain(new_q, db)
        else:
            # sous-cas : atome positif
            new_q = [atom for atom in q if atom != f]
            pred = f[1]
            args = f[3]
            new_facts = db.get(pred, [])

            for fact in new_facts:
                # Pour chaque fait R(ā) dans db
                # vérifier que θ(g) = b pour toutes les autres variables
                if not is_certain(new_q, db):
                    return False
            return True