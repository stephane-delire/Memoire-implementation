"""
--------------------------------------------------------------------------------
Algorithm 

Implémentation de l'algorithme "IsCertain" présent a la page 216.
Il prend en entrée une requête et une base de données. 

--------------------------------------------------------------------------------
"""
from .attack_graph import build_attack_graph

# -----------------------------------------------------------------------------
#  Helpers génériques

def is_variable(t):
    """
    Heuristique très simple : tout identifiant alphabétique en minuscules est
    considéré comme une variable (x, y, p, …).  Tout le reste (1, 'A', 'PARIS')
    est traité comme constante.
    """
    return isinstance(t, str) and t.isalpha() and t.islower()


def is_all_key_atom(atom):
    """
    Un atome est all-key si toutes ses variables apparaissent déjà dans la clé.
    atom = (neg, pred, pk_len, args)
    """
    _, _, pk_len, args = atom
    key_vars = set(a for a in args[:pk_len] if is_variable(a))
    for term in args:
        if is_variable(term) and term not in key_vars:
            return False
    return True


def is_all_key(query):
    return all(is_all_key_atom(a) for a in query)


def build_db_dict(database):
    """
    Convertit la liste parsée  [(pred, pk_len, args), …]  en  {pred: [fact, …]}.
    """
    db = {}
    for pred, _, args in database:
        db.setdefault(pred, []).append(tuple(args))
    return db


def unify_tuple(template, fact, bindings):
    """
    Essaie d’unifier `template` (tuple de termes) avec un `fact` concret sous
    l’environnement `bindings`.  Renvoie un nouveau dict (bindings étendus) ou
    None si échec.
    """
    new = dict(bindings)
    for t, c in zip(template, fact):
        if is_variable(t):
            if t in new and new[t] != c:
                return None
            new[t] = c
        elif t != c:
            return None
    return new


# -----------------------------------------------------------------------------
#  Évaluation d’une requête entièrement all-key (uniquement des pk)  
# (lignes 1–2 de l’algo)

def db_satisfies(query, db):
    pos = [a for a in query if not a[0]]
    neg = [a for a in query if a[0]]

    def backtrack(i, env):
        if i == len(pos):
            # Tous les positifs sont satisfaits ; vérifions les négatifs
            for _, pred, _, args in neg:
                for fact in db.get(pred, []):
                    if unify_tuple(args, fact, env) is not None:
                        return False
            return True

        _negflag, pred, _, args = pos[i]   # ←   changement ici
        for fact in db.get(pred, []):
            env2 = unify_tuple(args, fact, env)
            if env2 is not None and backtrack(i + 1, env2):
                return True
        return False

    return backtrack(0, {})


# -----------------------------------------------------------------------------
#  Sélection d’un atome non-all-key et unattacked

def select_unattacked_non_all_key_atom(query):
    g = build_attack_graph(query)
    indeg = {a: 0 for a in query}
    for src, outs in g.items():
        for tgt in outs:
            indeg[tgt] += 1

    for atom in query:
        if not is_all_key_atom(atom) and indeg[atom] == 0:
            return atom

    # secours : prend simplement le premier non-all-key
    # probleme, provoque une max recursion depth....
    # for atom in query:
    #     if not is_all_key_atom(atom):
    #         return atom
    return None   # devrait jamais arriver si la requête n’est pas vide


# -----------------------------------------------------------------------------
#  Sous-routines pour les valuations

def key_valuations(atom, db):
    _, pred, pk_len, args = atom
    key_positions = range(pk_len)
    vals = []

    for fact in db.get(pred, []):
        theta = {}
        ok = True
        for idx in key_positions:
            t, c = args[idx], fact[idx]
            if is_variable(t):
                if t in theta and theta[t] != c:
                    ok = False
                    break
                theta[t] = c
            elif t != c:
                ok = False
                break
        if ok:
            vals.append(theta)
    return vals


def apply_valuation(query, theta):
    new_q = []
    for neg, pred, pk_len, args in query:
        new_args = tuple(theta.get(a, a) for a in args)
        new_q.append((neg, pred, pk_len, new_args))
    return new_q


# -----------------------------------------------------------------------------
#  Générateur de relations fraîches E1, E2, …

_rel_counter = 0
def fresh_relation():
    global _rel_counter
    _rel_counter += 1
    return f"E{_rel_counter}"


# -----------------------------------------------------------------------------
#  Algo Principal  :  is_certain_core

