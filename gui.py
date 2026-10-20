# Interface Pygame du jeu.
# Etape 6  : rendu d'un niveau.
# Etape 7  : jeu manuel (fleches du clavier), compteur de coups, recommencer.
# Etape 10 : quand toutes les caisses sont sur les cibles, la porte s'ouvre et s'illumine,
#            une pancarte "Bravo" glisse dans l'ecran, puis l'ecran glisse vers le niveau suivant.
# Etape 8  : bouton "Resoudre (BFS)" qui affiche le cout, le nombre de pas et le temps de calcul.
# Etape 9  : apres le BFS, trajectoire tracee et lecture automatique de la solution.
# Etape 11 : menu de choix du niveau (au lancement, ou touche M / bouton "Menu").
# Etape 13 : sons crees par le code (ambiance de prairie, bruit de pas), touche S pour couper.

import math
import time
from collections import deque
import pygame

from levels import LEVELS
from sokoban import SokobanPuzzle
from search import BFS
from assets_loader import load_sprites, load_sounds

TAILLE = 44            # taille d'une case en pixels
MARGE = 2              # marge autour du plus grand niveau, en nombre de cases (sert de decor)
HAUTEUR_BARRE = 112    # hauteur de la barre d'infos en bas de la fenetre, en pixels
# Couleurs de la cible : plaque de pierre avec un contour dore (plus brillant quand une caisse est dessus).
COULEUR_PLAQUE = (120, 115, 105)
COULEUR_RUNE = (205, 150, 50)
COULEUR_RUNE_ALLUMEE = (255, 230, 110)
COULEUR_BON = (80, 210, 100)       # contour vert d'une caisse bien placee

# Touche du clavier -> nom de l'action de successorFunction.
TOUCHES = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}

# Durees des phases de fin de niveau, en millisecondes.
DUREE_OUVERTURE = 1200   # la porte s'ouvre, la lumiere apparait
DELAI_CASE = 170         # le chat marche jusqu'a la porte : temps pour traverser une case
DUREE_QUEUE = 1600       # le chat remue la queue devant la porte
DUREE_BRAVO = 2000       # la pancarte "Bravo"
DUREE_GLISSE = 900       # le glissement vers le niveau suivant

# La porte est ouverte (et la lumiere allumee) pendant toutes ces phases.
PHASES_PORTE_OUVERTE = ("ouverture", "marche", "queue", "bravo")

# Temps entre deux pas quand le programme joue la solution tout seul, en millisecondes.
DELAI_PAS = 350
COULEUR_TRAJET = (90, 210, 255)


