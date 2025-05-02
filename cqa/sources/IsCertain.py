"""
--------------------------------------------------------------------------------
Algorithm 1 

Implémentation de l'algorithme "IsCertain" présent a la page 216.
Il prend en entrée une requête et une base de données. 

Si la requête est weakly-guarded, et son graphe d'attaque acyclique,
alors il renvoie True...

--------------------------------------------------------------------------------
"""
from .attack_graph import build_attack_graph

###############################################################################
#  Helpers génériques
###############################################################################

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


###############################################################################
#  Évaluation d’une requête entièrement all-key  (lignes 1–2 de l’algo)
###############################################################################

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


###############################################################################
#  Sélection d’un atome non-all-key et unattacked
###############################################################################

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


###############################################################################
#  Sous-routines pour les valuations
###############################################################################

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


###############################################################################
#  Générateur de relations fraîches E1, E2, …
###############################################################################

_rel_counter = 0
def fresh_relation():
    global _rel_counter
    _rel_counter += 1
    return f"E{_rel_counter}"


###############################################################################
#  ALGORITHME PRINCIPAL  :  is_certain_core
###############################################################################

def is_certain_core(query, database_or_dict):
    """
    query      : [(neg, pred, pk_len, args), …]   – exactement ton format
    database   : soit la liste parsée par @database, soit déjà un dict {pred: […]}
    Renvoie True ssi la requête est vraie dans *tous* les repairs de la BD.
    """

    db = (database_or_dict if isinstance(database_or_dict, dict)
          else build_db_dict(database_or_dict))
    # (0-bis) La base est déja conforme à toutes les clés
    # ceci peut empecher l'erreur de "max recursion depth" plus loin
    if all(len({fact[:pk_len] for fact in db.get(pred, [])}) == len(db.get(pred, []))
        for pred, pk_len in {(a[1], a[2]) for a in query}):
        return db_satisfies(query, db)
    
    # 0) Requête vide
    if not query:
        return True

    # 1) Tous les atomes sont all-key  → simple FO-évaluation
    if is_all_key(query):
        return db_satisfies(query, db)

    # 2) Choix de F  (non-all-key, unattacked)
    F = select_unattacked_non_all_key_atom(query)
    if F is None:
        return False    # sécurité

    neg_F, pred_F, pk_F, args_F = F

    # -------------------------------------------------------------------------
    #  BRANCHE  A  :  key(F) ≠ ∅
    # -------------------------------------------------------------------------
    if pk_F > 0:
        for theta in key_valuations(F, db):
            q_theta = apply_valuation(query, theta)
            if is_certain_core(q_theta, db):           # EXISTENTIEL
                return True
        return False

    # -------------------------------------------------------------------------
    #  key(F) = ∅      ⇒  F = R(ā, ȳ)  avec vars(ā)=∅
    # -------------------------------------------------------------------------
    # Séparation constants / variables dans F
    const_pos = [i for i, t in enumerate(args_F) if not is_variable(t)]
    var_pos   = [i for i, t in enumerate(args_F) if is_variable(t)]

    # Tous les faits R(ā, b̄) compatibles avec ā
    relevant_facts = []
    for fact in db.get(pred_F, []):
        if all(fact[i] == args_F[i] for i in const_pos):
            relevant_facts.append(fact)

    if not relevant_facts:
        return False     # Aucune instanciation possible

    q_prime = [a for a in query if a is not F]

    # ------------------------------------------------------------------ F négatif
    if neg_F:
        # (i) IsCertain(q', db)
        if not is_certain_core(q_prime, db):
            return False

        # (ii) ∀ b̄ : IsCertain(q' ∪ {¬E(b̄)}, db ∪ {E(b̄)})
        for fact in relevant_facts:
            b_bar = tuple(fact[i] for i in var_pos)
            fresh = fresh_relation()
            pk_len_E = len(b_bar)          # E est all-key
            neg_E = (True,  fresh, pk_len_E, b_bar)
            new_db = dict(db)              # shallow copy
            new_db.setdefault(fresh, []).append(b_bar)
            if not is_certain_core(q_prime + [neg_E], new_db):
                return False
        return True

    # ------------------------------------------------------------------ F positif
    else:
        y_vars = [args_F[i] for i in var_pos]

        for fact in relevant_facts:        # EXISTENTIEL sur b̄
            # On teste si ce candidat marche pour *tous* les b̄'
            ok_candidate = True
            for fact2 in relevant_facts:   # UNIVERSALITÉ sur b̄'
                theta = {}
                for v, pos in zip(y_vars, var_pos):
                    theta[v] = fact2[pos]
                q_theta = apply_valuation(q_prime, theta)
                if not is_certain_core(q_theta, db):
                    ok_candidate = False
                    break
            if ok_candidate:
                return True
        return False