"""
--------------------------------------------------------------------------------
parseur.py

Objet définissant le parseur permettant de passer d'un fichier/texte brut
vers un dictionnaire de données python.

--------------------------------------------------------------------------------
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any

Fact        = Tuple[str, int, List[str]]           # (pred, pk_len,  args)
Condition   = Tuple[bool, str, int, List[str]]     # (neg,  pred, pk_len, args)
ParseResult = Dict[str, List[Any]]                 # {"database":[Fact], "query":[Condition]}


class parseur:
    """
    Classe permettant de parser un fichier texte brut en un dictionnaire python.
    """

    def __init__(self):
        """
        Constructeur de la classe parseur.
        """
        pass

    @staticmethod
    def parse(text):
        """
        Fonction permettant de parser un fichier texte brut en un dictionnaire python.
        :param text: Le texte brut à parser.
        :return: Un dictionnaire python contenant les données du fichier.
        """
        # Var
        current = None
        
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
            print(line)

        # return parseur.parse_dsl(text)

    @staticmethod
    def parse_dsl(text: str) -> ParseResult:
        """
        Reconnaît @database / @query et renvoie :
            database : list[Fact]
            query    : list[Condition]
        """
        sections: ParseResult = {"database": [], "query": []}
        current = None

        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("@database"):
                current = "database"; continue
            if line.startswith("@query"):
                current = "query";    continue
            if current is None:
                continue

            # --- négation éventuelle (seulement côté @query) ---
            neg = False
            if current == "query" and line.startswith("not "):
                neg = True
                line = line[4:].lstrip()

            # --- prédicat + arguments (on garde la position du ";") ---
            m = re.fullmatch(r"(\w+)\s*\(([^)]*)\)\s*", line)
            if not m:
                raise ValueError(f"Ligne mal formée : {raw}")
            pred, argblock = m.groups()

            # Séparation clé primaire / autres attributs
            pk_part, *rest_part = argblock.split(";", 1)
            pk_args   = [a.strip() for a in re.split(r"[,\s]+", pk_part) if a.strip()]
            rest_args = [a.strip() for a in re.split(r"[,\s]+", rest_part[0]) if a.strip()] if rest_part else []

            args   = pk_args + rest_args
            pk_len = len(pk_args)

            if current == "database":
                sections["database"].append((pred, pk_len, args))
            else:
                sections["query"].append((neg, pred, pk_len, args))

        return sections
    
    @staticmethod
    def to_sql(parsed):
        # Très simplifié : suppose qu’il n’y a qu’un seul littéral positif
        pos = next((l for l in parsed["query"] if not l[0]), None)
        if pos is None:
            raise ValueError("Au moins un littéral positif requis")
        _, pred0, _, vars0 = pos

        sql  = [f'SELECT DISTINCT "yes"\nFROM {pred0} AS T0']
        alias = 1
        for neg, pred, _, vars in parsed["query"]:
            if neg:
                # construit la clause NOT EXISTS
                join = " AND ".join(
                    f"T{alias}.{v_left} = T0.{v_right}"
                    for v_left, v_right in zip(vars, vars0)
                )
                sql.append(f"WHERE NOT EXISTS (SELECT * FROM {pred} AS T{alias}\n"
                        f"              WHERE {join})")
                alias += 1
        return "\nAND ".join(sql)