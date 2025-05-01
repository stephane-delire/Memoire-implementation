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

# -----------------------------------------------------------------------------
def certainty(text):
    """
    Fonction principale qui gère le flux de travail de la vérification de la 
    certitude.
    Elle parse le texte d'entrée, vérifie la structure NGFO, construit
    le graphe d'attaque, détecte les cycles et évalue la certitude 
    de la requête.
    :param text: Le texte d'entrée contenant la base de données et la requête.
    """
    # ------------------------------------------------------------------- Parse
    data = parse(text)
    # -------------------------------------------------------------------- NGFO
    guarded = is_guarded(data["query"])
    # ------------------------------------------------------------ Attack graph
    attack_graph = build_attack_graph(data["query"])
    # ------------------------------------------------------------ graphe Cycle
    cycle = detect_cycle(attack_graph)
    # --------------------------------------------------------------- certainty
