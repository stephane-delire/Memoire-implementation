"""
--------------------------------------------------------------------------------
Fichier de test unitaire pour le projet d'implémentation du mémoire.
--------------------------------------------------------------------------------
"""

import unittest
from sources.parseur import parse
from sources.ngfo import is_guarded
from sources.attack_graph import build_attack_graph, detect_cycle
from sources.certainty import certainty

# =============================================================================
# --------------------------------------------------------------------- Parseur
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


# =============================================================================
# ------------------------------------------------------------------------ NGFO
class TestNGFO(unittest.TestCase):
    # --------------------------------------------------- Cas de base
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

    # =========================================================================
    # --------------------------------------------------------------------- Sjf
    def test_sjf(self):
        """
        Teste une requête qui n'est pas self-join free.
        """
        query = [
            (False, 'Likes', 2, ('p', 't')),
            (False, 'Likes', 2, ('p', 't'))
        ]
        result = is_guarded(query)
        self.assertEqual(result, (False, "not sjf"))
        
    def test_sfj2(self):
        """
        Teste une requête qui n'est pas self-join free.
        """
        query = [
            (False, 'Likes', 2, ('p', 't')),
            (False, 'Likes', 2, ('p', 't')),
            (True, 'Lives', 1, ('p', 't')),
            (False, 'Likes', 2, ('p', 't')),
        ]
        result = is_guarded(query)
        self.assertEqual(result, (False, "not sjf"))

# =============================================================================
# ---------------------------------------------------------------- Attack graph
class TestAttackGraph(unittest.TestCase):
    def test_empty_query(self):
        query = []
        graph = build_attack_graph(query)
        self.assertEqual(graph, {})

    def test_no_attack(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 1, ('a', 'b'))  # aucune dépendance fonctionnelle ne permet d’atteindre 'a'
        ]
        graph = build_attack_graph(query)
        self.assertEqual(len(graph), 2)
        for v in graph.values():
            self.assertEqual(v, [])
        self.assertFalse(detect_cycle(graph))

    def test_single_attack(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 1, ('y', 'z'))
        ]
        graph = build_attack_graph(query)
        attackers = [k for k, v in graph.items() if v]
        self.assertEqual(len(attackers), 1)
        self.assertIn((False, 'A', 1, ('x', 'y')), attackers)
        self.assertFalse(detect_cycle(graph))

    def test_multiple_attacks(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 1, ('y', 'z')),
            (False, 'C', 1, ('z', 'x'))
        ]
        graph = build_attack_graph(query)
        count = sum(len(v) for v in graph.values())
        self.assertEqual(count, 6)
        self.assertTrue(detect_cycle(graph))

    def test_cycle_present(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 1, ('y', 'z')),
            (False, 'C', 1, ('z', 'x'))  # forme un cycle complet
        ]
        graph = build_attack_graph(query)
        self.assertTrue(detect_cycle(graph))

    def test_cross_attacks_cycle(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 1, ('x', 'z')),
            (False, 'C', 1, ('y', 'w'))  # A attaque C, B n’attaque personne
        ]
        graph = build_attack_graph(query)
        self.assertTrue(detect_cycle(graph))

    def test_target_with_empty_pk(self):
        query = [
            (False, 'A', 1, ('x', 'y')),
            (False, 'B', 0, ('z', 'w'))  # pas de clé primaire => ne peut être attaqué
        ]
        graph = build_attack_graph(query)
        self.assertFalse(detect_cycle(graph))

    def test_negative_atoms(self):
        query = [
            (True, 'Neg1', 1, ('a', 'b')),
            (True, 'Neg2', 1, ('b', 'c')),
        ]
        graph = build_attack_graph(query)

        expected = {
            (True, 'Neg1', 1, ('a', 'b')): [(True, 'Neg2', 1, ('b', 'c'))],
            (True, 'Neg2', 1, ('b', 'c')): []
        }
        self.assertEqual(graph, expected)
        self.assertFalse(detect_cycle(graph))

    def test_cycle_wg(self):
        """
        Teste un cycle dans le graphe d'attaque.
        """
        query = [
            (False, 'P', 1, ('x', 'y')),
            (False, 'Q', 1, ('y', 'z')),
            (False, 'R', 1, ('z', 'x')),
            (True, 'D', 1, ('x', 'y', 'z'))
        ]
        graph = build_attack_graph(query)
        self.assertTrue(detect_cycle(graph))

# =============================================================================
# ------------------------------------------------------------------- certainty
"""
Evaluation de la fonction certainty.
"""
class TestCertainty(unittest.TestCase):
    def test_correct(self):
        """
        Teste une requête a priori correcte.
        """
        text = """
        @database
        Likes(John, Paris;)
        Dislikes(John, London;)
        Hates(John, Berlin;)

        @query
        Likes(p, t;)
        not Dislikes(p, t)
        not Hates(t, p)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], True)
        self.assertEqual(guarded[1], "NGFO")
        self.assertEqual(cycle, True)
        self.assertEqual(certain, True)

    def test_not_sjf(self):
        """
        Teste une requête pas sjf.
        """
        text = """
        @database
        Friend(John, Mary;)
        Friend(Mary, Bob;)
        Enemy(Bob, John;)

        @query
        Friend(x, y;)
        Friend(y, z;)
        Enemy(z, x;)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], False)
        self.assertEqual(guarded[1], "not sjf")
        self.assertEqual(graph, None)
        self.assertEqual(cycle, None)
        self.assertEqual(certain, None)

    def test_neg_not_certain(self):
        """
        Teste une requête NFGO mais pas certaine.
        """
        text = """
        @database
        Parent(John, Mary;)
        Parent(Mary, Alice;)
        Teacher(Mary;)
        Student(Alice;)

        @query
        Parent(x, y;)
        Teacher(x;)
        not Student(y;)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], True)
        self.assertEqual(guarded[1], "NGFO")
        self.assertEqual(cycle, False)
        self.assertEqual(certain, False)
    
    def test_correct2(self):
        """
        Teste une requête a priori correcte.
        """
        text = """
        @database
        Parent(John, Mary;)
        Parent(Mary, Alice;)
        Teacher(Mary;)
        Student(Bob;)

        @query
        Parent(x, y;)
        Teacher(x;)
        not Student(y;)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], True)
        self.assertEqual(guarded[1], "NGFO")
        self.assertEqual(cycle, False)
        self.assertEqual(certain, True)
    
    def test_wk(self):
        """
        Teste une requête weakly-guarded.
        """
        text = """
        @database
        P(a, b;)
        Q(a, c;)
        R(c, b;)

        @query
        P(x, y;)
        Q(x, z;)
        R(z, y;)
        not S(x, y, z)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], True)
        self.assertEqual(guarded[1], "WG")
        self.assertEqual(cycle, False)
        self.assertEqual(certain, True)

    def test_wk_cyclic(self):
        """
        Teste une requête weakly-guarded mais cyclique ?
        Utilise le select_unattacked_non_all_key_atom
        Mais ne détecte pas le cycle !
        Semble etre un cas particulier...

        """
        text = """
        @database
        P(a; b)
        Q(b; c)
        R(c; a)
        D(a, b, c;)

        @query
        P(x; y)
        Q(y; z)
        R(z; x)
        not D(x, y, z)
        """
        data, guarded, graph, cycle, certain, rewrite = certainty(text)
        self.assertEqual(guarded[0], True)
        self.assertEqual(guarded[1], "WG")
        self.assertEqual(cycle, True)
        self.assertEqual(certain, False)

if __name__ == "__main__":
    unittest.main()