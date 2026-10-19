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
        self.playerPos = self.trouverJoueur()

    def trouverJoueur(self):
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
        successeurs = []
        r, c = self.playerPos

        for action in ("UP", "DOWN", "LEFT", "RIGHT"):
            dr, dc = ACTIONS[action]
            n1 = (r + dr, c + dc)
            n1Case = self.grid[n1[0]][n1[1]]

            if n1Case == "O":
                # Mur : déplacement impossible.
                continue

            if n1Case == " " or n1Case == "S":
                # Case libre : le joueur se déplace simplement.
                nouvelleGrille = self.deplacerJoueur(r, c, n1[0], n1[1])
                successeurs.append((action, SokobanPuzzle(nouvelleGrille)))
                continue

            if n1Case == "B" or n1Case == "*":
                # Caisse : on ne peut la pousser que si la case suivante est libre.
                n2 = (r + 2 * dr, c + 2 * dc)
                n2Case = self.grid[n2[0]][n2[1]]
                if n2Case == " " or n2Case == "S":
                    nouvelleGrille = self.pousserCaisse(r, c, n1[0], n1[1], n2[0], n2[1])
                    successeurs.append((action, SokobanPuzzle(nouvelleGrille)))
                continue

        return successeurs

    def deplacerJoueur(self, r, c, nr, nc):
        # Construit une nouvelle grille avec le joueur déplacé de (r,c) vers (nr,nc).
        lignes = [list(ligne) for ligne in self.grid]

        # Case quittée par le joueur.
        if self.grid[r][c] == "R":
            lignes[r][c] = " "
        elif self.grid[r][c] == ".":
            lignes[r][c] = "S"

        # Case occupée par le joueur.
        if self.grid[nr][nc] == "S":
            lignes[nr][nc] = "."
        else:
            lignes[nr][nc] = "R"

        return ["".join(ligne) for ligne in lignes]

    def pousserCaisse(self, r, c, nr, nc, nnr, nnc):
        # Construit une nouvelle grille : le joueur avance de (r,c) vers (nr,nc)
        # et pousse la caisse de (nr,nc) vers (nnr,nnc).
        lignes = [list(ligne) for ligne in self.grid]

        # Case quittée par le joueur.
        if self.grid[r][c] == "R":
            lignes[r][c] = " "
        elif self.grid[r][c] == ".":
            lignes[r][c] = "S"

        # Case où arrive la caisse.
        if self.grid[nnr][nnc] == "S":
            lignes[nnr][nnc] = "*"
        else:
            lignes[nnr][nnc] = "B"

        # Case où arrive le joueur (où était la caisse).
        if self.grid[nr][nc] == "*":
            lignes[nr][nc] = "."
        else:
            lignes[nr][nc] = "R"

        return ["".join(ligne) for ligne in lignes]
