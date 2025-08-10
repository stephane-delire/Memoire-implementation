# -----------------------------------------------------------------------------
#  rewrite.py   – consistent first‑order rewriting  (Lemme 6.1)

# from itertools import count
# from .attack_graph import build_attack_graph
# from .IsCertain import is_variable, is_all_key_atom, select_unattacked_non_all_key_atom

# # -----------------------------------------------------------------------------
# #  outils de pretty‑printing
# def atom_to_str(atom):
#     neg, pred, pk, args = atom
#     tup = ", ".join(str(a) for a in args)
#     return f"¬{pred}({tup})" if neg else f"{pred}({tup})"

# def conj(atoms):
#     return " ⊓ ".join(atom_to_str(a) for a in atoms) or "⊤"

# def disj(forms):
#     return " ⊔ ".join(forms)

# def forall(vars_, phi):
#     return f"∀{', '.join(vars_)} ( {phi} )" if vars_ else phi

# def exists(vars_, phi):
#     return f"∃{', '.join(vars_)} ( {phi} )" if vars_ else phi

# def fo_to_latex(fo_string):
#     return (
#         fo_string
#         .replace("∀", r"\forall ")
#         .replace("∃", r"\exists ")
#         .replace("⊓", r"\land ")
#         .replace("⊔", r"\lor ")
#         .replace("¬", r"\lnot ")
#         .replace("→", r"\rightarrow ")
#         .replace(",", ", ")
#     )

# # -----------------------------------------------------------------------------
# #  générateur de nouveaux symboles  (E1, E2, …)  pour les clés vides
# _fresh = count(1)
# def fresh_rel():
#     return f"E{next(_fresh)}"

# # -----------------------------------------------------------------------------

# #  réécriture principale   (Algorithme 3 implicite dans la preuve)
# # Implémentation du trace
# def rewrite(query, trace=None):
#     if trace is None:
#         trace = []

#     trace.append(f"== Appel rewrite sur requête : {query}")

#     # Cas base : tous les atomes sont all-key
#     if all(is_all_key_atom(a) for a in query):
#         trace.append(" - Cas de base : tous les atomes sont all-key → réécriture directe (conjonction)")
#         return conj(query)

#     # Sélection d’un atome non all-key unattacked
#     F = select_unattacked_non_all_key_atom(query, trace=None)
#     if F is None:
#         trace.append(" - Aucun atome non-all-key unattacked → conjonction directe")
#         return conj(query)

#     trace.append(f" - Atome choisi pour élimination : {F}")

#     neg, pred, pk_len, args = F
#     key_vars = [args[i] for i in range(pk_len) if is_variable(args[i])]
#     rest_query = [a for a in query if a is not F]

#     # -----------------------------------------------------------
#     # A) Cas où la clé de F est non vide
#     if pk_len > 0:
#         trace.append(f" - Clé non vide (pk_len = {pk_len}) → branche A")

#         inner = rewrite(rest_query, trace)

#         if not neg:
#             trace.append(" - Atome F est positif")

#             if len(key_vars) == 1:
#                 x = key_vars[0]
#                 y = [a for i, a in enumerate(args) if i >= pk_len and is_variable(a)]
#                 yprime = [f"{v}′" for v in y]
#                 block_atom = f"{pred}({x}, {', '.join(y)})"
#                 block_guard = f"{pred}({x}, {', '.join(yprime)})"
#                 block_cond = forall(yprime, f"{block_guard} → {inner}")
#                 result = exists(y, f"{block_atom} ⊓ {block_cond}")
#                 trace.append(f"   - Cas spécial : clé simple → {result}")
#                 return result
#             else:
#                 result = exists(key_vars, f"{atom_to_str(F)} ⊓ {inner}")
#                 trace.append(f"   - Clé multiple → {result}")
#                 return result
#         else:
#             trace.append(" - Atome F est négatif")
#             antecedent = atom_to_str(F)[1:]  # retire le ¬
#             result = forall(key_vars, f"¬{antecedent} ⊔ {inner}")
#             trace.append(f"   - Réécriture négative : {result}")
#             return result

#     # -----------------------------------------------------------
#     # B) Cas où la clé est vide
#     trace.append(" - Clé vide → branche B")
#     const_part = [t for t in args if not is_variable(t)]
#     var_part = [t for t in args if is_variable(t)]
#     fresh_E = fresh_rel()

#     inner = rewrite(rest_query, trace)

#     if neg:
#         trace.append(" - Atome F est négatif")
#         inner_negE = rewrite(rest_query + [(True, fresh_E, len(var_part), tuple(var_part))], trace)
#         guarded = forall(var_part, f"{pred}({', '.join(args)}) → {inner_negE}")
#         result = f"{inner} ⊓ {guarded}"
#         trace.append(f"   - Réécriture négative avec fresh : {result}")
#         return result
#     else:
#         trace.append(" - Atome F est positif")
#         theta_inner = exists(var_part, inner)
#         guarded = forall(var_part, f"{pred}({', '.join(args)}) → {theta_inner}")
#         result = exists(var_part, f"{pred}({', '.join(args)}) ⊓ {guarded}")
#         trace.append(f"   - Réécriture positive : {result}")
#         return result


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
            if len(key_vars) == 1:
                # clé simple : garder TOUTES les positions hors-clé (constantes incluses)
                x = key_vars[0]
                tail_args = list(args[pk_len:])                      # mélange vars/constantes
                var_pos   = [i for i, a in enumerate(tail_args) if is_variable(a)]
                y         = [tail_args[i] for i in var_pos]          # seules les variables
                yprime    = [f"{v}′" for v in y]                     # variables fraîches

                # atome pour le témoin (constantes intactes)
                block_atom = _format_positive(pred, [x] + tail_args)

                # garde universelle : on remplace seulement les variables par leurs copies y′
                tail_prime = tail_args[:]
                for i, v in zip(var_pos, yprime):
                    tail_prime[i] = v
                block_guard = _format_positive(pred, [x] + tail_prime)

                block_cond = forall(yprime, f"{block_guard} → {inner}")
                result = exists(y, f"{block_atom} ⊓ {block_cond}")
                trace.append(f"   - Clé simple → {result}")
                return result
            else:
                # clé multiple : on quantifie les variables de clé (variables seulement) et on conjonctionne
                result = exists(key_vars, f"{atom_to_str(F)} ⊓ {inner}")
                trace.append(f"   - Clé multiple → {result}")
                return result

        else:
            trace.append(" - F est négatif")
            # universaliser seulement les variables hors-clé, avec nouveaux noms
            idxs = _non_key_var_positions(F)
            uvars = _freshen_vars(non_key_vars)  # ex: ['t1']
            ant_args = list(args)
            for j, newv in zip(idxs, uvars):
                ant_args[j] = newv
            antecedent = _format_positive(pred, ant_args)
            result = forall(uvars, f"¬{antecedent} ⊔ {inner}")
            trace.append(f"   - Négatif pk>0 (∀ hors-clé, frais) → {result}")
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
    Ferme la formule FO par des ∃ sur les variables de la requête d'origine
    (utile pour éviter des variables libres comme p dans ¬Lives(p,t)).
    """
    print("rewrite_closed called")
    fo = rewrite(query, trace)
    # variables de la requête initiale
    base_vars = []
    seen = set()
    for (_, _, _, args) in query:
        for a in args:
            if is_variable(a) and a not in seen:
                seen.add(a); base_vars.append(a)
    return exists(base_vars, fo)