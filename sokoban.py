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

    def __init__(self, grid, player_pos=None):
        # Correspond à init() dans l'énoncé.
        # On stocke la grille sous forme de tuple de chaînes (immuable, donc hashable).
        # player_pos : position du joueur si on la connaît déjà (c'est le cas pour un successeur :
        # on vient de le déplacer). Sinon (niveau de départ), on la cherche une seule fois dans la grille.
        # Les lignes peuvent avoir des longueurs differentes (un niveau en forme de L, par exemple) :
        # on complete les lignes courtes avec des murs 'O', donc le reste du code voit une grille rectangulaire.
        largeur = 0
        for ligne in grid:
            largeur = max(largeur, len(ligne))
        self.grid = tuple(ligne.ljust(largeur, "O") for ligne in grid)
        if player_pos is None:
            player_pos = self.trouver_joueur()
        self.player_pos = player_pos

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
            n1 = (r + dr, c + dc)
            n1_case = self.grid[n1[0]][n1[1]]

            if n1_case == " " or n1_case == "S":
                # Case libre : le joueur avance simplement (sa nouvelle position est n1, pas besoin de la chercher).
                successeurs.append((action, SokobanPuzzle(self.nouvelle_grille(r, c, dr, dc, False), n1)))
            elif n1_case == "B" or n1_case == "*":
                # Caisse : on ne peut la pousser que si la case derrière est libre
                # (pas un mur, pas une autre caisse).
                n2_case = self.grid[r + 2 * dr][c + 2 * dc]
                if n2_case == " " or n2_case == "S":
                    successeurs.append((action, SokobanPuzzle(self.nouvelle_grille(r, c, dr, dc, True), n1)))
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


# ---------------------------------------------------------------------------
# Détection de deadlock (partie D). Ce ne sont PAS des règles du jeu : ces fonctions servent seulement
# à repérer une caisse "perdue" (qu'on ne pourra plus jamais mettre sur une cible), pour que A* ne perde
# pas son temps sur ces positions. On répond True seulement si on est sûr : sinon A* pourrait rater
# la solution optimale.
# ---------------------------------------------------------------------------

def est_mur(grid, r, c):
    # Vrai si la case (r, c) est un mur (ou en dehors de la grille).
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[r]):
        return True
    return grid[r][c] == "O"


def est_cible(grid, r, c):
    # Vrai si la case (r, c) est une case cible (vide, avec le joueur, ou avec une caisse).
    return grid[r][c] == "S" or grid[r][c] == "." or grid[r][c] == "*"


def est_coin_deadlock(grid, r, c):
    # Deadlock d'angle : une caisse hors cible ('B') avec un mur au-dessus ou en dessous
    # ET un mur à gauche ou à droite ne bougera plus jamais.
    if grid[r][c] != "B":
        return False
    mur_vertical = est_mur(grid, r - 1, c) or est_mur(grid, r + 1, c)
    mur_horizontal = est_mur(grid, r, c - 1) or est_mur(grid, r, c + 1)
    return mur_vertical and mur_horizontal


def bout_sans_issue(grid, r, c, mr, mc, dr, dc):
    # La caisse est collée à un mur : le mur est du côté (mr, mc). On avance le long du mur dans la direction (dr, dc).
    # Retourne True si on arrive au mur du bout sans avoir vu de cible et sans que le mur s'arrête.
    while not est_mur(grid, r, c):
        if est_cible(grid, r, c):
            return False                    # une cible sur la ligne : la caisse peut y glisser
        if not est_mur(grid, r + mr, c + mc):
            return False                    # le mur s'arrête : la caisse pourrait sortir de la ligne
        r = r + dr
        c = c + dc
    return True


def est_ligne_deadlock(grid, r, c):
    # Deadlock de ligne : une caisse hors cible collée à un mur ne peut que glisser le long de ce mur.
    # Si la ligne de mur n'a aucune cible et que ses deux bouts sont fermés, la caisse est perdue.
    if grid[r][c] != "B":
        return False
    for mr in (-1, 1):                      # mur au-dessus ou en dessous : la caisse glisse à gauche et à droite
        if est_mur(grid, r + mr, c):
            if bout_sans_issue(grid, r, c, mr, 0, 0, 1) and bout_sans_issue(grid, r, c, mr, 0, 0, -1):
                return True
    for mc in (-1, 1):                      # mur à gauche ou à droite : la caisse glisse en haut et en bas
        if est_mur(grid, r, c + mc):
            if bout_sans_issue(grid, r, c, 0, mc, 1, 0) and bout_sans_issue(grid, r, c, 0, mc, -1, 0):
                return True
    return False


def is_deadlock(etat):
    # Vrai si l'état contient au moins une caisse perdue (dans un angle, ou sur une ligne de mur sans cible).
    grid = etat.grid
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == "B":
                if est_coin_deadlock(grid, r, c) or est_ligne_deadlock(grid, r, c):
                    return True
    return False
