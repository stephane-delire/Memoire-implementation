"""
-------------------------------------------------------------------------------
certainty

Module général rassemblant les diverses fonctions et intégrant
les différentes parties du code, afin de déterminer la certitude
d'une requête. 


-------------------------------------------------------------------------------
"""

from .parseur import parse
from .ngfo import is_guarded
from .attack_graph import build_attack_graph, detect_cycle, print_attack_graph
from .attack_graph import draw_attack_graph
from .IsCertain import is_certain_core
from .rewriter import rewrite, fo_to_latex
import base64


# -----------------------------------------------------------------------------
def certainty(text, graph_png=False):
    """
    Fonction principale qui gère le flux de travail de la vérification de la 
    certitude.
    Elle parse le texte d'entrée, vérifie la structure NGFO, construit
    le graphe d'attaque, détecte les cycles et évalue la certitude 
    de la requête.
    
    :param text: Le texte d'entrée à analyser.
    :param graph_png: Si True, génère une image du graphe d'attaque.
    
    """
    data, guarded, graph, cycle, certain, rewriting, latex = None, None, None, None, False, None, None
    
    # =========================================================================
    # ------------------------------------------------------------------- Parse
    data = parse(text)
    # =========================================================================
    # -------------------------------------------------------------------- NGFO

    guarded = is_guarded(data["query"])
    
    # Si la requête n'est pas gardée, on ne continue pas
    if not guarded[0]:
        if guarded[1] == "not sjf":
            return data, guarded, graph, cycle, None, None, None
        return data, guarded, graph, cycle, certain, None, None
    # =========================================================================
    # ------------------------------------------------------------ Attack graph
    graph = {}
    base_graph = build_attack_graph(data["query"])
    graph["base"] = base_graph

    # -------------------------------------------------- graphe Cycle
    cycle = detect_cycle(base_graph)
    graph["cycle"] = cycle
    
    # ---------------------------------------------------- graphe txt
    txt_graph = print_attack_graph(base_graph)
    graph["txt"] = txt_graph
    # ---------------------------------------------------- graphe png
    if not graph_png:
        graph["png"] = None
    else:
        try:
            # On essaie d'importer graphviz
            # Si l'import échoue, on met graph_png à None
            # et on ne génère pas l'image
            from graphviz import Digraph
        except ImportError:
            print("graphviz not installed, graph_png set to None")
            graph_png = None

        img = draw_attack_graph(base_graph)
        graph["png"] = base64.b64encode(img).decode('utf-8')
    


    # Si le graphe d'attaque est cyclique, on ne continue pas
    # UPT, un cycle n'interdit pas de continuer, mais l'évaluation
    # est plus complexe... A la base c'était pour éviter les
    # boucles infinies, mais.. les résultats sont faux!
    
    # if cycle:
    #     return data, guarded, graph, cycle, certain

    # =========================================================================
    # --------------------------------------------------------------- certainty
    certain = is_certain_core(data["query"], data["database"])

    # =========================================================================
    # ---------------------------------------------------------------- Rewriter
    # Réécriture de la requête, si gardée et acyclique
    if guarded[0] and not cycle:
        rewriting = rewrite(data["query"])
        # Conversion de la réécriture en LaTeX
        latex = fo_to_latex(rewriting)
    else:
        rewriting = None

    # =========================================================================
    # ------------------------------------------------------------------ Return
    return data, guarded, graph, cycle, certain, rewriting, latex
