# Interface Pygame du jeu.
# Etape 6  : rendu d'un niveau.
# Etape 7  : jeu manuel (fleches du clavier), compteur de coups, recommencer.
# Etape 7c : quand toutes les caisses sont sur les cibles, la porte s'ouvre et s'illumine,
#            une pancarte "Bravo" glisse dans l'ecran, puis l'ecran glisse vers le niveau suivant.
# Etape 8  : bouton "Resoudre (BFS)" qui affiche le cout, le nombre de pas et le temps de calcul.
# Les etapes 9 (simulation de la solution) et 7b (menu) viendront ensuite.

import math
import time
import pygame

from levels import LEVELS
from sokoban import SokobanPuzzle
from search import BFS
from assets_loader import load_sprites

TAILLE = 48            # taille d'une case en pixels
MARGE = 2              # marge autour du plus grand niveau, en nombre de cases (sert de decor)
HAUTEUR_BARRE = 132    # hauteur de la barre d'infos en bas de la fenetre, en pixels
COULEUR_FOND_CIBLE = (60, 50, 20)
COULEUR_CIBLE = (235, 215, 90)

# Touche du clavier -> nom de l'action de successorFunction.
TOUCHES = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}

# Durees des phases de fin de niveau, en millisecondes.
DUREE_OUVERTURE = 2000
DUREE_BRAVO = 2000
DUREE_GLISSE = 900


