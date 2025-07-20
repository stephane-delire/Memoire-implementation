"""
-------------------------------------------------------------------------------
Attack_graph.py

Refonte de Juillet 2025.
Au vu des différents tests, il semble que soit la définition dans l'article
soit erronée, ou alors les exemples sont erronés(mal choisis).
D'apres les test et expérimentations, il est impossible de construire
un graphe d'attaque sur la façon dont il est défini et de reproduire les
exemples de l'article.
En particulier, la query Qa de la page 213.

De ce fait, afin de respecter un minimum la définition, et surtout afin de
correspondre aux plus grand nombre de cas testés, le graphe sera construit
selon mon mémo : "Les variables attaquent les clés primaires des atomes"

On ne fait pas la distinction entre les atomes positifs et négatifs, tel que
suggéré à un endroit dans l'article.

-------------------------------------------------------------------------------
"""


#  Version pré juillet 2025, fonctionnelle mais ne correspond pas
# def build_attack_graph(query):
#     atoms = [(neg, pred, pk_len, args) for (neg, pred, pk_len, args) in query]
#     graph = {f: [] for f in atoms}

#     # Dépendances : seulement depuis les positifs
#     dependencies = []
#     for neg, pred, pk_len, args in atoms:
#         if not neg:                       # atome positif
#             key = args[:pk_len]
#             for var in args:
#                 if var not in key:
#                     dependencies.append((tuple(key), var))

#     def closure(key_vars):
#         X = set(key_vars)                # on part de la clé, pas de tout l'atome
#         changed = True
#         while changed:
#             changed = False
#             for Y, z in dependencies:
#                 if set(Y) <= X and z not in X:
#                     X.add(z)
#                     changed = True
#         return X

#     for f in atoms:
#         f_neg, f_pred, f_pk_len, f_args = f
#         if f_neg:                        # règle 1 : seul un POSITIF peut attaquer
#             continue

#         f_key = f_args[:f_pk_len]
#         f_clos = closure(f_key)

#         for g in atoms:
#             if f == g:
#                 continue
#             g_pk = set(g[3][:g[2]])
#             if g_pk and g_pk <= f_clos:
#                 graph[f].append(g)
#     print(graph)
#     exit()
#     return graph

def build_attack_graph(query, trace=None):
    """
    Construit le graphe d'attaque à partir de la requête.
    On part de la définition de l'article, mais on adapte légèrement
    pour correspondre de manière plus générale aux cas testés.
    On considère que les variables attaquent les clés primaires des atomes.
    """
    atoms = []
    dict_to_tuple = {}
    graph_internal = {}

    # Reformulation des atomes avec mapping vers tuples
    trace.append(" - Extraction des atomes de la requête")
    for atom in query:
        neg, pred, pk_len, args = atom
        pks = args[:pk_len]
        variables = args[pk_len:]
        atom_dict = {
            'neg': neg,
            'pred': pred,
            'pk_len': pk_len,
            'args': args,
            'pks': pks,
            'variables': variables
        }
        atoms.append(atom_dict)
        dict_to_tuple[id(atom_dict)] = (neg, pred, pk_len, args)

    trace.append(f" - Nombre d'atomes extraits : {len(atoms)}")
    # impression des atomes dans le trace
    trace.append(" - Atomes extraits :")
    for atom in atoms:
        trace.append(f"   - {atom['neg']} {atom['pred']}({', '.join(atom['args'])})")
    # Construction du graphe d'attaque
    trace.append(" - Construction du graphe d'attaque")

    for atom in atoms:
        atom_id = id(atom)
        atoms_tmp = [a for a in atoms if a is not atom]

        for var in atom['variables']:
            for target in atoms_tmp:
                if var in target['pks']:
                    if atom_id not in graph_internal:
                        graph_internal[atom_id] = []
                    graph_internal[atom_id].append(id(target))
    trace.append(f" - Nombre de dépendances trouvées : {len(graph_internal)}")
    
    # Impression des dépendances dans le trace
    trace.append(" - Dépendances trouvées :")
    for src_id, target_ids in graph_internal.items():
        src_atom = dict_to_tuple[src_id]
        src_name = f"{src_atom[1]}({', '.join(src_atom[3])})"
        for tgt_id in target_ids:
            tgt_atom = dict_to_tuple[tgt_id]
            tgt_name = f"{tgt_atom[1]}({', '.join(tgt_atom[3])})"
            trace.append(f"   - {src_name} ---> {tgt_name}")


    # Conversion finale du graphe en format (tuple) → [tuple] (format d'origine)
    trace.append(" - Conversion du graphe interne en format final")
    graph = {}
    for atom_id, target_ids in graph_internal.items():
        atom_tuple = dict_to_tuple[atom_id]
        target_tuples = [dict_to_tuple[tid] for tid in target_ids]
        graph[atom_tuple] = target_tuples

    return graph

# =============================================================================
# ----------------------------------------------------------------- Cycle check
def detect_cycle(graph, trace=None):
    def log(msg):
        if trace is not None:
            trace.append(msg)

    visited = set()
    rec_stack = set()

    def dfs(v):
        log(f"Visite de {v}")
        visited.add(v)
        rec_stack.add(v)

        for neighbour in graph.get(v, []):
            log(f"  {v} → {neighbour}")
            if neighbour not in visited:
                if dfs(neighbour):
                    log(f"Cycle détecté via {neighbour}")
                    return True
            elif neighbour in rec_stack:
                log(f"Cycle trouvé : {neighbour} est dans la pile récursive")
                return True

        rec_stack.remove(v)
        return False

    for node in graph:
        if node not in visited:
            log(f"Lancement DFS depuis {node}")
            if dfs(node):
                return True

    log("Pas de cycle détecté")
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