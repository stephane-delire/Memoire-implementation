"""
-------------------------------------------------------------------------------
Attack_graph.py

Methodes pour construire un graphe d'attaque à partir d'une requête, et pour
vérifier si le graphe est cyclique ou acyclique.

Si le graphe est acyclique, on peut construire une réécriture logique de la
requête en FO, mais si le graphe est cyclique, NP-complet.

Chaque atome (positif ou negatif) est un noeud.
L'attaque dépend : 
    - de la clé primaire de l'atome (sous forme d'ensemble de variables)
    - des dépendances fonctionnelles entre variables

La clé primaire provoque l'attaque.
Si F et G sont 2 atomes de la requête, F attaque G si :
    - une variable de la clé primaire de G dépend d'une variable de F en 
    utilisant les dépendances dans q


-------------------------------------------------------------------------------
"""



# =============================================================================
# ----------------------------------------------------------------- Build graph
# def build_attack_graph(query):
#     """
#     Construit le graphe d'attaque en respectant la définition stricte de l'article :
#     - Une attaque existe de F vers G si une variable de clé primaire de G
#       est atteignable depuis F via la closure fonctionnelle.
    
#     On considère tant les atomes positifs que négatifs (voir Section 4.1 de l'article).
#     """
#     atoms = [(neg, pred, pk_len, args) for (neg, pred, pk_len, args) in query]
#     graph = dict()

#     # Construction du set des dépendances fonctionnelles
#     # Seuls les atomes positifs fournissent des dépendances fonctionnelles
#     dependencies = []
#     for neg, pred, pk_len, args in atoms:
#         if not neg:  # uniquement les atomes positifs
#             key = args[:pk_len]
#             for var in args:
#                 if var not in key:
#                     dependencies.append((key, var))

#     # Fonction pour calculer la closure stricte
#     def closure(vars_init):
#         closure_set = set(vars_init)
#         changed = True
#         while changed:
#             changed = False
#             for key_vars, var in dependencies:
#                 if set(key_vars).issubset(closure_set) and var not in closure_set:
#                     closure_set.add(var)
#                     changed = True
#         return closure_set

#     # Construction du graphe d'attaque
#     for f in atoms:
#         f_neg, f_pred, f_pk_len, f_args = f
#         graph[f] = []

#         f_vars = set(f_args)
#         f_closure = closure(f_vars)

#         for g in atoms:
#             if f == g:
#                 continue  # pas d'attaque sur soi-même

#             g_neg, g_pred, g_pk_len, g_args = g
#             g_pk_vars = set(g_args[:g_pk_len])

#             # vérifie que la clé primaire entière de G est atteinte
#             if not g_pk_vars:
#                 continue  # Pas de clé primaire, Impossible d'attaquer
#             if g_pk_vars.issubset(f_closure):
#                 graph[f].append(g)

#     return graph

def build_attack_graph(query):
    atoms = [(neg, pred, pk_len, args) for (neg, pred, pk_len, args) in query]
    graph = {f: [] for f in atoms}

    # Dépendances : seulement depuis les positifs
    dependencies = []
    for neg, pred, pk_len, args in atoms:
        if not neg:                       # atome positif
            key = args[:pk_len]
            for var in args:
                if var not in key:
                    dependencies.append((tuple(key), var))

    def closure(key_vars):
        X = set(key_vars)                # on part de la clé, pas de tout l'atome
        changed = True
        while changed:
            changed = False
            for Y, z in dependencies:
                if set(Y) <= X and z not in X:
                    X.add(z)
                    changed = True
        return X

    for f in atoms:
        f_neg, f_pred, f_pk_len, f_args = f
        if f_neg:                        # règle 1 : seul un POSITIF peut attaquer
            continue

        f_key = f_args[:f_pk_len]
        f_clos = closure(f_key)

        for g in atoms:
            if f == g:
                continue
            g_pk = set(g[3][:g[2]])
            if g_pk and g_pk <= f_clos:
                graph[f].append(g)

    return graph


# =============================================================================
# ----------------------------------------------------------------- Cycle check
def detect_cycle(graph):
    """
    Détecte s'il existe un cycle dans le graphe d'attaque.
    Algorithme basé sur DFS (Depth First Search).
    """
    visited = set()
    stack = set()

    def dfs(node):
        if node in stack:
            return True  # Cycle trouvé
        if node in visited:
            return False
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        stack.remove(node)
        return False

    for node in graph:
        if dfs(node):
            return True
    return False

# =============================================================================
# -------------------------------------------------------------------- Printing
def print_attack_graph(graph):
    """
    Affiche lisiblement le graphe d'attaque.
    """
    s = ""
    for src, targets in graph.items():
        src_name = f"{src[1]}({', '.join(src[3])})"
        for tgt in targets:
            tgt_name = f"{tgt[1]}({', '.join(tgt[3])})"
            s += f"  {src_name}  --->  {tgt_name}\n"
    return s.strip()  # Enlève le dernier \n

# =============================================================================
# -------------------------------------------------------------------- Graphviz
def draw_attack_graph(graph, filename="attack_graph"):
    """
    Génère une image du graphe d'attaque avec Graphviz.
    A voir si réllement utile...
    """
    # Safe import, c'est vérifié dans "certainty" si
    # graphviz est installé
    from graphviz import Digraph
    
    dot = Digraph()
    dot.attr(rankdir='LR')  # Graphe horizontal, plus lisible

    # Ajouter les nœuds
    for node in graph:
        name = f"{node[1]}({', '.join(node[3])})"
        dot.node(name)

    # Ajouter les flèches
    for src, targets in graph.items():
        src_name = f"{src[1]}({', '.join(src[3])})"
        for tgt in targets:
            tgt_name = f"{tgt[1]}({', '.join(tgt[3])})"
            dot.edge(src_name, tgt_name)

    # a utiliser pour générer un fichier
    # dot.render(filename, format='png', cleanup=True)
    
    # Renvoie l'image au format PNG
    img_bytes = dot.pipe(format='png')  # Renvoie un bytes object
    return img_bytes