class Game:

    def __init__(self, numero=0, menu=True):
        # numero : position du niveau dans LEVELS (0 = Exemple 1).
        # menu : vrai pour commencer par le menu de choix du niveau.
        # Son en mono, 22050 echantillons par seconde : suffisant, et les sons se calculent plus vite.
        pygame.mixer.pre_init(22050, -16, 1, 512)
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

        # Sons : dictionnaire vide si l'ordinateur n'a pas de carte son (le jeu marche quand meme).
        self.sons = load_sounds()
        self.son_actif = False
        self.changer_son()

        # Les trois boutons de la barre d'infos (rectangles cliquables).
        self.bouton_resoudre = pygame.Rect(14, hauteur + 52, 200, 34)
        self.bouton_recommencer = pygame.Rect(226, hauteur + 52, 190, 34)
        self.bouton_menu = pygame.Rect(428, hauteur + 52, 120, 34)

        # Boutons du menu : un par niveau, sur deux colonnes, au milieu de la zone de jeu.
        self.boutons_niveaux = []
        for i in range(len(LEVELS)):
            colonne = i % 2
            ligne = i // 2
            x = largeur // 2 - 250 + colonne * 260
            y = 200 + ligne * 64
            self.boutons_niveaux.append(pygame.Rect(x, y, 240, 50))

        # Le niveau est dessine sur "monde", puis recopie sur l'ecran (pratique pour faire glisser).
        self.monde = pygame.Surface((largeur, hauteur))
        self.ancien_monde = None
        self.charger_niveau(numero)
        if menu:
            self.ouvrir_menu()

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
        # Phase : "menu" (choix du niveau), "jeu", puis la fin de niveau : "ouverture" (porte + lumiere),
        # "marche" et "queue" (le chat va a la porte), "bravo" (pancarte), "glisse" (vers le niveau suivant).
        self.phase = "jeu"
        self.debut_phase = 0
        self.debut_victoire = 0    # moment ou la porte s'est ouverte (pour la lumiere)
        self.chemin_chat = []      # cases que le chat traverse pour aller a la porte
        self.coups = 0          # nombre de deplacements faits a la main
        self.annuler_solution()
        pygame.display.set_caption("Sokoban - Niveau " + str(numero + 1))

    def changer_son(self):
        # Allume ou coupe le son (touche S). L'ambiance tourne en boucle (loops=-1) tant que le son est allume.
        self.son_actif = not self.son_actif
        if "ambiance" in self.sons:
            if self.son_actif:
                self.sons["ambiance"].play(-1)
            else:
                self.sons["ambiance"].stop()

    def ouvrir_menu(self):
        # Retour au menu : on arrete la solution automatique et l'animation de fin de niveau.
        self.annuler_solution()
        self.ancien_monde = None
        self.phase = "menu"
        pygame.display.set_caption("Sokoban - Menu")

    def annuler_solution(self):
        # Efface la solution du BFS et arrete la lecture automatique.
        self.solution = None      # liste d'actions trouvee par le BFS
        self.trajectoire = []     # positions (ligne, colonne) du chat sur le chemin de la solution
        self.auto = False         # vrai pendant que le programme joue la solution tout seul
        self.pas_auto = 0         # nombre d'actions de la solution deja jouees
        self.dernier_pas = 0      # moment du dernier pas automatique (en ms)
        self.resultat = ""

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
            elif self.phase == "menu":
                self.evenement_menu(evenement)
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_cours = False
                if evenement.key == pygame.K_r:
                    self.charger_niveau(self.numero)
                if evenement.key == pygame.K_m:
                    self.ouvrir_menu()
                if evenement.key == pygame.K_s:
                    self.changer_son()
                if evenement.key == pygame.K_b and self.phase == "jeu":
                    self.resoudre()
                if evenement.key in TOUCHES and self.phase == "jeu":
                    # Jouer a la main arrete la solution automatique (la position change).
                    self.annuler_solution()
                    self.bouger(TOUCHES[evenement.key])
            elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                if self.bouton_recommencer.collidepoint(evenement.pos):
                    self.charger_niveau(self.numero)
                if self.bouton_resoudre.collidepoint(evenement.pos) and self.phase == "jeu":
                    self.resoudre()
                if self.bouton_menu.collidepoint(evenement.pos):
                    self.ouvrir_menu()

    def evenement_menu(self, evenement):
        # Dans le menu : clic sur un niveau, ou touche 1 a 8 ; Echap quitte le jeu.
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                self.en_cours = False
            if evenement.key == pygame.K_s:
                self.changer_son()
            if evenement.unicode.isdigit():
                numero = int(evenement.unicode) - 1
                if 0 <= numero < len(LEVELS):
                    self.charger_niveau(numero)
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            for i in range(len(self.boutons_niveaux)):
                if self.boutons_niveaux[i].collidepoint(evenement.pos):
                    self.charger_niveau(i)

    def bouger(self, action):
        # Deplacement a la main. On ne re-ecrit AUCUNE regle ici : on demande a successorFunction
        # la liste des coups possibles et on prend celui qui correspond a la touche.
        # Si le coup n'y est pas (mur, caisse bloquee...), on ne fait rien.
        for nom, suivant in self.etat.successorFunction():
            if nom == action:
                self.etat = suivant
                self.coups = self.coups + 1
                if self.son_actif and "pas" in self.sons:
                    self.sons["pas"].play()
                return

    def resoudre(self):
        # Lance le BFS depuis la position actuelle, mesure le temps de calcul, trace la trajectoire
        # du chat (positions de chaque etat du chemin) et demarre la lecture automatique.
        self.annuler_solution()
        debut = time.time()
        noeud = BFS(self.etat, lambda s: s.successorFunction(), lambda s: s.isGoal())
        duree = time.time() - debut
        if noeud is None:
            self.resultat = "BFS : aucune solution depuis cette position"
        else:
            self.solution = noeud.getSolution()
            self.trajectoire = [etat.player_pos for etat in noeud.getPath()]
            self.auto = True
            self.dernier_pas = pygame.time.get_ticks()
            self.resultat = "BFS : cout " + str(noeud.g) + " | " + str(len(self.solution)) + " pas | " + "%.3f" % duree + " s"

    def changer_phase(self, phase):
        self.phase = phase
        self.debut_phase = pygame.time.get_ticks()

    def update(self):
        # Enchaine les phases de fin de niveau. isGoal() est la seule chose qui decide de la victoire.
        ecoule = pygame.time.get_ticks() - self.debut_phase

        # Lecture automatique de la solution : un pas toutes les DELAI_PAS millisecondes.
        if self.auto and self.phase == "jeu":
            if pygame.time.get_ticks() - self.dernier_pas >= DELAI_PAS:
                if self.pas_auto < len(self.solution):
                    self.bouger(self.solution[self.pas_auto])
                    self.pas_auto = self.pas_auto + 1
                    self.dernier_pas = pygame.time.get_ticks()
                else:
                    self.auto = False

        if self.phase == "jeu":
            if self.etat.isGoal():
                self.debut_victoire = pygame.time.get_ticks()
                self.changer_phase("ouverture")
        elif self.phase == "ouverture":
            if ecoule >= DUREE_OUVERTURE:
                self.chemin_chat = self.chemin_vers_porte()
                self.changer_phase("marche")
        elif self.phase == "marche":
            if ecoule >= (len(self.chemin_chat) - 1) * DELAI_CASE:
                self.changer_phase("queue")
        elif self.phase == "queue":
            if ecoule >= DUREE_QUEUE:
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

    def chemin_vers_porte(self):
        # Chemin (liste de cases) du chat jusqu'a la case juste devant la porte, en evitant murs et caisses.
        # C'est un petit parcours en largeur sur les cases, pour l'animation seulement : ce n'est
        # pas un coup du jeu, donc ni les coups ni le cout du BFS ne changent.
        grille = self.etat.grid
        depart = self.etat.player_pos
        if self.porte is None:
            return [depart]
        arrivee = (self.porte[0] + 1, self.porte[1])

        parent = {depart: None}
        file = deque([depart])
        while len(file) > 0:
            r, c = file.popleft()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                voisine = (r + dr, c + dc)
                case = grille[voisine[0]][voisine[1]]
                if voisine not in parent and case != "O" and case != "B" and case != "*":
                    parent[voisine] = (r, c)
                    file.append(voisine)

        if arrivee not in parent:
            return [depart]          # porte inaccessible : le chat reste ou il est
        chemin = []
        case = arrivee
        while case is not None:
            chemin.append(case)
            case = parent[case]
        chemin.reverse()
        return chemin

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

    def dessiner_cible(self, x, y, allumee):
        # La cible est une plaque de pierre carree avec un contour dore (dessinee avec pygame.draw,
        # il n'y a pas de sprite pour ca dans le pack). Le contour brille quand une caisse est dessus.
        plaque = pygame.Rect(x + 4, y + 4, TAILLE - 8, TAILLE - 8)
        pygame.draw.rect(self.monde, COULEUR_PLAQUE, plaque, 0, 6)
        couleur = COULEUR_RUNE
        if allumee:
            couleur = COULEUR_RUNE_ALLUMEE
        pygame.draw.rect(self.monde, couleur, plaque, 4, 6)

    def dessiner_haie(self):
        # Rangee de buissons sur tout le bord de la zone de jeu (il en manque un de temps en temps).
        for r in range(self.cases_hauteur):
            for c in range(self.cases_largeur):
                sur_le_bord = r == 0 or c == 0 or r == self.cases_hauteur - 1 or c == self.cases_largeur - 1
                if sur_le_bord and (r * 7 + c * 13) % 4 != 0:
                    variante = ["buisson", "buisson2"][(r + c) % 2]
                    self.monde.blit(self.sprites[variante], (c * TAILLE, r * TAILLE))

    def mur_visible(self, r, c):
        # Vrai si (r, c) est un mur du niveau qu'on voit a l'ecran (dans la grille, et qui touche du sol).
        grille = self.etat.grid
        if r < 0 or r >= len(grille) or c < 0 or c >= len(grille[r]):
            return False
        return grille[r][c] == "O" and self.touche_le_sol(r, c)

    def poser(self, nom, wr, wc):
        # Pose un objet du decor dans la case (wr, wc) de la zone de jeu, les pieds en bas de la case.
        # On ne pose rien si la case est occupee (ou, pour un objet haut, si la case au-dessus l'est).
        image = self.sprites[nom]
        if not self.case_libre(wr, wc):
            return
        if image.get_height() > TAILLE and not self.case_libre(wr - 1, wc):
            return
        x = wc * TAILLE + (TAILLE - image.get_width()) // 2
        y = (wr + 1) * TAILLE - image.get_height()
        self.monde.blit(image, (x, y))

    def dessiner_decor(self):
        # Decor identique dans tous les niveaux : quelques caisses, 3 tombes alignees,
        # 3 tonneaux groupes dans un coin et 2 totems contre le mur, de chaque cote de la porte.

        # Caisses de decor : positions donnees par une formule (pas de hasard, le rendu est toujours le meme).
        for wr in range(1, self.cases_hauteur - 1):
            for wc in range(1, self.cases_largeur - 1):
                if (wr * 13 + wc * 7) % 3 == 0:
                    numero = (wr * 5 + wc * 9) % 30
                    if numero == 28:
                        self.poser("caisses", wr, wc)
                    if numero == 29:
                        self.poser("caisse_petite", wr, wc)

        # Les tombes et les tonneaux sont poses juste sous le niveau (et pas dans les coins de la fenetre),
        # pour que les petits niveaux ne soient pas perdus au milieu de l'herbe.
        grille = self.etat.grid
        bas = min(self.decalage_ligne + len(grille), self.cases_hauteur - 2)
        gauche = self.decalage_colonne
        droite = self.decalage_colonne + len(grille[0]) - 1

        # Trois tombes alignees sous le coin bas gauche du niveau.
        for k in range(3):
            self.poser("tombe", bas, gauche + k)

        # Trois tonneaux groupes sous le coin bas droit du niveau.
        self.poser("tonneau", bas, droite)
        self.poser("tonneau", bas, droite - 1)
        self.poser("tonneau", bas - 1, droite + 1)

        # Deux totems poses sur le mur du haut, de chaque cote de la porte (jamais dans le vide).
        # On essaie a 3 cases de la porte, sinon a 2 cases (niveaux etroits).
        if self.porte is not None:
            for sens in (-1, 1):
                for distance in (3, 2):
                    colonne = self.porte[1] + sens * distance
                    if self.mur_visible(self.porte[0], colonne):
                        self.poser("totem", self.porte[0] + self.decalage_ligne - 1, colonne + self.decalage_colonne)
                        break

    def position_porte(self):
        # Coin haut gauche du dessin de la porte (posee sur le bas de sa case de mur) et son sprite.
        sprite = self.sprites["porte"]
        if self.phase in PHASES_PORTE_OUVERTE:
            sprite = self.sprites["porte_ouverte"]
        x = (self.porte[1] + self.decalage_colonne) * TAILLE + (TAILLE - sprite.get_width()) // 2
        y = (self.porte[0] + self.decalage_ligne + 1) * TAILLE - sprite.get_height()
        return sprite, x, y

    def dessiner_trajectoire(self):
        # Trace le chemin que le chat va suivre : une ligne bleue entre les centres des cases,
        # avec un point sur chaque case et un gros point a l'arrivee.
        # On ne dessine que ce qu'il reste a parcourir : le trait raccourcit pendant la lecture.
        reste = self.trajectoire[self.pas_auto:]
        points = []
        for (r, c) in reste:
            x = (c + self.decalage_colonne) * TAILLE + TAILLE // 2
            y = (r + self.decalage_ligne) * TAILLE + TAILLE // 2
            points.append((x, y))
        if len(points) >= 2:
            pygame.draw.lines(self.monde, COULEUR_TRAJET, False, points, 5)
            for point in points:
                pygame.draw.circle(self.monde, (255, 255, 255), point, 5)
            pygame.draw.circle(self.monde, COULEUR_TRAJET, points[-1], 10)
            pygame.draw.circle(self.monde, (255, 255, 255), points[-1], 10, 3)

    def dessiner_herbe(self):
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

    def dessiner_niveau(self):
        # Dessine tout le niveau sur self.monde : herbe, haie, decor, murs, sol, cibles, caisses, chat, porte.
        grille = self.etat.grid
        self.dessiner_herbe()
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
                    self.dessiner_cible(x, y, case == "*")

        # La trajectoire est dessinee sur le sol, sous les caisses et le chat.
        self.dessiner_trajectoire()

        # Caisses et chat par-dessus.
        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                x = (c + self.decalage_colonne) * TAILLE
                y = (r + self.decalage_ligne) * TAILLE
                if case == "B" or case == "*":
                    self.monde.blit(self.sprites["caisse"], (x, y))
                if case == "*":
                    # Caisse bien placee : contour vert autour de la case, pour la reperer de loin.
                    pygame.draw.rect(self.monde, COULEUR_BON, (x, y, TAILLE, TAILLE), 3, 6)
                # Pendant la marche vers la porte, le chat est dessine a part (voir plus bas).
                if (case == "R" or case == ".") and self.phase != "marche" and self.phase != "queue":
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
            if self.phase in PHASES_PORTE_OUVERTE:
                pygame.draw.rect(self.monde, (255, 245, 190), (x + 4, y + 8, sprite.get_width() - 8, sprite.get_height() - 8))
            self.monde.blit(sprite, (x, y))

        # Le chat qui marche vers la porte, puis remue la queue devant (par-dessus la porte et l'arche).
        if self.phase == "marche" or self.phase == "queue":
            self.dessiner_chat_sortie()

    def dessiner_chat_sortie(self):
        # Position du chat : il glisse d'une case a la suivante le long de self.chemin_chat.
        ecoule = pygame.time.get_ticks() - self.debut_phase
        chemin = self.chemin_chat
        rang = ecoule / float(DELAI_CASE)
        if self.phase == "queue" or rang > len(chemin) - 1:
            rang = len(chemin) - 1.0
        i = int(rang)
        suivante = min(i + 1, len(chemin) - 1)
        reste = rang - i
        ligne = chemin[i][0] + (chemin[suivante][0] - chemin[i][0]) * reste
        colonne = chemin[i][1] + (chemin[suivante][1] - chemin[i][1]) * reste

        # Image : la queue bouge de gauche a droite devant la porte, et le chat fait de petits sauts en marchant.
        image = self.sprites["joueur"]
        saut = 0
        if self.phase == "queue":
            image = self.sprites["joueur_queue" + str(1 + (ecoule // 150) % 2)]
        else:
            saut = int(abs(math.sin(ecoule / 90.0)) * 4)
        x = (colonne + self.decalage_colonne) * TAILLE + (TAILLE - image.get_width()) // 2
        y = (ligne + self.decalage_ligne) * TAILLE + TAILLE - image.get_height() - saut
        self.monde.blit(image, (int(x), int(y)))

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

    def dessiner_menu(self):
        # Menu : herbe et haie en fond, une grande planche en bois avec le titre et un bouton par niveau.
        self.dessiner_herbe()
        self.dessiner_haie()
        largeur = self.monde.get_width()
        planche = pygame.Rect(largeur // 2 - 280, 70, 560, 150 + 64 * ((len(LEVELS) + 1) // 2))
        pygame.draw.rect(self.monde, (150, 100, 52), planche, 0, 12)
        pygame.draw.rect(self.monde, (85, 52, 25), planche, 5, 12)
        titre = self.ecrire("SOKOBAN", 56, (255, 240, 200))
        texte = self.ecrire("Choisis un niveau", 24, (255, 240, 200))
        self.monde.blit(titre, (largeur // 2 - titre.get_width() // 2, 90))
        self.monde.blit(texte, (largeur // 2 - texte.get_width() // 2, 155))
        self.ecran.blit(self.monde, (0, 0))

        # Le bouton sous la souris est un peu plus clair.
        souris = pygame.mouse.get_pos()
        for i in range(len(LEVELS)):
            rectangle = self.boutons_niveaux[i]
            nom = str(i + 1) + " - " + LEVELS[i]["name"]
            self.dessiner_bouton(rectangle, nom, rectangle.collidepoint(souris))

    def dessiner_bouton(self, rectangle, texte, survole=False):
        couleur = (150, 100, 52)
        if survole:
            couleur = (185, 128, 70)
        pygame.draw.rect(self.ecran, couleur, rectangle, 0, 8)
        pygame.draw.rect(self.ecran, (230, 200, 130), rectangle, 3, 8)
        image = self.ecrire(texte, 16, (255, 245, 215))
        self.ecran.blit(image, (rectangle.x + (rectangle.width - image.get_width()) // 2, rectangle.y + (rectangle.height - image.get_height()) // 2))

    def dessiner_barre(self):
        # Barre d'infos en bas : niveau, coups, resultat du BFS, boutons et rappel des touches.
        haut = self.monde.get_height()
        largeur = self.ecran.get_width()
        pygame.draw.rect(self.ecran, (70, 45, 25), (0, haut, largeur, HAUTEUR_BARRE))
        pygame.draw.line(self.ecran, (230, 200, 130), (0, haut), (largeur, haut), 3)

        if self.phase == "menu":
            self.ecran.blit(self.ecrire("Menu", 18, (255, 245, 215)), (14, haut + 6))
            aide = "Clic sur un niveau ou touche 1 a " + str(len(LEVELS)) + "   S : son   Echap : quitter"
            self.ecran.blit(self.ecrire(aide, 14, (220, 200, 170)), (14, haut + 92))
            return

        titre = "Niveau " + str(self.numero + 1) + "  -  Coups : " + str(self.coups)
        self.ecran.blit(self.ecrire(titre, 18, (255, 245, 215)), (14, haut + 6))
        self.ecran.blit(self.ecrire(self.resultat, 18, (255, 225, 120)), (14, haut + 28))
        aide = "Fleches: bouger  R: recommencer  B: BFS  M: menu  S: son  Echap: quitter"
        self.ecran.blit(self.ecrire(aide, 14, (220, 200, 170)), (14, haut + 92))

        self.dessiner_bouton(self.bouton_resoudre, "Resoudre (BFS)")
        self.dessiner_bouton(self.bouton_recommencer, "Recommencer")
        self.dessiner_bouton(self.bouton_menu, "Menu")

    def draw(self):
        ecoule = pygame.time.get_ticks() - self.debut_phase
        if self.phase == "menu":
            self.dessiner_menu()
            self.dessiner_barre()
            pygame.display.flip()
            return

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

        if self.phase in PHASES_PORTE_OUVERTE:
            # La lumiere reste allumee depuis le moment de la victoire.
            self.dessiner_lumiere(pygame.time.get_ticks() - self.debut_victoire)
        if self.phase == "bravo":
            self.dessiner_pancarte(ecoule)

        self.dessiner_barre()
        pygame.display.flip()
