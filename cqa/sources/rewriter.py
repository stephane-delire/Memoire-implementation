# # -----------------------------------------------------------------------------
# #  rewrite.py   – consistent first‑order rewriting  (Lemme 6.1)

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
#     """
#     Convertit une chaîne de caractères FO en une chaîne LaTeX.
#     Utilise des substitutions simples pour les symboles logiques.
#     """
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
# def rewrite(query):
#     """
#     Renvoie une chaîne FO équivalente à CERTAINTY(q), supposant :
#       – q self-join free, négation weakly-guarded ;
#       – attack-graph(q) acyclique.
#     """
#     # 1.  cas de base : tout est all‑key  →  simple conjonction
#     if all(is_all_key_atom(a) for a in query):
#         return conj(query)

#     # 2.  choix de F  (unattacked si possible, sinon premier non‑all‑key)
#     F = select_unattacked_non_all_key_atom(query)
#     if F is None:                       # requête vide – ne devrait pas arriver
#         return conj(query)

#     neg, pred, pk_len, args = F
#     key_vars   = [args[i] for i in range(pk_len) if is_variable(args[i])]
#     rest_query = [a for a in query if a is not F]

#     # ------------------------------------------------------------------ A) clé non vide
#     if pk_len > 0:
#         inner = rewrite(rest_query)

#         #  (i) F positif  →  EXISTENTIEL
#         if not neg:
#             phi = exists(key_vars, f"{atom_to_str(F)} ⊓ {inner}")
#         #  (ii) F négatif →  ∀  (implication)
#         else:
#             antecedent = atom_to_str(F)[1:]      # on retire le «¬»
#             phi = forall(key_vars, f"¬{antecedent} ⊔ {inner}")
#         return phi

#     # ------------------------------------------------------------------ B) clé vide
#     const_part = [t for t in args if not is_variable(t)]
#     var_part   = [t for t in args if is_variable(t)]
#     fresh_E    = fresh_rel()
#     tuple_E    = ", ".join(var_part)

#     inner = rewrite(rest_query)

#     #  (i)  F négatif  :  φ := inner  ⊓  ∀y ( pred(const, y) → inner[¬E(y)] )
#     if neg:
#         inner_negE = rewrite(rest_query + [(True, fresh_E, len(var_part), tuple(var_part))])
#         guarded = forall(var_part,
#                          f"{pred}({', '.join(args)}) → {inner_negE}")
#         return f"{inner} ⊓ {guarded}"

#     #  (ii) F positif  :  φ := ∃y ( pred(const,y) ⊓ ∀y' ( pred(const,y') → ∃θ inner ) )
#     else:
#         theta_inner = exists(var_part, inner)
#         guarded = forall(var_part,
#                          f"{pred}({', '.join(args)}) → {theta_inner}")
#         return exists(var_part, f"{pred}({', '.join(args)}) ⊓ {guarded}")



# -----------------------------------------------------------------------------
#  rewrite.py   – consistent first‑order rewriting  (Lemme 6.1)

from itertools import count
from .attack_graph import build_attack_graph
from .IsCertain import is_variable, is_all_key_atom, select_unattacked_non_all_key_atom

# -----------------------------------------------------------------------------
#  outils de pretty‑printing
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
#  générateur de nouveaux symboles  (E1, E2, …)  pour les clés vides
_fresh = count(1)
def fresh_rel():
    return f"E{next(_fresh)}"

# -----------------------------------------------------------------------------
#  réécriture principale   (Algorithme 3 implicite dans la preuve)
def rewrite(query):
    if all(is_all_key_atom(a) for a in query):
        return conj(query)

    F = select_unattacked_non_all_key_atom(query)
    if F is None:
        return conj(query)

    neg, pred, pk_len, args = F
    key_vars = [args[i] for i in range(pk_len) if is_variable(args[i])]
    rest_query = [a for a in query if a is not F]

    # A) clé non vide
    if pk_len > 0:
        inner = rewrite(rest_query)

        if not neg:
            # cas spécial pour F positif avec clé non vide : bloc P(cx, y)
            if len(key_vars) == 1:
                x = key_vars[0]
                y = [a for i, a in enumerate(args) if i >= pk_len and is_variable(a)]
                yprime = [f"{v}′" for v in y]
                block_atom = f"{pred}({x}, {', '.join(y)})"
                block_guard = f"{pred}({x}, {', '.join(yprime)})"
                block_cond = forall(yprime, f"{block_guard} → {inner}")
                return exists(y, f"{block_atom} ⊓ {block_cond}")
            else:
                return exists(key_vars, f"{atom_to_str(F)} ⊓ {inner}")
        else:
            antecedent = atom_to_str(F)[1:]  # retire le ¬
            return forall(key_vars, f"¬{antecedent} ⊔ {inner}")

    # B) clé vide
    const_part = [t for t in args if not is_variable(t)]
    var_part = [t for t in args if is_variable(t)]
    fresh_E = fresh_rel()

    inner = rewrite(rest_query)

    if neg:
        inner_negE = rewrite(rest_query + [(True, fresh_E, len(var_part), tuple(var_part))])
        guarded = forall(var_part, f"{pred}({', '.join(args)}) → {inner_negE}")
        return f"{inner} ⊓ {guarded}"
    else:
        theta_inner = exists(var_part, inner)
        guarded = forall(var_part, f"{pred}({', '.join(args)}) → {theta_inner}")
        return exists(var_part, f"{pred}({', '.join(args)}) ⊓ {guarded}")
