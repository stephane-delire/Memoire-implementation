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
    q_plus = [a for a in data["query"] if not a[0]] # Atome positif
    q_minus = [a for a in data["query"] if a[0]] # Atome negatif

    # weakly-guarded negation
    if not _is_weakly_guarded(data["query"]):
        print("La requête n'est pas weakly-guarded")
        return None
    print("La requête est weakly-guarded")
    # La requête est weakly-guarded

    # # attack graph
    # att_graph = _build_attack_graph(data["query"])
    # print(att_graph)

    # # CYCLE ???

    # # Build rewriting
    # rewriting = _build_rewriting(data["query"], att_graph)
    # print(rewriting)


# ==============================================================================
# --------------------------------------------------------------- Weakly-guarded
def _is_weakly_guarded(query):
    """
    Une négation «dangereuse» peut comparer librement deux variables qui ne 
    co-existent jamais dans un même atome positif; cela permet de «relier» des 
    composantes normalement indépendantes et rend le problème plus dur.
    
    Lives(p,t)        ← positif
    not Born(p,t)     ← négatif : variables (p,t) déjà présentes ensemble dans Lives  ✔ WG
    not Likes(t,p)    ← (t,p) apparaissent aussi dans Lives                           ✔ WG


    !!! Plus utilisé ! Voir le fichier NGFO

    """
    # Séparer atomes positifs et négatifs
    positives = [a for a in query if not a[0]]
    negatives = [a for a in query if a[0]]

    # Liste des ensembles de variables de chaque atome positif
    pos_varsets = [set(a[3]) for a in positives]

    # Pour chaque atome négatif
    for neg in negatives:
        vars_neg = neg[3]
        # Pour chaque paire (x, y) de variables dans l'atome négatif
        for i in range(len(vars_neg)):
            for j in range(i + 1, len(vars_neg)):
                x, y = vars_neg[i], vars_neg[j]
                # Vérifie si une des varsets positives contient à la fois x et y
                if not any({x, y}.issubset(pos_vars) for pos_vars in pos_varsets):
                    return False
    return True

# ==============================================================================
# ----------------------------------------------------------------- Attack graph
def _build_attack_graph(atoms):
    """
    Construit un graphe d'attaque :
    Chaque atome peut attaquer un autre si une de ses clés permet de découvrir une clé de l'autre.
    """

    # Récupère les dépendances fonctionnelles des atomes positifs (clé -> tous les attributs)
    fds = []
    for is_negated, _, key_len, args in atoms:
        if is_negated:
            continue
        key = set(args[:key_len])
        fds.append((key, set(args)))

    def closure(var):
        """Retourne tous les attributs atteignables depuis une variable via les FD."""
        reachable = {var}
        changed = True
        while changed:
            changed = False
            for left, right in fds:
                if left <= reachable and not right <= reachable:
                    reachable |= right
                    changed = True
        return reachable

    # Initialisation du graphe (index de l'atome -> set des index attaqués)
    graph = {i: set() for i in range(len(atoms))}

    for i, (_, _, key_len_i, args_i) in enumerate(atoms):
        key_i = set(args_i[:key_len_i])

        for var in key_i:
            reachable = closure(var)

            for j, (_, _, key_len_j, args_j) in enumerate(atoms):
                if i == j:
                    continue

                key_j = set(args_j[:key_len_j])
                for key_attr in key_j:
                    if key_attr not in key_i and key_attr in reachable:
                        graph[i].add(j)
                        break  # un seul arc suffit

    return graph

# ==============================================================================
# ---------------------------------------------------------------- build rewrite
def _build_rewriting(query, attack_graph):
    """
    Construit la réécriture logique de la requête en respectant le théorème 8 :
    - Si tous les atomes positifs sont 'all-key', on les garde tels quels.
    - Sinon, on sélectionne un pivot non all-key non attaqué et on structure :
        pivot ∧ not_exists_dup ∧ not_exists(...)
    """

    # ─── Étape 1 : Chercher un atome pivot (positif, non all-key, non attaqué)
    pivot_idx = None
    for idx, (neg, _, pk_len, args) in enumerate(query):
        if neg:
            continue
        if pk_len != len(args):  # donc pas all-key
            is_attacked = any(idx in attacked for attacked in attack_graph.values())
            if not is_attacked:
                pivot_idx = idx
                break

    # ─── Cas simple : tous les positifs sont all-key → pas besoin de réécriture
    if pivot_idx is None:
        return {
            'op': 'and',
            'children': [_atom_node(atom) for atom in query]
        }

    # ─── Étape 2 : Construire l’arbre de réécriture autour du pivot
    pivot_atom = query[pivot_idx]
    _, pred, pk_len, args = pivot_atom

    pk_vars = args[:pk_len]
    nonpk_vars = args[pk_len:]

    pivot_node = _atom_node(pivot_atom)

    # Clause anti-doublon : exclure les autres tuples avec même clé mais valeurs différentes
    dup_filter_node = {
        'op': 'not_exists_dup',
        'pred': pred,
        'pk_vars': pk_vars,
        'nvars': nonpk_vars,
        'pk_len': pk_len
    }

    # ─── Étape 3 : Transformer chaque atome négatif en not_exists corrélé
    neg_nodes = []
    for atom in query:
        if not atom[0]:
            continue
        _, neg_pred, neg_pk_len, neg_args = atom
        eq_conditions = [
            (neg_args[i], pk_vars[i]) for i in range(neg_pk_len)
        ]
        neg_nodes.append({
            'op': 'not_exists',
            'pred': neg_pred,
            'eq': eq_conditions
        })

    return {
        'op': 'and',
        'children': [pivot_node, dup_filter_node] + neg_nodes
    }
def _atom_node(atom):
    return {
        'op': 'atom',
        'pred': atom[1],
        'args': atom[3]
    }
# ------------------------------------------------------------------------------