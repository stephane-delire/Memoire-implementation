# -----------------------------------------------------------------------------
#  rewrite.py   – consistent first‑order rewriting  (Lemme 6.1)

# Redo du module en entier... 

from itertools import count
from .IsCertain import is_variable, is_all_key_atom, select_unattacked_non_all_key_atom


_var_counter = count(1)
def _freshen_vars(vars_):
    # t -> t1, p -> p2, etc.
    return [f"{v}{next(_var_counter)}" for v in vars_]

def _non_key_var_positions(atom):
    neg, pred, pk_len, args = atom
    return [i for i in range(pk_len, len(args)) if is_variable(args[i])]

def _distinct_non_key_var_map(atom):
    """Retourne (mapping, positions) pour les variables hors-clé.
       mapping: { var -> fresh_var }
       positions: { var -> [pos1, pos2, ...] } (toutes les occurrences)
    """
    neg, pred, pk_len, args = atom
    mapping = {}
    positions = {}
    for j in range(pk_len, len(args)):
        a = args[j]
        if is_variable(a):
            if a not in mapping:
                mapping[a] = f"{a}{next(_var_counter)}"  # un seul frais par variable
            positions.setdefault(a, []).append(j)
    return mapping, positions

# -----------------------------------------------------------------------------
#  Pretty-printing FO
def atom_to_str(atom):
    neg, pred, pk, args = atom
    tup = ", ".join(str(a) for a in args)
    return f"¬{pred}({tup})" if neg else f"{pred}({tup})"

def conj(atoms):
    return " ⊓ ".join(atom_to_str(a) for a in atoms) or "⊤"

def disj(forms):
    return " ⊔ ".join(forms)

def forall(vars_, phi):
    return f"∀{', '.join(vars_)} ( {phi} )" if vars_ else phi

def exists(vars_, phi):
    return f"∃{', '.join(vars_)} ( {phi} )" if vars_ else phi

def fo_to_latex(fo_string):
    return (
        fo_string
        .replace("∀", r"\forall ")
        .replace("∃", r"\exists ")
        .replace("⊓", r"\land ")
        .replace("⊔", r"\lor ")
        .replace("¬", r"\lnot ")
        .replace("→", r"\rightarrow ")
        .replace(",", ", ")
    )

# -----------------------------------------------------------------------------
#  nouveaux symboles frais  (E1, E2, …)  pour le cas pk vide
_fresh = count(1)
def fresh_rel():
    return f"E{next(_fresh)}"

# -----------------------------------------------------------------------------
#  utilitaires variables
def _key_vars(atom):
    neg, pred, pk_len, args = atom
    return [args[i] for i in range(pk_len) if is_variable(args[i])]

def _non_key_vars(atom):
    neg, pred, pk_len, args = atom
    return [args[i] for i in range(pk_len, len(args)) if is_variable(args[i])]

def _free_vars_atoms(atoms):
    vs = []
    seen = set()
    for (_, _, _, args) in atoms:
        for a in args:
            if is_variable(a) and a not in seen:
                seen.add(a); vs.append(a)
    return vs

def _format_positive(pred, args):
    return f"{pred}({', '.join(args)})"

# nonkey helpers (post memoire)
def _nonkey_positions(F):
    """Renvoie les indices de positions hors-clé, en supposant que
    les positions de clé sont les 'pk_len' premières."""
    neg, pred, pk_len, args = F
    n = len(args)
    return [i for i in range(n) if i >= pk_len]

# si tu n’as pas déjà un fresh_var():
def fresh_var(prefix="z"):
    global _var_counter
    try:
        _var_counter
    except NameError:
        from itertools import count
        _var_counter = count(1)
    return f"{prefix}{next(_var_counter)}"

