"""
--------------------------------------------------------------------------------
parseur.py

Objet définissant le parseur permettant de passer d'un fichier/texte brut
vers un dictionnaire de données python.

--------------------------------------------------------------------------------
"""

import re

def parse(text):
    """
    Fonction permettant de parser un fichier texte brut en un dictionnaire python.
    :param text: Le texte brut à parser.
    :return: Un dictionnaire contenant les données du fichier texte.
    :raises ValueError: Si le texte ne contient pas de données valides.

    @database (predicat, longueur de la clé primaire, [attributs])
    @query (negation, predicat, longueur de la clé primaire, [attributs])
    
    """
    # Var
    current = None
    database = []
    query    = []
    # Parsing
    # ligne par ligne
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@database") or line.startswith("@Database"):
            current = "database"
            continue
        if line.startswith("@query") or line.startswith("@Query"):
            current = "query"
            continue
        if current is None:
            continue
        # Suppression des commentaires
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        # negation
        neg = False
        if current == "query" and (line.startswith("not ") or line.startswith("Not ")):
            neg = True
            line = line[4:].lstrip()
        
        # Prédicat et arguments (on garde la position du ";")
        m = re.fullmatch(r"(\w+)\s*\(([^)]*)\)\s*", line)
        if not m:
            raise ValueError(f"Ligne mal formée : {raw}")
        pred, argblock = m.groups()
        # Séparation clé primaire / autres attributs
        pk_part, *rest_part = argblock.split(";", 1)
        pk_args   = [a.strip() for a in re.split(r"[,\s]+", pk_part) if a.strip()]
        rest_args = [a.strip() for a in re.split(r"[,\s]+", rest_part[0]) if a.strip()] if rest_part else []
        args   = pk_args + rest_args
        args   = tuple(args)
        pk_len = len(pk_args)
        # Ajout dans le dictionnaire
        if current == "database":
            database.append((pred, pk_len, args))
        else:
            query.append((neg, pred, pk_len, args))
    # Vérification
    if not database:
        raise ValueError("Aucune @database trouvée")
    if not query:
        raise ValueError("Aucune @query trouvée")

    # Renvoie le dictionnaire
    return {
        "database": database,
        "query": query
    }

