# Classe SokobanPuzzle : représente un état du jeu (la grille) et les règles du jeu.
# Toutes les règles du jeu doivent vivre ici, dans successorFunction(), et nulle part ailleurs.

# Les 4 déplacements possibles, avec leur delta (ligne, colonne).
ACTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


class SokobanPuzzle:

    def __init__(self, grid):
        # Correspond à init() dans l'énoncé.
        # On stocke la grille sous forme de tuple de chaînes (immuable, donc hashable).
        self.grid = tuple(grid)
        self.player_pos = self.trouver_joueur()

    def trouver_joueur(self):
        # Cherche le joueur dans la grille ('R' ou '.') et retourne sa position (ligne, colonne).
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                case = self.grid[r][c]
                if case == "R" or case == ".":
                    return (r, c)
        return None

    def __eq__(self, other):
        # Deux états sont égaux si leurs grilles sont identiques.
        return isinstance(other, SokobanPuzzle) and self.grid == other.grid

    def __hash__(self):
        # La grille (tuple de chaînes) est hashable : utile pour les sets de BFS
        # (test "child.state not in Closed and not in Open").
        return hash(self.grid)

    def __str__(self):
        return "\n".join(self.grid)

    def isGoal(self):
        # But atteint quand il ne reste plus de caisse hors case cible ('B').
        # Comme il y a toujours autant de cases cibles que de caisses, l'absence
        # de 'B' veut dire que toutes les caisses sont devenues '*' (sur une cible).
        for ligne in self.grid:
            if "B" in ligne:
                return False
        return True

    def successorFunction(self):
        # Génère la liste des (action, successeur) pour les 4 directions, dans
        # l'ordre UP, DOWN, LEFT, RIGHT, pour que le résultat soit déterministe.
        # n1 = case où le joueur veut aller, n2 = case juste derrière (utile seulement pour pousser).
        successeurs = []
        r, c = self.player_pos

        for action in ("UP", "DOWN", "LEFT", "RIGHT"):
            dr, dc = ACTIONS[action]
            n1_case = self.grid[r + dr][c + dc]

            if n1_case == " " or n1_case == "S":
                # Case libre : le joueur avance simplement.
                successeurs.append((action, SokobanPuzzle(self.nouvelle_grille(r, c, dr, dc, False))))
            elif n1_case == "B" or n1_case == "*":
                # Caisse : on ne peut la pousser que si la case derrière est libre
                # (pas un mur, pas une autre caisse).
                n2_case = self.grid[r + 2 * dr][c + 2 * dc]
                if n2_case == " " or n2_case == "S":
                    successeurs.append((action, SokobanPuzzle(self.nouvelle_grille(r, c, dr, dc, True))))
            # Sinon c'est un mur : déplacement impossible, pas de successeur.

        return successeurs

    def nouvelle_grille(self, r, c, dr, dc, pousse):
        # Construit la grille de l'état suivant (l'état actuel n'est jamais modifié) :
        # le joueur va de (r, c) vers (r+dr, c+dc) ; si pousse est vrai, il pousse la caisse
        # qui était sur cette case vers (r+2dr, c+2dc).
        lignes = [list(ligne) for ligne in self.grid]

        # Case quittée par le joueur : elle redevient vide, ou cible s'il était sur une cible.
        if self.grid[r][c] == ".":
            lignes[r][c] = "S"
        else:
            lignes[r][c] = " "

        # Case où arrive le joueur : '.' si c'est une cible (avec ou sans caisse avant), sinon 'R'.
        case = self.grid[r + dr][c + dc]
        if case == "S" or case == "*":
            lignes[r + dr][c + dc] = "."
        else:
            lignes[r + dr][c + dc] = "R"

        # Case où arrive la caisse poussée : '*' si c'est une cible, sinon 'B'.
        if pousse:
            if self.grid[r + 2 * dr][c + 2 * dc] == "S":
                lignes[r + 2 * dr][c + 2 * dc] = "*"
            else:
                lignes[r + 2 * dr][c + 2 * dc] = "B"

        return ["".join(ligne) for ligne in lignes]