def _fresh_nonkey_per_position(F):
    """Une variable fraîche par **position hors-clé** (inclut constantes/répétitions dans les égalités)."""
    neg, pred, pk_len, args = F
    nonkey_pos = _nonkey_positions(F)
    zvars = [fresh_var() for _ in nonkey_pos]

    # antécédent: R(key, z...) en remplaçant chaque position hors-clé par sa fraîche
    ant_args = list(args)
    for i, zi in zip(nonkey_pos, zvars):
        ant_args[i] = zi

    # égalités positionnelles: zi = args[i] (constantes ou variables, répétitions incluses)
    eq_atoms = [f"{zi} = {args[i]}" for i, zi in zip(nonkey_pos, zvars)]
    return zvars, ant_args, eq_atoms

def _vars_in_atoms(atoms):
    """Variables (strings) apparaissant dans une liste d’atomes."""
    vs = set()
    for (neg, pred, pk_len, args) in atoms:
        for a in args:
            if is_variable(a):
                vs.add(a)
    return sorted(vs)

# -----------------------------------------------------------------------------
#  réécriture principale (récursive)
def rewrite(query, trace=None):
    """
    Retourne une chaîne FO. Conforme aux points suivants:
      - sélection d’un atome non-all-key unattacked,
      - cas pk>0 : négatif = ∀ (vars hors-clé) (¬pred ∨ inner),
                    positif = cas spécial clé simple avec garde ; sinon ∃key(F)(F ∧ inner)
      - cas pk=0 : usage d’un symbole frais E pour le négatif ; garde universelle,
      - cas de base all-key : conjonction fermée existentiellement sur les variables libres.
    """
    if trace is None:
        trace = []

    trace.append(f"== Appel rewrite sur requête : {query}")

    # Cas base : tous all-key -> on ferme existentiellement les variables libres
    if all(is_all_key_atom(a) for a in query):
        base = conj(query)
        trace.append(" - Cas de base : all-key → conjonction brute")
        trace.append(f"   → {base}")
        return base

    # Sélection d’un atome non-all-key et unattacked (suivant l’algo)
    F = select_unattacked_non_all_key_atom(query, trace=trace)
    if F is None:
        # sécurité : si rien de sélectionnable, on renvoie la conjonction fermée existentiellement
        base = conj(query)
        trace.append(" - Aucun atome non-all-key unattacked → conjonction brute")
        trace.append(f"   → {base}")
        return base

    trace.append(f" - Atome choisi pour élimination : {F}")

    neg, pred, pk_len, args = F
    key_vars = _key_vars(F)
    non_key_vars = _non_key_vars(F)
    rest_query = [a for a in query if a is not F]

    # -----------------------------------------------------------
    # A) Clé non vide
    if pk_len > 0:
        trace.append(f" - Clé non vide (pk_len = {pk_len}) → branche A")
        inner = rewrite(rest_query, trace)

        if not neg:
            trace.append(" - F est positif")

            # 1) formulation de l'intérieur
            inner = rewrite(rest_query, trace)

            # 2) hors-clé : distincts + copies fraîches
            mapping, positions = _distinct_non_key_var_map(F)
            y = list(mapping.keys())        # variables hors-clé originales
            yprime = list(mapping.values()) # leurs copies fraîches (∀)

            # 3) atome-témoin exact (avec constantes hors-clé intactes)
            block_atom = _format_positive(pred, list(args))

            # 4) atome-garde : on remplace chacune des var hors-clé par sa copie fraîche partout
            guard_args = list(args)
            for v, newv in mapping.items():
                for j in positions[v]:
                    guard_args[j] = newv
            block_guard = _format_positive(pred, guard_args)

            # 5) garde universelle + témoin existentiel
            #    (si y est vide, exists([], ...) et forall([], ...) tombent à l'intérieur pur)
            block_cond = forall(yprime, f"{block_guard} → {inner}")
            result = exists(y, f"{block_atom} ⊓ {block_cond}")
            trace.append(f"   - Clé non vide (garde ∀ sur hors-clé, témoin ∃) → {result}")
            return result

        # Branche else, pré mémoire
        # else:
        #     trace.append(" - F est négatif")
        #     mapping, positions = _distinct_non_key_var_map(F)
        #     uvars = list(mapping.values())  # quantifier une fois par var distincte
        #     ant_args = list(args)
        #     for v, newv in mapping.items():
        #         for j in positions[v]:
        #             ant_args[j] = newv
        #     antecedent = _format_positive(pred, ant_args)
        #     result = forall(uvars, f"{antecedent} → {inner}")   # équiv. à (antecedent → inner)
        #     trace.append(f"   - Négatif pk>0 (∀ hors-clé, frais par variable) → {result}")
        #     return result
        # Branche else, post mémoire...
        else:
            trace.append(" - F est négatif")

            # 1) fraiches par position + antécédent + égalités
            zvars, ant_args, eq_atoms = _fresh_nonkey_per_position(F)
            antecedent = _format_positive(pred, ant_args)

            # 2) réécriture du reste
            inner = rewrite(rest_query, trace)

            # 3) négation de la conjonction d’égalités (si pas d’hors-clé → ⊤)
            eq_conj = " ⊓ ".join(eq_atoms) if eq_atoms else "⊤"
            guarded = f"{inner} ⊓ ¬({eq_conj})"

            # 4) ∃ **à l’intérieur** (témoins pouvant dépendre de z)
            witnesses = _vars_in_atoms(rest_query)   # simple et robuste
            inner_exist = exists(witnesses, guarded) # exists([], φ) doit rendre φ inchangé

            # 5) >>> ICI LA DIFFÉRENCE IMPORTANTE <<<
            guard_clause = forall(zvars, f"{antecedent} → {inner_exist}")
            result = f"{inner} ⊓ {guard_clause}"   # on conserve inner AU NIVEAU COURANT
            trace.append("   - Négatif pk>0 → inner ∧ ∀(ant → ∃(inner ∧ ¬(∧=)))")

            return result

    # -----------------------------------------------------------
    # B) Clé vide
    trace.append(" - Clé vide → branche B")
    var_part = [t for t in args if is_variable(t)]
    fresh_E = fresh_rel()
    inner = rewrite(rest_query, trace)

    if neg:
        trace.append(" - F est négatif")
        # ajoute not E(var_part) dans la requête résiduelle
        inner_negE = rewrite(rest_query + [(True, fresh_E, len(var_part), tuple(var_part))], trace)
        guarded = forall(var_part, f"{_format_positive(pred, list(args))} → {inner_negE}")
        result = f"{inner} ⊓ {guarded}"
        trace.append(f"   - Négatif pk=0 avec symbole frais → {result}")
        return result
    else:
        trace.append(" - F est positif")
        theta_inner = exists(var_part, inner)
        guarded = forall(var_part, f"{_format_positive(pred, list(args))} → {theta_inner}")
        result = exists(var_part, f"{_format_positive(pred, list(args))} ⊓ {guarded}")
        trace.append(f"   - Positif pk=0 → {result}")
        return result

def rewrite_closed(query, trace=None):
    """
    Ferme la formule FO par des ∃ sur les variables de la requête d'origine.
    """
    global _var_counter, _fresh
    _var_counter = count(1)   # reset pour les variables fraîches t1, t2, …
    _fresh = count(1)         # reset pour les prédicats frais E1, E2, …
    if trace is None:
        trace = []

    trace.append("[rewrite_closed] called")

    # 1) Formule intermédiaire (peut contenir des ∀ internes)
    fo = rewrite(query, trace)
    trace.append(f"[rewrite_closed] after rewrite => {fo}")

    # 2) Variables de la requête d’origine à fermer
    base_vars, seen = [], set()
    for (_, _, _, args) in query:
        for a in args:
            if is_variable(a) and a not in seen:
                seen.add(a)
                base_vars.append(a)
    trace.append(f"[rewrite_closed] base_vars (to existentially close) => {base_vars}")

    # 3) Fermeture existentielle en tête
    closed = exists(base_vars, fo)
    trace.append(f"[rewrite_closed] final (closed) => {closed}")
    return closed