class Game:

    def __init__(self, numero=0):
        # numero : position du niveau dans LEVELS (0 = Exemple 1).
        pygame.init()

        # La zone de jeu a toujours la meme taille : celle du plus grand niveau + la marge.
        # Les niveaux plus petits sont centres dedans.
        self.colonnes_max = 0
        self.lignes_max = 0
        for niveau in LEVELS:
            self.lignes_max = max(self.lignes_max, len(niveau["grid"]))
            self.colonnes_max = max(self.colonnes_max, len(niveau["grid"][0]))
        self.cases_largeur = self.colonnes_max + 2 * MARGE
        self.cases_hauteur = self.lignes_max + 2 * MARGE
        largeur = self.cases_largeur * TAILLE
        hauteur = self.cases_hauteur * TAILLE

        # La fenetre = la zone de jeu + la barre d'infos en dessous.
        self.ecran = pygame.display.set_mode((largeur, hauteur + HAUTEUR_BARRE))

        # Les sprites se chargent apres set_mode.
        self.sprites = load_sprites(TAILLE)
        self.polices = {}     # polices deja creees, rangees par taille (voir ecrire)

        # Les deux boutons de la barre d'infos (rectangles cliquables).
        self.bouton_resoudre = pygame.Rect(14, hauteur + 66, 230, 38)
        self.bouton_recommencer = pygame.Rect(260, hauteur + 66, 230, 38)

        # Le niveau est dessine sur "monde", puis recopie sur l'ecran (pratique pour faire glisser).
        self.monde = pygame.Surface((largeur, hauteur))
        self.ancien_monde = None
        self.charger_niveau(numero)

        self.horloge = pygame.time.Clock()
        self.en_cours = True

    def charger_niveau(self, numero):
        self.numero = numero
        self.niveau = LEVELS[numero]
        self.etat = SokobanPuzzle(self.niveau["grid"])
        self.porte = self.trouver_porte()
        # Position du coin haut gauche du niveau dans la zone de jeu, en cases (niveau centre).
        self.decalage_colonne = (self.cases_largeur - len(self.etat.grid[0])) // 2
        self.decalage_ligne = (self.cases_hauteur - len(self.etat.grid)) // 2
        # Phase : "jeu", "ouverture" (porte + lumiere), "bravo" (pancarte), "glisse" (vers le niveau suivant).
        self.phase = "jeu"
        self.debut_phase = 0
        self.coups = 0          # nombre de deplacements faits a la main
        self.resultat = ""      # texte du dernier calcul BFS (vide tant qu'on n'a pas clique sur Resoudre)
        self.solution = None    # liste d'actions trouvee par le BFS (servira a la simulation, etape 9)
        pygame.display.set_caption("Sokoban - " + self.niveau["name"])

    def ecrire(self, texte, taille, couleur):
        # Texte "jeu 2D pixel" : on ecrit en petit sans lissage, puis on agrandit x2 sans lissage.
        # Si la premiere police n'existe pas sur l'ordinateur, pygame essaie les suivantes.
        if taille not in self.polices:
            self.polices[taille] = pygame.font.SysFont("lucidaconsole,consolas,couriernew", taille // 2, bold=True)
        petit = self.polices[taille].render(texte, False, couleur)
        return pygame.transform.scale(petit, (petit.get_width() * 2, petit.get_height() * 2))

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
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_cours = False
                if evenement.key == pygame.K_r:
                    self.charger_niveau(self.numero)
                if evenement.key == pygame.K_b and self.phase == "jeu":
                    self.resoudre()
                if evenement.key in TOUCHES and self.phase == "jeu":
                    self.bouger(TOUCHES[evenement.key])
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                if self.bouton_recommencer.collidepoint(evenement.pos):
                    self.charger_niveau(self.numero)
                if self.bouton_resoudre.collidepoint(evenement.pos) and self.phase == "jeu":
                    self.resoudre()

    def bouger(self, action):
        # Deplacement a la main. On ne re-ecrit AUCUNE regle ici : on demande a successorFunction
        # la liste des coups possibles et on prend celui qui correspond a la touche.
        # Si le coup n'y est pas (mur, caisse bloquee...), on ne fait rien.
        for nom, suivant in self.etat.successorFunction():
            if nom == action:
                self.etat = suivant
                self.coups = self.coups + 1
                self.resultat = ""
                self.solution = None
                return

    def resoudre(self):
        # Lance le BFS depuis la position actuelle et mesure le temps de calcul.
        debut = time.time()
        noeud = BFS(self.etat, lambda s: s.successorFunction(), lambda s: s.isGoal())
        duree = time.time() - debut
        if noeud is None:
            self.solution = None
            self.resultat = "BFS : aucune solution depuis cette position"
        else:
            self.solution = noeud.getSolution()
            self.resultat = "BFS : cout " + str(noeud.g) + " | " + str(len(self.solution)) + " pas | " + "%.3f" % duree + " s"

    def changer_phase(self, phase):
        self.phase = phase
        self.debut_phase = pygame.time.get_ticks()

    def update(self):
        # Enchaine les phases de fin de niveau. isGoal() est la seule chose qui decide de la victoire.
        ecoule = pygame.time.get_ticks() - self.debut_phase
        if self.phase == "jeu":
            if self.etat.isGoal():
                self.changer_phase("ouverture")
        elif self.phase == "ouverture":
            if ecoule >= DUREE_OUVERTURE:
                self.changer_phase("bravo")
        elif self.phase == "bravo":
            if ecoule >= DUREE_BRAVO:
                # On garde une copie de l'image du niveau fini, puis on charge le suivant.
                self.ancien_monde = self.monde.copy()
                self.charger_niveau((self.numero + 1) % len(LEVELS))
                self.changer_phase("glisse")
                self.dessiner_niveau()
        elif self.phase == "glisse":
            if ecoule >= DUREE_GLISSE:
                self.phase = "jeu"
                self.ancien_monde = None

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

    def trouver_porte(self):
        # La porte de sortie est posee sur un mur visible du haut du niveau, avec du sol juste en dessous
        # (de preference au milieu). Retourne (ligne, colonne) ou None. C'est seulement un dessin :
        # la case reste un mur, les regles du jeu ne changent pas.
        grille = self.etat.grid
        milieu = len(grille[0]) // 2
        meilleure = None
        for r in range(len(grille) - 1):
            for c in range(len(grille[r])):
                if grille[r][c] == "O" and self.touche_le_sol(r, c) and grille[r + 1][c] != "O":
                    if meilleure is None or r < meilleure[0] or (r == meilleure[0] and abs(c - milieu) < abs(meilleure[1] - milieu)):
                        meilleure = (r, c)
        return meilleure

    def case_libre(self, wr, wc):
        # Vrai si la case (wr, wc) de la zone de jeu est de l'herbe visible : hors du niveau, ou case de mur
        # qui ne touche pas le sol (donc non dessinee). On peut y poser du decor.
        grille = self.etat.grid
        r = wr - self.decalage_ligne
        c = wc - self.decalage_colonne
        if r < 0 or r >= len(grille) or c < 0 or c >= len(grille[r]):
            return True
        return grille[r][c] == "O" and not self.touche_le_sol(r, c)

    def dessiner_cible(self, x, y):
        # Croix jaune dans un anneau au centre de la case (la cible n'a pas de sprite dans le pack).
        # On la dessine d'abord en sombre et plus epaisse pour qu'elle ressorte sur le sol.
        petit = TAILLE // 4
        centre_x = x + TAILLE // 2
        centre_y = y + TAILLE // 2
        pygame.draw.circle(self.monde, COULEUR_CIBLE, (centre_x, centre_y), TAILLE // 2 - 6, 2)
        for (couleur, epaisseur) in [(COULEUR_FOND_CIBLE, 8), (COULEUR_CIBLE, 4)]:
            pygame.draw.line(self.monde, couleur, (centre_x - petit, centre_y - petit), (centre_x + petit, centre_y + petit), epaisseur)
            pygame.draw.line(self.monde, couleur, (centre_x - petit, centre_y + petit), (centre_x + petit, centre_y - petit), epaisseur)

    def dessiner_haie(self):
        # Rangee de buissons sur tout le bord de la zone de jeu (il en manque un de temps en temps).
        for r in range(self.cases_hauteur):
            for c in range(self.cases_largeur):
                sur_le_bord = r == 0 or c == 0 or r == self.cases_hauteur - 1 or c == self.cases_largeur - 1
                if sur_le_bord and (r * 7 + c * 13) % 4 != 0:
                    variante = ["buisson", "buisson2"][(r + c) % 2]
                    self.monde.blit(self.sprites[variante], (c * TAILLE, r * TAILLE))

    def dessiner_decor(self):
        # Decor pose sur les cases d'herbe libres, partout autour et dans les creux du niveau.
        # Le choix de l'objet depend seulement de la position (pas de hasard : le rendu est toujours le meme).
        # Les objets hauts (statue, totem...) ont leur pied dans la case et montent vers le haut :
        # on verifie que la case au-dessus est libre aussi.
        s = self.sprites
        objets = ["statue", "lanterne", "vase", "buisson", "tonneau", "coffre", "totem", "panneau", "tombe", "banc",
                  "buisson2", "vase2", "stele", "banc2", "tombe2", "totem2", "rocher", "vase3", "coffre2", "panneau2",
                  "stele2", "stele3", "tombe3", "tombe4", "sarcophage", "dalle_haute", "dalle_haute2", "ruine",
                  "caisses", "caisse_petite", "arche", "arche2", "escalier", "escalier2"]
        for wr in range(1, self.cases_hauteur - 1):
            for wc in range(1, self.cases_largeur - 1):
                if not self.case_libre(wr, wc):
                    continue
                if (wr * 13 + wc * 7) % 3 != 0:
                    continue
                nom = objets[(wr * 5 + wc * 9) % len(objets)]
                image = s[nom]
                if image.get_height() > TAILLE and not self.case_libre(wr - 1, wc):
                    continue
                x = wc * TAILLE + (TAILLE - image.get_width()) // 2
                y = (wr + 1) * TAILLE - image.get_height()
                self.monde.blit(image, (x, y))

    def position_porte(self):
        # Coin haut gauche du dessin de la porte (posee sur le bas de sa case de mur) et son sprite.
        sprite = self.sprites["porte"]
        if self.phase == "ouverture" or self.phase == "bravo":
            sprite = self.sprites["porte_ouverte"]
        x = (self.porte[1] + self.decalage_colonne) * TAILLE + (TAILLE - sprite.get_width()) // 2
        y = (self.porte[0] + self.decalage_ligne + 1) * TAILLE - sprite.get_height()
        return sprite, x, y

    def dessiner_niveau(self):
        # Dessine tout le niveau sur self.monde : herbe, haie, decor, murs, sol, cibles, caisses, chat, porte.
        grille = self.etat.grid

        # Fond : de l'herbe partout (avec quelques fleurs et touffes).
        for r in range(self.cases_hauteur):
            for c in range(self.cases_largeur):
                if (r * 5 + c * 3) % 9 == 0:
                    self.monde.blit(self.sprites["herbe_fleurs"], (c * TAILLE, r * TAILLE))
                else:
                    self.monde.blit(self.sprites["herbe"], (c * TAILLE, r * TAILLE))
                if (r * 7 + c * 3) % 4 == 0:
                    touffe = self.sprites["touffe" + str((r + c) % 5)]
                    self.monde.blit(touffe, (c * TAILLE + TAILLE // 4, r * TAILLE + TAILLE // 2))

        self.dessiner_haie()
        self.dessiner_decor()

        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                x = (c + self.decalage_colonne) * TAILLE
                y = (r + self.decalage_ligne) * TAILLE

                if case == "O":
                    if self.touche_le_sol(r, c):
                        self.monde.blit(self.sprites["mur" + str(1 + (r + c) % 2)], (x, y))
                    continue

                # Toutes les autres cases sont du sol de jeu (dalle de pierre) ; l'herbe reste a l'exterieur.
                self.monde.blit(self.sprites["sol" + str(1 + (r * 3 + c * 5) % 2)], (x, y))
                if case == "S" or case == "." or case == "*":
                    self.dessiner_cible(x, y)
                if case == "B" or case == "*":
                    self.monde.blit(self.sprites["caisse"], (x, y))
                if case == "R" or case == ".":
                    # Le chat est plus haut qu'une case : on aligne ses pieds sur le bas de la case.
                    chat = self.sprites["joueur"]
                    self.monde.blit(chat, (x + (TAILLE - chat.get_width()) // 2, y + TAILLE - chat.get_height()))

        # Porte de sortie, dessinee par-dessus le mur choisi (fermee, puis ouverte avec de la lumiere derriere).
        if self.porte is not None:
            sprite, x, y = self.position_porte()
            # L'arche en pierre est toujours autour de la porte (posee sur le bas de la case du mur).
            arche = self.sprites["arche_porte"]
            arche_x = (self.porte[1] + self.decalage_colonne) * TAILLE + (TAILLE - arche.get_width()) // 2
            arche_y = (self.porte[0] + self.decalage_ligne + 1) * TAILLE - arche.get_height()
            self.monde.blit(arche, (arche_x, arche_y))
            if self.phase == "ouverture" or self.phase == "bravo":
                pygame.draw.rect(self.monde, (255, 245, 190), (x + 4, y + 8, sprite.get_width() - 8, sprite.get_height() - 8))
            self.monde.blit(sprite, (x, y))

    def dessiner_lumiere(self, ecoule):
        # Lumiere doree qui sort de la porte ouverte : un faisceau vers le bas et un halo qui pulse.
        # Elle grandit pendant la premiere seconde puis reste allumee.
        sprite, x, y = self.position_porte()
        centre_x = x + sprite.get_width() // 2
        centre_y = y + sprite.get_height() // 2
        force = min(1.0, ecoule / 1000.0)
        pulsation = 1.0 + 0.08 * math.sin(ecoule / 150.0)
        lumiere = pygame.Surface(self.monde.get_size(), pygame.SRCALPHA)

        # Faisceau : un trapeze qui s'elargit vers le bas.
        bas = y + sprite.get_height()
        longueur = int(TAILLE * 3 * force)
        pygame.draw.polygon(lumiere, (255, 240, 150, 90),
                            [(x + 6, bas), (x + sprite.get_width() - 6, bas),
                             (x + sprite.get_width() + TAILLE // 2, bas + longueur), (x - TAILLE // 2, bas + longueur)])

        # Halo : cercles de plus en plus grands et de plus en plus transparents.
        for k in range(6):
            rayon = int((TAILLE * 2.2) * force * pulsation * (k + 1) / 6)
            pygame.draw.circle(lumiere, (255, 240, 150, 40), (centre_x, centre_y), rayon)
        self.ecran.blit(lumiere, (0, 0))

    def dessiner_pancarte(self, ecoule):
        # Pancarte en bois "Bravo" qui descend du haut de l'ecran jusqu'au milieu de la zone de jeu.
        largeur = 380
        hauteur = 130
        progression = min(1.0, ecoule / 600.0)
        progression = 1 - (1 - progression) * (1 - progression)      # ralentit a l'arrivee
        cible_y = self.monde.get_height() // 2 - hauteur // 2
        x = self.monde.get_width() // 2 - largeur // 2
        y = int(-hauteur - 40 + (cible_y + hauteur + 40) * progression)

        # Deux poteaux, puis la planche avec son contour et ses veines.
        pygame.draw.rect(self.ecran, (95, 60, 30), (x + 40, y + hauteur - 10, 24, 50))
        pygame.draw.rect(self.ecran, (95, 60, 30), (x + largeur - 64, y + hauteur - 10, 24, 50))
        pygame.draw.rect(self.ecran, (150, 100, 52), (x, y, largeur, hauteur), 0, 10)
        pygame.draw.rect(self.ecran, (85, 52, 25), (x, y, largeur, hauteur), 5, 10)
        for k in range(1, 4):
            pygame.draw.line(self.ecran, (125, 80, 40), (x + 8, y + k * hauteur // 4), (x + largeur - 8, y + k * hauteur // 4), 2)

        titre = self.ecrire("BRAVO !", 56, (255, 240, 200))
        texte = self.ecrire("Niveau suivant...", 24, (255, 240, 200))
        self.ecran.blit(titre, (x + (largeur - titre.get_width()) // 2, y + 14))
        self.ecran.blit(texte, (x + (largeur - texte.get_width()) // 2, y + 82))

    def dessiner_bouton(self, rectangle, texte):
        pygame.draw.rect(self.ecran, (150, 100, 52), rectangle, 0, 8)
        pygame.draw.rect(self.ecran, (230, 200, 130), rectangle, 3, 8)
        image = self.ecrire(texte, 16, (255, 245, 215))
        self.ecran.blit(image, (rectangle.x + (rectangle.width - image.get_width()) // 2, rectangle.y + (rectangle.height - image.get_height()) // 2))

    def dessiner_barre(self):
        # Barre d'infos en bas : niveau, coups, resultat du BFS, boutons et rappel des touches.
        haut = self.monde.get_height()
        largeur = self.ecran.get_width()
        pygame.draw.rect(self.ecran, (70, 45, 25), (0, haut, largeur, HAUTEUR_BARRE))
        pygame.draw.line(self.ecran, (230, 200, 130), (0, haut), (largeur, haut), 3)

        titre = self.niveau["name"] + "  -  Coups : " + str(self.coups)
        self.ecran.blit(self.ecrire(titre, 18, (255, 245, 215)), (14, haut + 8))
        self.ecran.blit(self.ecrire(self.resultat, 18, (255, 225, 120)), (14, haut + 36))
        aide = "Fleches : bouger   R : recommencer   B : resoudre   Echap : quitter"
        self.ecran.blit(self.ecrire(aide, 14, (220, 200, 170)), (14, haut + 110))

        self.dessiner_bouton(self.bouton_resoudre, "Resoudre (BFS)")
        self.dessiner_bouton(self.bouton_recommencer, "Recommencer")

    def draw(self):
        ecoule = pygame.time.get_ticks() - self.debut_phase
        if self.phase != "glisse":
            self.dessiner_niveau()

        if self.phase == "glisse":
            # L'ancien niveau sort a gauche pendant que le nouveau entre par la droite.
            progression = min(1.0, ecoule / float(DUREE_GLISSE))
            decalage = int(progression * self.monde.get_width())
            self.ecran.blit(self.ancien_monde, (-decalage, 0))
            self.ecran.blit(self.monde, (self.monde.get_width() - decalage, 0))
        else:
            self.ecran.blit(self.monde, (0, 0))

        if self.phase == "ouverture" or self.phase == "bravo":
            temps_lumiere = ecoule
            if self.phase == "bravo":
                temps_lumiere = ecoule + DUREE_OUVERTURE
            self.dessiner_lumiere(temps_lumiere)
        if self.phase == "bravo":
            self.dessiner_pancarte(ecoule)

        self.dessiner_barre()
        pygame.display.flip()
