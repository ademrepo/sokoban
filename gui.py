# Interface Pygame du jeu.
# Etape 6 : rendu statique d'un niveau (pas encore de deplacement).
# Les etapes 7 a 9 ajouteront le jeu manuel, le menu, l'ecran Bravo, le BFS et la simulation.

import pygame

from levels import LEVELS
from sokoban import SokobanPuzzle
from assets_loader import load_sprites

TAILLE = 48          # taille d'une case en pixels
MARGE = 2            # marge autour du niveau, en nombre de cases (sert de decor)
COULEUR_FOND_CIBLE = (60, 50, 20)
COULEUR_CIBLE = (235, 215, 90)


class Game:

    def __init__(self, numero=0):
        # numero : position du niveau dans LEVELS (0 = Exemple 1).
        pygame.init()
        self.numero = numero
        self.niveau = LEVELS[numero]
        self.etat = SokobanPuzzle(self.niveau["grid"])

        lignes = len(self.etat.grid)
        colonnes = len(self.etat.grid[0])
        largeur = (colonnes + 2 * MARGE) * TAILLE
        hauteur = (lignes + 2 * MARGE) * TAILLE
        self.ecran = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Sokoban - " + self.niveau["name"])

        # Les sprites se chargent apres set_mode.
        self.sprites = load_sprites(TAILLE)
        self.horloge = pygame.time.Clock()
        self.en_cours = True

    def run(self):
        while self.en_cours:
            self.handle_events()
            self.update()
            self.draw()
            self.horloge.tick(30)
        pygame.quit()

    def handle_events(self):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False
            if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                self.en_cours = False

    def update(self):
        # Rien a mettre a jour pour le rendu statique.
        pass

    def touche_le_sol(self, r, c):
        # Vrai si un des 8 voisins de (r, c) n'est pas un mur.
        # Sert a ne dessiner que les murs du bord du labyrinthe (le reste = decor vert).
        grille = self.etat.grid
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr = r + dr
                nc = c + dc
                if 0 <= nr < len(grille) and 0 <= nc < len(grille[nr]):
                    if grille[nr][nc] != "O":
                        return True
        return False

    def dessiner_cible(self, x, y):
        # Croix jaune au centre de la case (la cible n'a pas de sprite dans le pack).
        # On la dessine d'abord en sombre et plus epaisse pour qu'elle ressorte sur l'herbe.
        petit = TAILLE // 4
        centre_x = x + TAILLE // 2
        centre_y = y + TAILLE // 2
        pygame.draw.circle(self.ecran, COULEUR_CIBLE, (centre_x, centre_y), TAILLE // 2 - 6, 2)
        for (couleur, epaisseur) in [(COULEUR_FOND_CIBLE, 8), (COULEUR_CIBLE, 4)]:
            pygame.draw.line(self.ecran, couleur, (centre_x - petit, centre_y - petit), (centre_x + petit, centre_y + petit), epaisseur)
            pygame.draw.line(self.ecran, couleur, (centre_x - petit, centre_y + petit), (centre_x + petit, centre_y - petit), epaisseur)

    def dessiner_haie(self, largeur, hauteur):
        # Rangee de buissons sur tout le bord de la fenetre (il en manque un de temps en temps).
        for r in range(hauteur // TAILLE):
            for c in range(largeur // TAILLE):
                sur_le_bord = r == 0 or c == 0 or r == hauteur // TAILLE - 1 or c == largeur // TAILLE - 1
                if sur_le_bord and (r * 7 + c * 13) % 4 != 0:
                    variante = ["buisson", "buisson2", "buisson3"][(r + c) % 3]
                    self.ecran.blit(self.sprites[variante], (c * TAILLE, r * TAILLE))

    def case_libre(self, wr, wc):
        # Vrai si la case (wr, wc) de la fenetre est de l'herbe visible : marge, ou case de mur
        # qui ne touche pas le sol (donc non dessinee). On peut y poser du decor.
        grille = self.etat.grid
        r = wr - MARGE
        c = wc - MARGE
        if r < 0 or r >= len(grille) or c < 0 or c >= len(grille[r]):
            return True
        return grille[r][c] == "O" and not self.touche_le_sol(r, c)

    def dessiner_decor(self, lignes, colonnes):
        # Decor pose sur les cases d'herbe libres, partout autour et dans les creux du niveau.
        # Le choix de l'objet depend seulement de la position (pas de hasard : le rendu est toujours le meme).
        # Les objets hauts (arbre, statue, totem) ont leur pied dans la case et montent vers le haut :
        # on verifie que les cases au-dessus sont libres aussi.
        s = self.sprites
        objets = ["arbre", "statue", "lanterne", "vase", "buisson", "tonneau", "coffre", "totem", "panneau", "tombe", "arbre2", "banc"]
        for wr in range(1, lignes - 1):
            for wc in range(1, colonnes - 1):
                if not self.case_libre(wr, wc):
                    continue
                if (wr * 13 + wc * 7) % 3 != 0:
                    continue
                nom = objets[(wr * 5 + wc * 9) % len(objets)]
                if nom == "arbre" or nom == "arbre2":
                    # Un arbre est large : il lui faut aussi la case de droite et celles du dessus.
                    if not (self.case_libre(wr - 1, wc) and self.case_libre(wr, wc + 1) and self.case_libre(wr - 1, wc + 1)):
                        continue
                if nom == "statue" or nom == "totem":
                    if not self.case_libre(wr - 1, wc):
                        continue
                image = s[nom]
                x = wc * TAILLE + (TAILLE - image.get_width()) // 2
                y = (wr + 1) * TAILLE - image.get_height()
                self.ecran.blit(image, (x, y))

    def draw(self):
        grille = self.etat.grid
        largeur, hauteur = self.ecran.get_size()

        # Fond : de l'herbe partout (avec quelques fleurs), meme dans la marge.
        for r in range(hauteur // TAILLE):
            for c in range(largeur // TAILLE):
                if (r * 5 + c * 3) % 9 == 0:
                    self.ecran.blit(self.sprites["herbe_fleurs"], (c * TAILLE, r * TAILLE))
                else:
                    self.ecran.blit(self.sprites["herbe"], (c * TAILLE, r * TAILLE))

        self.dessiner_haie(largeur, hauteur)
        self.dessiner_decor(hauteur // TAILLE, largeur // TAILLE)

        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                x = (c + MARGE) * TAILLE
                y = (r + MARGE) * TAILLE

                if case == "O":
                    if self.touche_le_sol(r, c):
                        self.ecran.blit(self.sprites["mur" + str(1 + (r + c) % 2)], (x, y))
                    continue

                # Toutes les autres cases sont du sol de jeu (dalle de pierre) ; l'herbe reste a l'exterieur.
                self.ecran.blit(self.sprites["sol" + str(1 + (r * 3 + c * 5) % 2)], (x, y))
                if case == "S" or case == "." or case == "*":
                    self.dessiner_cible(x, y)
                if case == "B" or case == "*":
                    self.ecran.blit(self.sprites["caisse"], (x, y))
                if case == "R" or case == ".":
                    self.ecran.blit(self.sprites["joueur"], (x, y))

        pygame.display.flip()