def is_certain_core(query, database_or_dict, trace=None):
    """
    Implémentation de l'algorithme "IsCertain" pour une requête donnée.

    query      : [(neg, pred, pk_len, args), …]
    database   : soit la liste parsée par @database, soit déjà un dict {pred: […]}
    trace      : liste dans laquelle on stocke les étapes de l’algorithme
    Renvoie True ssi la requête est vraie dans toutes les repairs de la BD.
    """
    if trace is None:
        trace = []

    trace.append(f"== Appel is_certain_core sur requête : {query}")

    db = (database_or_dict if isinstance(database_or_dict, dict)
          else build_db_dict(database_or_dict))

    # (0-bis) Base déjà conforme
    all_keys_ok = all(len({fact[:pk_len] for fact in db.get(pred, [])}) == len(db.get(pred, []))
                     for pred, pk_len in {(a[1], a[2]) for a in query})
    if all_keys_ok:
        trace.append(" - Base déjà conforme aux clés primaires → évaluation directe")
        result = db_satisfies(query, db)
        trace.append(f" → Résultat FO direct : {result}")
        return result

    # 0) Requête vide
    if not query:
        trace.append(" - Requête vide → True")
        return True

    # 1) Tous les atomes sont all-key
    if is_all_key(query):
        trace.append(" - Tous les atomes sont all-key → évaluation FO directe")
        result = db_satisfies(query, db)
        trace.append(f" → Résultat FO : {result}")
        return result

    # 2) Sélection de F
    F = select_unattacked_non_all_key_atom(query)
    if F is None:
        trace.append(" - Aucun atome non-all-key unattacked trouvé → False (sécurité)")
        return False

    neg_F, pred_F, pk_F, args_F = F
    trace.append(f" - Atome choisi F : {F}")

    # -------------------------------------------------------------------------
    # Branche A : clé non vide
    if pk_F > 0:
        trace.append(" - Clé primaire de F non vide")
        for theta in key_valuations(F, db):
            q_theta = apply_valuation(query, theta)
            if q_theta == query:
                continue
            trace.append(f"   - Application de valuation {theta} → {q_theta}")
            if is_certain_core(q_theta, db, trace):
                trace.append("   → Une valuation a mené à True")
                return True
        trace.append("   → Aucune valuation n’a mené à True")
        return False

    # -------------------------------------------------------------------------
    # Branche B : clé vide
    trace.append(" - Clé primaire de F vide")
    const_pos = [i for i, t in enumerate(args_F) if not is_variable(t)]
    var_pos   = [i for i, t in enumerate(args_F) if is_variable(t)]

    relevant_facts = []
    for fact in db.get(pred_F, []):
        if all(fact[i] == args_F[i] for i in const_pos):
            relevant_facts.append(fact)

    trace.append(f" - Faits compatibles avec les constantes : {relevant_facts}")

    if not relevant_facts:
        trace.append(" → Aucun fait compatible → False")
        return False

    q_prime = [a for a in query if a is not F]

    # ------------------------------------------------------------------ F négatif
    if neg_F:
        trace.append(" - F est négatif")
        if not is_certain_core(q_prime, db, trace):
            trace.append("   → q' échoue → False")
            return False

        for fact in relevant_facts:
            b_bar = tuple(fact[i] for i in var_pos)
            fresh = fresh_relation()
            pk_len_E = len(b_bar)
            neg_E = (True, fresh, pk_len_E, b_bar)
            new_db = dict(db)
            new_db.setdefault(fresh, []).append(b_bar)
            trace.append(f"   - Ajout de ¬{fresh}{b_bar} et appel récursif")
            if not is_certain_core(q_prime + [neg_E], new_db, trace):
                trace.append("   → Un ajout mène à False")
                return False
        trace.append("   → Tous les ajouts ont mené à True")
        return True

    # ------------------------------------------------------------------ F positif
    else:
        trace.append(" - F est positif")
        y_vars = [args_F[i] for i in var_pos]

        for fact in relevant_facts:
            ok_candidate = True
            trace.append(f"   - Candidat : {fact}")
            for fact2 in relevant_facts:
                theta = {v: fact2[pos] for v, pos in zip(y_vars, var_pos)}
                q_theta = apply_valuation(q_prime, theta)
                if q_theta == q_prime:
                    ok_candidate = False
                    trace.append("     - Theta inchangé → rejet")
                    break
                if not is_certain_core(q_theta, db, trace):
                    ok_candidate = False
                    trace.append(f"     - Theta {theta} mène à False → rejet")
                    break
            if ok_candidate:
                trace.append("   → Candidat accepté")
                return True
        trace.append("   → Aucun candidat accepté → False")
        return False