# Classe SokobanPuzzle : représente un état du jeu (la grille) et les règles du jeu.
# Toutes les règles du jeu doivent vivre ici, dans successorFunction(), et nulle part ailleurs.


class SokobanPuzzle:

    def __init__(self, grid):
        # Crée un état à partir d'une grille (liste ou tuple de chaînes).
        # Correspond à init() dans l'énoncé.
        pass

    def __eq__(self, other):
        # Compare deux états en comparant leurs grilles.
        pass

    def __hash__(self):
        # Permet de mettre un état dans un set ou comme clé de dict (utile pour BFS).
        pass

    def __str__(self):
        # Affiche la grille sous forme de texte (debug / mode console).
        pass

    def isGoal(self):
        # Vrai si tous les B ont été transformés en * (plus aucune boîte hors case cible).
        pass

    def successorFunction(self):
        # Retourne la liste des couples (action, successeur) possibles depuis cet état.
        pass
