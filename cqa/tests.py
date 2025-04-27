"""
--------------------------------------------------------------------------------
Fichier de test unitaire pour le projet d'implémentation du mémoire.
--------------------------------------------------------------------------------
"""

import unittest
from sources2.parseur import parse
from sources2.ngfo import is_guarded


# ==============================================================================
# ---------------------------------------------------------------------- Parseur
class TestParseur(unittest.TestCase):
    # --------------------------------------------------------- Cas de base
    def test_cas_base(self):
        """
        Teste le cas de base.
        """
        text = """
    @database
    Likes(John, Paris;)
    Lives(John; London)
    Mayor(Paris; Hidalgo)
    Mayor(London; Khan)

    @query
    Likes(p,t;)
    not Lives(p;t)
    not Mayor(t;p)
        """
        data = parse(text)
        self.assertEqual(data["database"], [
            ("Likes", 2, ("John", "Paris")),
            ("Lives", 1, ("John", "London")),
            ("Mayor", 1, ("Paris", "Hidalgo")),
            ("Mayor", 1, ("London", "Khan"))
        ])
        self.assertEqual(data["query"], [
            (False, "Likes", 2, ("p", "t")),
            (True, "Lives", 1, ("p", "t")),
            (True, "Mayor", 1, ("t", "p"))
        ])

    # --------------------------------------------------------- Cas commenté
    def test_cas_commente(self):
        """
        Teste le cas commenté.
        """
        text = """
    # Commentaire
    @database
    Likes(John, Paris;)
    Lives(John; London)
    Mayor(Paris; Hidalgo) # Commentaire
    Mayor(London; Khan)
    @query
    Likes(p,t;)
    not Lives(p;t)
    not Mayor(t;p)
    # Commentaire
        """
        data = parse(text)
        self.assertEqual(data["database"], [
            ("Likes", 2, ("John", "Paris")),
            ("Lives", 1, ("John", "London")),
            ("Mayor", 1, ("Paris", "Hidalgo")),
            ("Mayor", 1, ("London", "Khan"))
        ])
        self.assertEqual(data["query"], [
            (False, "Likes", 2, ("p", "t")),
            (True, "Lives", 1, ("p", "t")),
            (True, "Mayor", 1, ("t", "p"))
        ])
    # --------------------------------------------------------- Texte vide
    def test_texte_vide(self):
        """
        Teste le cas d'un texte vide.
        """
        text = ""
        with self.assertRaises(ValueError) as context:
            parse(text)
        self.assertIn("Aucune @database trouvée", str(context.exception))
    
    # --------------------------------------------------------- Sans DB
    def test_sans_database(self):
        """
        Teste un texte sans @database.
        """
        text = """
    @query
    Likes(p, t;)
        """
        with self.assertRaises(ValueError) as context:
            parse(text)
        self.assertIn("Aucune @database trouvée", str(context.exception))
    # --------------------------------------------------------- Sans Query
    def test_sans_query(self):
        """
        Teste un texte sans @query.
        """
        text = """
    @database
    Likes(John, Paris;)
        """
        with self.assertRaises(ValueError) as context:
            parse(text)
        self.assertIn("Aucune @query trouvée", str(context.exception))
    # --------------------------------------------------------- Ligne mal formée
    def test_ligne_mal_formee(self):
        """
        Teste une ligne mal formée.
        """
        text = """
    @database
    Likes John, Paris; London)
    @query
    Likes(p,t;)
        """
        with self.assertRaises(ValueError) as context:
            parse(text)
        self.assertIn("Ligne mal formée", str(context.exception))
    # --------------------------------------------------------- Atome mal formé
    def test_avec_commentaires(self):
        """
        Teste le parsing avec des lignes contenant des commentaires.
        """
        text = """
    @database
    Likes(John, Paris;) # commentaire ici
    Lives(John; London) # encore un commentaire

    @query
    Likes(p,t;) # test
    # not Lives(p;t) (commenté volontairement)
    not Mayor(t;p)
        """
        data = parse(text)
        self.assertEqual(data["database"], [
            ("Likes", 2, ("John", "Paris")),
            ("Lives", 1, ("John", "London"))
        ])
        self.assertEqual(data["query"], [
            (False, "Likes", 2, ("p", "t")),
            (True, "Mayor", 1, ("t", "p"))
        ])
    # --------------------------------------------------------- Min/Maj
    def test_majuscule_minuscule(self):
        """
        Teste que @Database et @Query sont insensibles à la casse.
        """
        text = """
    @Database
    Likes(John, Paris;)

    @Query
    Likes(p,t;)
        """
        data = parse(text)
        self.assertEqual(data["database"], [
            ("Likes", 2, ("John", "Paris"))
        ])
        self.assertEqual(data["query"], [
            (False, "Likes", 2, ("p", "t"))
        ])


# ==============================================================================
# ------------------------------------------------------------------------- NGFO
class TestNGFO(unittest.TestCase):
    # --------------------------------------------------------- Cas de base
    def test_ngfo(self):
        """
        Teste une requête NGFO classique.
        """
        query = [
            (False, 'Likes', 2, ('p', 't')),
            (True, 'Lives', 1, ('p', 't'))
        ]
        result = is_guarded(query)
        self.assertEqual(result, (True, "NGFO"))
    
    def test_weakly_guarded(self):
        """
        Teste une requête qui est weakly-guarded.
        Celle présente dans l'article
        """
        query = [
            (False, 'R', 1, ('x', 'y')),
            (False, 'S', 1, ('y', 'z')),
            (False, 'T', 1, ('z', 'x')),
            (True, 'N', 1, ('x', 'y', 'z')),
        ]
        result = is_guarded(query)
        self.assertEqual(result, (True, "WG"))
    
    def test_non_guarded(self):
        """
        Teste une requête qui n'est ni NGFO ni weakly-guarded.
        """
        query = [
            (False, 'Likes', 2, ('p', 't')),
            (True, 'Lives', 1, ('p', 'z'))
        ]
        result = is_guarded(query)
        self.assertEqual(result, (False, None))

    def test_que_des_positifs(self):
        """
        Teste une requête avec uniquement des atomes positifs (NGFO trivialement).
        """
        query = [
            (False, 'Likes', 2, ('a', 'b')),
            (False, 'Lives', 1, ('c',))
        ]
        result = is_guarded(query)
        self.assertEqual(result, (True, "NGFO"))
    
    def test_que_des_negatifs(self):
        """
        Teste une requête avec uniquement des atomes négatifs (jamais gardée).
        """
        query = [
            (True, 'Likes', 2, ('a', 'b')),
            (True, 'Lives', 1, ('c',))
        ]
        result = is_guarded(query)
        self.assertEqual(result, (False, None))






if __name__ == "__main__":
    unittest.main()