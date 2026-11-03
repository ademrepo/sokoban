# Interface Pygame du jeu (classe Game).
# - ecran d'accueil (Jouer, Comparer tous les niveaux, Quitter) ;
# - menu de choix du niveau, avec un apercu de chaque niveau (au lancement, ou touche M / bouton "Menu") ;
# - rendu d'un niveau avec les sprites du pack, decor autour et effets (lucioles, etincelles) ;
# - jeu manuel : le chat et les caisses glissent d'une case a l'autre, compteur de coups,
#   annuler (Z), recommencer ;
# - boutons BFS, A* h1, A* h2, A* h3 (et bouton Deadlock : A* sans les etats perdus) : cout, steps et temps de calcul, puis trajectoire
#   tracee et lecture automatique de la solution
#   (pause, vitesse reglable) ;
# - bouton "Comparer" : lance les 4 algorithmes et affiche leur cout, leurs steps et leur temps ;
# - fin de niveau : la porte s'ouvre et s'illumine, le chat va devant la porte et remue la queue,
#   une pancarte "Bravo" descend avec ses boutons (Rejouer, Niveau suivant, Menu) ;
# - sons crees par le code (ambiance de prairie, bruit de pas), touche S pour couper.

import math
import random
from collections import deque
import pygame

from levels import LEVELS
from sokoban import SokobanPuzzle, ACTIONS
from astar import h1, h2, h3
from solveur import resoudre
from assets_loader import load_sprites, load_sounds

TAILLE = 44            # taille d'une case en pixels
MARGE_X = 7            # marge a gauche et a droite du plus grand niveau, en cases (sert de decor)
MARGE_Y = 2            # marge en haut et en bas
HAUTEUR_BARRE = 140    # hauteur de la barre d'infos en bas de la fenetre, en pixels
# Couleurs de la cible : plaque de pierre avec un contour dore (plus brillant quand une caisse est dessus).
COULEUR_PLAQUE = (120, 115, 105)
COULEUR_CONTOUR = (205, 150, 50)
COULEUR_CONTOUR_ALLUME = (255, 230, 110)
COULEUR_BON = (80, 210, 100)       # contour vert d'une caisse bien placee

# Touche du clavier -> nom de l'action de successorFunction.
TOUCHES = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}

# Animation d'un deplacement, en millisecondes.
DUREE_MOUVEMENT = 140    # le chat (et la caisse poussee) glisse d'une case a la suivante

# Durees des phases de fin de niveau, en millisecondes.
DUREE_OUVERTURE = 1200   # la porte s'ouvre, la lumiere apparait
DELAI_CASE = 170         # le chat marche jusqu'a la porte : temps pour traverser une case
DUREE_QUEUE = 1600       # le chat remue la queue devant la porte
DUREE_PANCARTE = 600     # la pancarte "Bravo" descend (ensuite elle attend un clic sur un bouton)
HAUTEUR_SAUT = 40         # hauteur du chat quand il saute par-dessus une caisse, en pixels
DUREE_GLISSE = 900       # le glissement vers le niveau suivant

# La porte est ouverte (et la lumiere allumee) pendant toutes ces phases.
PHASES_PORTE_OUVERTE = ("ouverture", "marche", "queue", "bravo")

# Les algorithmes proposes : (nom, heuristique) ; None = pas d'heuristique, c'est le BFS.
ALGOS = [("BFS", None), ("A* h1", h1), ("A* h2", h2), ("A* h3", h3)]

# Colonnes du tableau de tous les niveaux : (nom, heuristique, avec elagage des deadlocks).
# "+DL" = A* qui ignore les etats deadlock (caisses perdues).
ALGOS_TOUS = [("BFS", None, False), ("A* h1", h1, False), ("A* h2", h2, False), ("A* h3", h3, False),
              ("h1+DL", h1, True), ("h2+DL", h2, True), ("h3+DL", h3, True)]
# Personnages au choix dans le menu : (nom affiche, cle).
PERSONNAGES = [("Jack", "jack"), ("Pingu", "pingu")]
COULEUR_DL = (140, 240, 150)       # vert : tout ce qui concerne la detection de deadlock
COULEUR_SANS_DL = (255, 200, 80)   # dore : sans detection

# Temps entre deux pas quand le programme joue la solution tout seul, en millisecondes (du plus lent au plus rapide).
# Les touches - et + changent de vitesse.
DELAIS_PAS = [700, 450, 260, 150, 80, 40]
VITESSE_DEPART = 2

# Menu : 4 colonnes de 3 cartes = 12 niveaux par page (les boutons < > servent s'il y en a plus).
COLONNES_MENU = 4
PAR_PAGE = 12
COULEUR_TRAJET = (90, 210, 255)

# Fondu (ecran qui apparait en douceur), messages et confettis.
DUREE_FONDU = 350
DUREE_MESSAGE = 1600
NOMBRE_CONFETTIS = 70
COULEURS_CONFETTIS = [(255, 90, 90), (255, 210, 70), (90, 200, 255), (120, 230, 120), (255, 150, 220)]
COULEUR_ETOILE = (255, 215, 70)
COULEUR_ETOILE_VIDE = (110, 80, 50)

# Effets du decor vivant.
NOMBRE_PETALES = 14      # petales de fleurs qui flottent dans l'air
NOMBRE_LUCIOLES = 18
DUREE_PARTICULE = 700    # duree de vie d'une etincelle ou d'un grain de poussiere, en millisecondes


def touche_le_sol(grille, r, c):
    # Vrai si un des 8 voisins de (r, c) n'est pas un mur.
    # Sert a ne dessiner que les murs du bord du labyrinthe (le reste = decor vert).
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < len(grille) and 0 <= nc < len(grille[nr]):
                if grille[nr][nc] != "O":
                    return True
    return False


def est_sol(grille, r, c):
    # Vrai si la case (r, c) est dans la grille et n'est pas un mur.
    return 0 <= r < len(grille) and 0 <= c < len(grille[r]) and grille[r][c] != "O"


def creer_halo(rayon, couleur, opacite):
    # Disque flou : opaque au centre (opacite entre 0 et 255), transparent au bord.
    # On dessine des cercles de plus en plus petits et de plus en plus opaques les uns sur les autres.
    image = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
    for k in range(rayon, 0, -1):
        alpha = int(opacite * (1 - k / float(rayon)))
        pygame.draw.circle(image, (couleur[0], couleur[1], couleur[2], alpha), (rayon, rayon), k)
    return image


def creer_vignette(largeur, hauteur):
    # Bords legerement assombris (comme au cinema) : des rectangles de plus en plus transparents vers le centre.
    image = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    for k in range(60):
        alpha = int(90 * (1 - k / 60.0) ** 2)
        pygame.draw.rect(image, (0, 0, 0, alpha), (k, k, largeur - 2 * k, hauteur - 2 * k), 1)
    return image


def dessiner_etoile(surface, x, y, rayon, couleur):
    # Etoile a 5 branches centree en (x, y) : 10 points, alternativement loin et pres du centre.
    points = []
    for k in range(10):
        angle = math.pi * k / 5 - math.pi / 2
        if k % 2 == 0:
            r = rayon
        else:
            r = rayon * 0.45
        points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
    pygame.draw.polygon(surface, couleur, points)
    pygame.draw.polygon(surface, (90, 55, 20), points, 2)


class Game:

    def __init__(self, numero=0, menu=True):
        # numero : position du niveau dans LEVELS (0 = Exemple 1).
        # menu : vrai pour commencer par le menu de choix du niveau.
        # Son en mono, 22050 echantillons par seconde : suffisant, et les sons se calculent plus vite.
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        # Fleche gardee appuyee : pygame renvoie la touche toute seule apres 250 ms, puis toutes les 140 ms
        # (le temps d'un pas), donc le chat continue d'avancer.
        pygame.key.set_repeat(250, DUREE_MOUVEMENT)

        # La zone de jeu a toujours la meme taille : celle du plus grand niveau + la marge.
        # Les niveaux plus petits sont centres dedans.
        colonnes_max = 0
        lignes_max = 0
        for niveau in LEVELS:
            lignes_max = max(lignes_max, len(niveau["grid"]))
            for ligne in niveau["grid"]:
                colonnes_max = max(colonnes_max, len(ligne))
        self.cases_largeur = colonnes_max + 2 * MARGE_X
        self.cases_hauteur = lignes_max + 2 * MARGE_Y
        largeur = self.cases_largeur * TAILLE
        hauteur = self.cases_hauteur * TAILLE

        # La fenetre = la zone de jeu + la barre d'infos en dessous.
        self.ecran = pygame.display.set_mode((largeur, hauteur + HAUTEUR_BARRE))

        # Les sprites se chargent apres set_mode.
        self.sprites = load_sprites(TAILLE)
        # Ellipse noire transparente, agrandie ou reduite pour faire les ombres au sol (voir dessiner_ombre).
        self.image_ombre = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image_ombre, (0, 0, 0, 70), (0, 0, 60, 20))

        # Effets du decor vivant (images preparees une seule fois).
        self.lueur = creer_halo(10, (255, 240, 140), 200)
        self.halo_cible = creer_halo(TAILLE, (255, 220, 90), 150)
        # Lucioles : position de depart, vitesse et decalage au hasard (graine fixe : toujours pareil).
        hasard = random.Random(5)
        self.lucioles = []
        for k in range(NOMBRE_LUCIOLES):
            self.lucioles.append((hasard.uniform(0, largeur), hasard.uniform(0, hauteur), hasard.uniform(0.6, 1.4), hasard.uniform(0, 6.28)))
        hasard_petales = random.Random(11)
        self.petales = []      # (x, y, vitesse en x, vitesse en y, decalage) de chaque petale
        for k in range(NOMBRE_PETALES):
            self.petales.append((hasard_petales.uniform(0, largeur), hasard_petales.uniform(0, hauteur),
                                 hasard_petales.uniform(12, 30), hasard_petales.uniform(10, 24), hasard_petales.uniform(0, 6.28)))
        self.polices = {}     # polices deja creees, rangees par taille (voir ecrire)
        self.vignette = creer_vignette(largeur, hauteur)
        self.etoiles = {}         # meilleur nombre d'etoiles par niveau (numero -> 0 a 3), garde pendant la session
        self.message = ""         # petit message qui apparait en haut (voir afficher_message)
        self.fin_message = 0
        self.debut_fondu = 0      # moment ou l'ecran actuel a commence a apparaitre
        self.debut_comparaison = 0
        self.personnage = "jack"     # "jack" (le chat) ou "pingu" (le pingouin), au choix dans le menu

        # Sons : dictionnaire vide si l'ordinateur n'a pas de carte son (le jeu marche quand meme).
        self.sons = load_sounds()
        self.son_actif = False
        self.changer_son()

        # Les boutons de la barre d'infos (rectangles cliquables), a droite du texte.
        # Premiere ligne : un bouton par algorithme, le bouton Deadlock (allume / eteint), puis "Comparer".
        self.boutons_algos = []
        for k in range(len(ALGOS)):
            self.boutons_algos.append(pygame.Rect(largeur - 630 + k * 86, hauteur + 24, 80, 38))
        self.bouton_deadlock = pygame.Rect(largeur - 630 + len(ALGOS) * 86 + 6, hauteur + 24, 150, 38)
        self.bouton_comparer = pygame.Rect(largeur - 124, hauteur + 24, 104, 38)
        # Deuxieme ligne : annuler, recommencer, menu, puis pause et vitesse de la lecture automatique.
        self.bouton_annuler = pygame.Rect(largeur - 536, hauteur + 76, 100, 38)
        self.bouton_recommencer = pygame.Rect(largeur - 430, hauteur + 76, 130, 38)
        self.bouton_menu = pygame.Rect(largeur - 294, hauteur + 76, 76, 38)
        self.bouton_pause = pygame.Rect(largeur - 212, hauteur + 76, 100, 38)
        self.bouton_moins = pygame.Rect(largeur - 106, hauteur + 76, 40, 38)
        self.bouton_plus = pygame.Rect(largeur - 60, hauteur + 76, 40, 38)
        self.deadlock = False         # vrai : les A* ignorent les etats deadlock
        self.comparaison = []         # lignes du tableau "Comparer" : listes de colonnes (vide = tableau cache)
        self.note_comparaison = ""    # phrase sous le tableau
        self.barres = []              # (steps sans, steps avec deadlock) de chaque ligne du tableau Comparer
        self.vitesse = VITESSE_DEPART # position dans DELAIS_PAS
        self.pause = False            # vrai : la lecture automatique est en pause
        self.algo_choisi = 0          # dernier algorithme lance (0 = BFS)
        self.tableau_global = []      # comparaison de tous les niveaux : (nom, cout, [steps], [temps])
        self.vue_globale = False      # vrai : le tableau de tous les niveaux est affiche
        self.vue_temps = False        # tableau global : colonnes de temps au lieu de steps

        # Cartes du menu : PAR_PAGE par page, sur COLONNES_MENU colonnes, au milieu de la zone de jeu.
        # La carte du niveau i est boutons_niveaux[i % PAR_PAGE] ; la page est choix_menu // PAR_PAGE.
        self.boutons_niveaux = []
        for i in range(PAR_PAGE):
            colonne = i % COLONNES_MENU
            ligne = i // COLONNES_MENU
            x = largeur // 2 - 446 + colonne * 226
            y = 140 + ligne * 106
            self.boutons_niveaux.append(pygame.Rect(x, y, 214, 96))
        self.choix_menu = 0     # carte selectionnee (souris ou fleches du clavier)
        self.bouton_page_avant = pygame.Rect(largeur // 2 + 180, hauteur - 58, 90, 34)
        self.bouton_page_apres = pygame.Rect(largeur // 2 + 370, hauteur - 58, 90, 34)
        # Choix du personnage : un bouton par personnage, en bas a gauche du menu.
        self.boutons_perso = []
        for k in range(len(PERSONNAGES)):
            self.boutons_perso.append(pygame.Rect(largeur // 2 - 290 + k * 160, hauteur - 66, 150, 48))

        # Ecran d'accueil : trois gros boutons.
        self.bouton_jouer = pygame.Rect(largeur // 2 - 150, 210, 300, 56)
        self.bouton_comparer_tout = pygame.Rect(largeur // 2 - 150, 282, 300, 56)
        self.bouton_quitter = pygame.Rect(largeur // 2 - 150, 354, 300, 56)
        # Tableau de tous les niveaux : boutons "Steps / Temps" et "Fermer".
        self.bouton_vue = pygame.Rect(largeur // 2 - 160, hauteur - 62, 150, 38)
        self.bouton_fermer = pygame.Rect(largeur // 2 + 10, hauteur - 62, 150, 38)

        # Pancarte "Bravo" (au milieu de la zone de jeu) et ses trois boutons, a leur place finale.
        centre_x = largeur // 2
        # La pancarte est a droite du niveau, pour qu'on voie le personnage sauter de joie devant la porte.
        self.pancarte = pygame.Rect(largeur - 318, hauteur // 2 - 160, 300, 310)
        self.bouton_rejouer = pygame.Rect(largeur - 288, hauteur // 2 + 5, 240, 40)
        self.bouton_suivant = pygame.Rect(largeur - 288, hauteur // 2 + 55, 240, 40)
        self.bouton_menu_bravo = pygame.Rect(largeur - 288, hauteur // 2 + 105, 240, 40)

        # Le niveau est dessine sur "monde", puis recopie sur l'ecran (pratique pour faire glisser).
        self.monde = pygame.Surface((largeur, hauteur))
        self.ancien_monde = None
        # Fond du menu (herbe et haie), dessine une seule fois.
        self.dessiner_herbe()
        self.dessiner_haie()
        self.fond_menu = self.monde.copy()
        self.charger_niveau(numero)
        if menu:
            self.ouvrir_accueil()

        self.horloge = pygame.time.Clock()
        self.en_cours = True

    def charger_niveau(self, numero):
        self.numero = numero
        self.niveau = LEVELS[numero]
        self.etat = SokobanPuzzle(self.niveau["grid"])
        self.porte = self.trouver_porte()
        # Position du coin haut gauche du niveau dans la zone de jeu, en cases (niveau centre).
        # Le niveau est centre au pixel pres : le decalage peut valoir une demi-case (ligne0 et colonne0 : partie entiere).
        self.decalage_colonne = (self.cases_largeur - len(self.etat.grid[0])) / 2.0
        self.decalage_ligne = (self.cases_hauteur - len(self.etat.grid)) / 2.0
        self.colonne0 = int(self.decalage_colonne)
        self.ligne0 = int(self.decalage_ligne)
        self.preparer_fond()
        # Phase : "menu" (choix du niveau), "jeu", puis la fin de niveau : "ouverture" (porte + lumiere),
        # "marche" et "queue" (le chat va a la porte), "bravo" (pancarte), "glisse" (vers le niveau suivant).
        self.phase = "jeu"
        self.debut_phase = 0
        self.debut_victoire = 0    # moment ou la porte s'est ouverte (pour la lumiere)
        self.debut_niveau = pygame.time.get_ticks()    # moment ou le niveau a commence (pour le temps de jeu)
        self.duree_niveau = 0      # temps de jeu en secondes, calcule a la victoire
        self.chemin_chat = []      # cases que le chat traverse pour aller a la porte
        self.debut_fondu = pygame.time.get_ticks()
        self.optimal = self.cout_optimal()     # nombre de coups minimal : l'objectif affiche et base des etoiles
        self.aide = False          # vrai si on a demande la solution a un algorithme (pas d'etoiles dans ce cas)
        self.nb_etoiles = 0
        self.confettis = []
        self.coups = 0          # nombre de deplacements faits (a la main ou par la lecture automatique)
        self.historique = []    # etats precedents, pour annuler un coup (touche Z)
        self.particules = []    # etincelles et poussiere : [x, y, vx, vy, naissance, couleur]

        # Animation du dernier deplacement : le chat glisse de anim_joueur[0] a anim_joueur[1],
        # et la caisse poussee (s'il y en a une) de anim_caisse[0] a anim_caisse[1].
        self.anim_debut = -DUREE_MOUVEMENT
        self.anim_joueur = None
        self.anim_caisse = None
        self.pop_caisse = None          # (case, moment) d'une caisse qui vient d'arriver sur une cible : elle fait "pop"
        self.dernier_rebond = -1        # numero du dernier rebond de joie (pour lancer les etincelles une fois par rebond)
        self.anim_direction = (0, 0)
        self.action_en_attente = None   # touche appuyee pendant une animation : jouee juste apres
        self.annuler_solution()
        pygame.display.set_caption("Sokoban - Niveau " + str(numero + 1))

    def cout_optimal(self):
        # Nombre de coups minimal du niveau, trouve par A* (avec elagage des deadlocks, tres rapide).
        noeud, steps, duree = resoudre(self.etat, h3, True)
        if noeud is None:
            return 0
        return noeud.g

    def calculer_etoiles(self):
        # 3 etoiles : autant de coups que le minimum ; 2 : au plus 50 % de plus ; 1 : le niveau est fini.
        # Pas d'etoile si c'est l'algorithme qui a joue la solution.
        if self.aide:
            return 0
        if self.coups <= self.optimal:
            return 3
        if self.coups <= self.optimal + self.optimal // 2:
            return 2
        return 1

    def afficher_message(self, texte):
        # Petit message en haut de la zone de jeu pendant DUREE_MESSAGE millisecondes.
        self.message = texte
        self.fin_message = pygame.time.get_ticks() + DUREE_MESSAGE

    def changer_son(self):
        # Allume ou coupe le son (touche S). L'ambiance tourne en boucle (loops=-1) tant que le son est allume.
        self.son_actif = not self.son_actif
        if "ambiance" in self.sons:
            if self.son_actif:
                self.sons["ambiance"].play(-1)
            else:
                self.sons["ambiance"].stop()

    def ouvrir_accueil(self):
        # Ecran d'accueil : titre et boutons Jouer / Comparer / Quitter.
        self.annuler_solution()
        self.ancien_monde = None
        self.debut_fondu = pygame.time.get_ticks()
        self.phase = "accueil"
        pygame.display.set_caption("Sokoban")

    def ouvrir_menu(self):
        # Retour au menu : on arrete la solution automatique et l'animation de fin de niveau.
        # La carte du niveau qu'on quitte est deja selectionnee.
        self.annuler_solution()
        self.ancien_monde = None
        self.choix_menu = self.numero
        self.debut_fondu = pygame.time.get_ticks()
        self.phase = "menu"
        pygame.display.set_caption("Sokoban - Menu")

    def annuler_solution(self):
        # Efface la solution trouvee et arrete la lecture automatique.
        self.solution = None      # liste d'actions trouvee par l'algorithme
        self.trajectoire = []     # positions (ligne, colonne) du chat sur le chemin de la solution
        self.auto = False         # vrai pendant que le programme joue la solution tout seul
        self.pause = False
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
            self.horloge.tick(60)      # 60 images par seconde : animations fluides
        pygame.quit()

    def handle_events(self):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False
            elif self.vue_globale:
                self.evenement_tableau_global(evenement)
            elif self.phase == "accueil":
                self.evenement_accueil(evenement)
            elif self.phase == "menu":
                self.evenement_menu(evenement)
            elif len(self.comparaison) > 0 and evenement.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.comparaison = []      # le tableau se ferme a la prochaine touche ou au prochain clic
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.ouvrir_menu()          # Echap = retour au menu
                if evenement.key == pygame.K_r:
                    self.charger_niveau(self.numero)
                    self.afficher_message("Niveau recommence")
                if evenement.key == pygame.K_m:
                    self.ouvrir_menu()
                if evenement.key == pygame.K_s:
                    self.changer_son()
                if evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_n) and self.phase == "bravo":
                    self.niveau_suivant()
                if self.phase == "jeu":
                    # B = BFS, 1 / 2 / 3 = A* avec h1 / h2 / h3, C = comparer les quatre.
                    if evenement.key == pygame.K_b:
                        self.resoudre(0)
                    if evenement.key == pygame.K_1:
                        self.resoudre(1)
                    if evenement.key == pygame.K_2:
                        self.resoudre(2)
                    if evenement.key == pygame.K_3:
                        self.resoudre(3)
                    if evenement.key == pygame.K_d:
                        self.changer_deadlock()
                    if evenement.key == pygame.K_c:
                        self.comparer()
                    if evenement.key in (pygame.K_p, pygame.K_SPACE):
                        self.pause = not self.pause
                    if evenement.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.changer_vitesse(1)
                    if evenement.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.changer_vitesse(-1)
                if evenement.key in (pygame.K_z, pygame.K_BACKSPACE) and self.phase == "jeu":
                    self.annuler_coup()
                if evenement.key in TOUCHES and self.phase == "jeu":
                    # Jouer a la main arrete la solution automatique (la position change).
                    self.annuler_solution()
                    if self.en_mouvement():
                        self.action_en_attente = TOUCHES[evenement.key]   # joue des que le pas en cours finit
                    else:
                        self.bouger(TOUCHES[evenement.key])
            elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                if self.bouton_recommencer.collidepoint(evenement.pos):
                    self.charger_niveau(self.numero)
                if self.phase == "jeu":
                    for k in range(len(ALGOS)):
                        if self.boutons_algos[k].collidepoint(evenement.pos):
                            self.resoudre(k)
                    if self.bouton_comparer.collidepoint(evenement.pos):
                        self.comparer()
                    if self.bouton_deadlock.collidepoint(evenement.pos):
                        self.changer_deadlock()
                    if self.bouton_pause.collidepoint(evenement.pos):
                        self.pause = not self.pause
                    if self.bouton_plus.collidepoint(evenement.pos):
                        self.changer_vitesse(1)
                    if self.bouton_moins.collidepoint(evenement.pos):
                        self.changer_vitesse(-1)
                if self.bouton_annuler.collidepoint(evenement.pos) and self.phase == "jeu":
                    self.annuler_coup()
                if self.bouton_menu.collidepoint(evenement.pos):
                    self.ouvrir_menu()
                if self.phase == "bravo":
                    self.clic_pancarte(evenement.pos)

    def changer_deadlock(self):
        # Allume ou eteint la detection de deadlock pour les boutons A* (le BFS ne l'utilise pas).
        self.deadlock = not self.deadlock
        if self.deadlock:
            self.afficher_message("Deadlock : oui - les A* ignorent les caisses perdues")
        else:
            self.afficher_message("Deadlock : non - A* normal")

    def changer_vitesse(self, sens):
        # sens = 1 : plus rapide ; sens = -1 : plus lent (DELAIS_PAS va du plus lent au plus rapide).
        self.vitesse = max(0, min(len(DELAIS_PAS) - 1, self.vitesse + sens))

    def evenement_accueil(self, evenement):
        # Ecran d'accueil : clic sur un bouton, ou J / C / Echap au clavier.
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                self.en_cours = False
            if evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_j):
                self.ouvrir_menu()
            if evenement.key == pygame.K_c:
                self.comparer_tous_les_niveaux()
            if evenement.key == pygame.K_s:
                self.changer_son()
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            if self.bouton_jouer.collidepoint(evenement.pos):
                self.ouvrir_menu()
            if self.bouton_comparer_tout.collidepoint(evenement.pos):
                self.comparer_tous_les_niveaux()
            if self.bouton_quitter.collidepoint(evenement.pos):
                self.en_cours = False

    def evenement_tableau_global(self, evenement):
        # Tableau de tous les niveaux : Echap ou "Fermer" le ferme ; T ou "Steps / Temps" change les colonnes.
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_t:
                self.vue_temps = not self.vue_temps
            elif evenement.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_c):
                self.vue_globale = False
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            if self.bouton_vue.collidepoint(evenement.pos):
                self.vue_temps = not self.vue_temps
            if self.bouton_fermer.collidepoint(evenement.pos):
                self.vue_globale = False

    def clic_pancarte(self, position):
        # Boutons de la pancarte "Bravo" (seulement une fois qu'elle est arrivee au milieu).
        if pygame.time.get_ticks() - self.debut_phase < DUREE_PANCARTE:
            return
        if self.bouton_suivant.collidepoint(position):
            self.niveau_suivant()
        elif self.bouton_rejouer.collidepoint(position):
            self.charger_niveau(self.numero)
        elif self.bouton_menu_bravo.collidepoint(position):
            self.ouvrir_menu()

    def niveau_suivant(self):
        # On garde une copie de l'image du niveau fini, on charge le suivant, et l'ecran glisse
        # de l'un a l'autre. Apres le dernier niveau, on revient au premier.
        self.ancien_monde = self.monde.copy()
        self.charger_niveau((self.numero + 1) % len(LEVELS))
        self.changer_phase("glisse")
        self.dessiner_niveau()

    def evenement_menu(self, evenement):
        # Dans le menu : clic sur une carte, touche 1 a 9, ou fleches + Entree ; Echap = retour a l'accueil.
        # Plus de PAR_PAGE niveaux : les boutons < > (ou la molette) changent de page.
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                self.ouvrir_accueil()
            if evenement.key == pygame.K_s:
                self.changer_son()
            if evenement.key == pygame.K_TAB:
                self.personnage = PERSONNAGES[(self.personnage_numero() + 1) % len(PERSONNAGES)][1]
            if evenement.unicode.isdigit():
                numero = int(evenement.unicode) - 1
                if 0 <= numero < len(LEVELS):
                    self.charger_niveau(numero)
            # Fleches : on se deplace dans la grille de cartes (2 colonnes).
            deplacements = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1, pygame.K_UP: -COLONNES_MENU, pygame.K_DOWN: COLONNES_MENU}
            if evenement.key in deplacements:
                nouveau = self.choix_menu + deplacements[evenement.key]
                if 0 <= nouveau < len(LEVELS):
                    self.choix_menu = nouveau
            if evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.charger_niveau(self.choix_menu)
        debut = self.choix_menu // PAR_PAGE * PAR_PAGE      # numero du premier niveau de la page
        if evenement.type == pygame.MOUSEMOTION:
            for k in range(PAR_PAGE):
                if debut + k < len(LEVELS) and self.boutons_niveaux[k].collidepoint(evenement.pos):
                    self.choix_menu = debut + k
        if evenement.type == pygame.MOUSEWHEEL:
            self.changer_page(-evenement.y)
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            for k in range(PAR_PAGE):
                if debut + k < len(LEVELS) and self.boutons_niveaux[k].collidepoint(evenement.pos):
                    self.charger_niveau(debut + k)
            for k in range(len(PERSONNAGES)):
                if self.boutons_perso[k].collidepoint(evenement.pos):
                    self.personnage = PERSONNAGES[k][1]
            if self.bouton_page_avant.collidepoint(evenement.pos):
                self.changer_page(-1)
            if self.bouton_page_apres.collidepoint(evenement.pos):
                self.changer_page(1)

    def personnage_numero(self):
        # Position du personnage choisi dans PERSONNAGES.
        for k in range(len(PERSONNAGES)):
            if PERSONNAGES[k][1] == self.personnage:
                return k
        return 0

    def image_joueur(self, direction, queue, perso=None, pas=0):
        # Image du personnage. direction = (ligne, colonne) du dernier deplacement ; queue = 0 (normal), 1 ou 2
        # (le chat remue la queue de face, le pingouin se dandine), 3 (le chat est content).
        # Les deux personnages ont une image par direction : face, droite, dos, gauche.
        if perso is None:
            perso = self.personnage
        if perso == "jack":
            # Jack a une image par direction, et 4 images de marche (pas = 0 a 3) vers la gauche et la droite.
            if direction[1] > 0:
                return self.sprites["jack_droite" + str(pas)]
            if direction[1] < 0:
                return self.sprites["jack_gauche" + str(pas)]
            if direction[0] < 0:
                return self.sprites["jack_dos"]
            if queue == 3:
                return self.sprites["jack_content"]
            if queue > 0:
                return self.sprites["jack_queue" + str(queue)]
            return self.sprites["jack_face"]
        image = self.sprites["pingu_face"]
        if direction[1] > 0:
            image = self.sprites["pingu_droite"]
        elif direction[1] < 0:
            image = self.sprites["pingu_gauche"]
        elif direction[0] < 0:
            image = self.sprites["pingu_dos"]
        if queue == 1:
            return pygame.transform.rotate(image, 8)       # il se dandine : penche d'un cote, puis de l'autre
        if queue == 2:
            return pygame.transform.rotate(image, -8)
        return image

    def changer_page(self, sens):
        # Passe a la page d'avant (-1) ou d'apres (1) : la carte choisie garde la meme place sur l'autre page.
        nouveau = self.choix_menu + sens * PAR_PAGE
        if 0 <= nouveau < len(LEVELS):
            self.choix_menu = nouveau
        elif sens > 0 and self.choix_menu // PAR_PAGE < (len(LEVELS) - 1) // PAR_PAGE:
            self.choix_menu = len(LEVELS) - 1      # derniere page plus courte : on prend son dernier niveau

    def bouger(self, action):
        # Un deplacement (touche flechee ou lecture automatique de la solution).
        # On ne re-ecrit AUCUNE regle ici : on demande a successorFunction la liste des coups possibles
        # et on prend celui qui correspond a la touche. Le reste ne sert qu'a l'animation.
        dr, dc = ACTIONS[action]
        ancien = self.etat
        self.anim_debut = pygame.time.get_ticks()
        self.anim_direction = (dr, dc)
        self.anim_caisse = None

        for nom, suivant in ancien.successorFunction():
            if nom == action:
                self.historique.append(ancien)
                self.etat = suivant
                self.coups = self.coups + 1
                arrivee = suivant.player_pos
                self.anim_joueur = (ancien.player_pos, arrivee)
                self.ajouter_particules(ancien.player_pos, 3, (225, 220, 195), 35)     # petit nuage de poussiere
                # Si une caisse etait sur la case d'arrivee, c'est qu'elle a ete poussee d'une case.
                case = ancien.grid[arrivee[0]][arrivee[1]]
                if case == "B" or case == "*":
                    caisse = (arrivee[0] + dr, arrivee[1] + dc)
                    self.anim_caisse = (arrivee, caisse)
                    # Un peu de poussiere derriere la caisse poussee, et des etincelles si elle arrive sur une cible.
                    self.ajouter_particules(arrivee, 5, (200, 190, 160), 60)
                    if suivant.grid[caisse[0]][caisse[1]] == "*":
                        self.ajouter_particules(caisse, 16, (255, 220, 90), 180)
                        self.pop_caisse = (caisse, pygame.time.get_ticks() + DUREE_MOUVEMENT)
                if self.son_actif and "pas" in self.sons:
                    self.sons["pas"].play()
                return

        # Coup refuse (mur, caisse bloquee...) : le chat ne bouge pas, il fait juste un petit "choc".
        self.anim_joueur = (ancien.player_pos, ancien.player_pos)

    def ajouter_particules(self, case, nombre, couleur, vitesse):
        # Petites particules qui partent du centre de la case dans toutes les directions
        # (vitesse en pixels par seconde). Elles disparaissent apres DUREE_PARTICULE ms.
        x, y = self.ecran_case(case[0], case[1])
        maintenant = pygame.time.get_ticks()
        for k in range(nombre):
            angle = 2 * math.pi * k / nombre + random.uniform(-0.3, 0.3)
            v = vitesse * random.uniform(0.5, 1.0)
            self.particules.append((x + TAILLE // 2, y + TAILLE // 2, math.cos(angle) * v, math.sin(angle) * v, maintenant, couleur))

    def annuler_coup(self):
        # Revient a l'etat d'avant le dernier coup (touche Z).
        if len(self.historique) == 0:
            self.afficher_message("Rien a annuler")
        else:
            self.afficher_message("Coup annule")
        if len(self.historique) > 0:
            self.etat = self.historique.pop()
            self.coups = self.coups - 1
            self.anim_joueur = None
            self.anim_caisse = None
            self.annuler_solution()

    def en_mouvement(self):
        # Vrai pendant l'animation du dernier deplacement.
        return pygame.time.get_ticks() - self.anim_debut < DUREE_MOUVEMENT

    def avancement(self):
        # Avancement de l'animation entre 0 et 1, qui ralentit a l'arrivee (plus doux qu'une vitesse constante).
        t = min(1.0, (pygame.time.get_ticks() - self.anim_debut) / float(DUREE_MOUVEMENT))
        return 1 - (1 - t) * (1 - t)

    def afficher_calcul(self):
        # Le calcul bloque la fenetre (Python pur) : on affiche "Calcul en cours..." AVANT de le lancer.
        self.draw()
        planche = pygame.Rect(0, 0, 360, 90)
        planche.center = (self.monde.get_width() // 2, self.monde.get_height() // 2)
        self.dessiner_planche(planche, 12)
        self.ecrire_ombre("Calcul en cours...", 26, (255, 235, 170), planche.centerx, planche.centery - 18, True)
        pygame.display.flip()
        pygame.event.pump()

    def resoudre(self, k):
        # Lance l'algorithme numero k, trace la trajectoire du chat (positions de chaque etat du chemin)
        # et demarre la lecture automatique.
        self.annuler_solution()
        self.algo_choisi = k
        nom = ALGOS[k][0]
        deadlock = self.deadlock and ALGOS[k][1] is not None
        if deadlock:
            nom = nom + " + deadlock"
        self.afficher_calcul()
        noeud, steps, duree = resoudre(self.etat, ALGOS[k][1], deadlock)
        # cout = longueur de la solution ; steps = noeuds developpes (travail de la recherche).
        if noeud is None:
            self.resultat = nom + " : aucune solution | " + str(steps) + " steps"
            self.afficher_message("Aucune solution depuis cette position")
        else:
            self.solution = noeud.getSolution()
            self.trajectoire = [etat.player_pos for etat in noeud.getPath()]
            self.auto = True
            self.aide = True
            self.dernier_pas = pygame.time.get_ticks()
            self.resultat = nom + " : cout " + str(noeud.g) + " | " + str(steps) + " steps | " + "%.3f" % duree + " s"

    def comparer(self):
        # Tableau de la position actuelle : pour chaque algorithme, cout / steps / temps SANS puis AVEC detection de deadlock.
        # Ligne = [algo, cout, steps, temps, cout DL, steps DL, temps DL, gain] ; le BFS n'a pas de version DL.
        # self.barres = (steps sans, steps avec ou None) de chaque ligne, pour dessiner les barres.
        self.annuler_solution()
        self.afficher_calcul()
        self.debut_comparaison = pygame.time.get_ticks()
        self.comparaison = [["Algo", "Cout", "Steps", "Temps", "Cout", "Steps", "Temps", "Gain"]]
        self.barres = []
        for nom, h in ALGOS:
            noeud, steps, duree = resoudre(self.etat, h, False)
            cout = "-"
            if noeud is not None:
                cout = str(noeud.g)
            ligne = [nom, cout, str(steps), "%.3f s" % duree, "-", "-", "-", "-"]
            avec = None
            if h is not None:
                noeud_dl, steps_dl, duree_dl = resoudre(self.etat, h, True)
                avec = steps_dl
                gain = 0.0
                if steps > 0:
                    gain = 100.0 * (steps - steps_dl) / steps
                if noeud_dl is not None:
                    ligne[4] = str(noeud_dl.g)
                ligne[5] = str(steps_dl)
                ligne[6] = "%.3f s" % duree_dl
                ligne[7] = "%.1f %%" % gain
            self.comparaison.append(ligne)
            self.barres.append((steps, avec))
        self.note_comparaison = "Gain = part des steps en moins avec la detection de deadlock (meme cout optimal)"

    def comparer_tous_les_niveaux(self):
        # Ecran d'accueil : les 7 colonnes de ALGOS_TOUS sur chaque niveau (une seule fois, le resultat est garde).
        if len(self.tableau_global) == 0:
            self.afficher_calcul()
            for niveau in LEVELS:
                etat = SokobanPuzzle(niveau["grid"])
                cout = "-"
                steps = []
                temps = []
                for nom, h, deadlock in ALGOS_TOUS:
                    noeud, nb_steps, duree = resoudre(etat, h, deadlock)
                    if noeud is not None:
                        cout = str(noeud.g)
                    steps.append(nb_steps)
                    temps.append(duree)
                self.tableau_global.append((niveau["name"], cout, steps, temps))
        self.vue_globale = True

    def lancer_confettis(self):
        # Confettis : position de depart, vitesse de chute, couleur et decalage au hasard.
        self.confettis = []
        largeur = self.monde.get_width()
        hauteur = self.monde.get_height()
        for k in range(NOMBRE_CONFETTIS):
            self.confettis.append((random.uniform(0, largeur), random.uniform(0, hauteur), random.uniform(60, 160),
                                   random.choice(COULEURS_CONFETTIS), random.uniform(0, 6.28)))

    def dessiner_confettis(self, ecoule):
        # Ils tombent en oscillant, et reviennent en haut quand ils sortent par le bas.
        hauteur = self.monde.get_height()
        for (x, y, vitesse, couleur, decalage) in self.confettis:
            yy = (y + vitesse * ecoule / 1000.0) % (hauteur + 20) - 10
            xx = x + math.sin(ecoule / 400.0 + decalage) * 18
            pygame.draw.rect(self.ecran, couleur, (int(xx), int(yy), 8, 5))

    def changer_phase(self, phase):
        self.phase = phase
        self.debut_phase = pygame.time.get_ticks()

    def update(self):
        # Enchaine les phases de fin de niveau. isGoal() est la seule chose qui decide de la victoire.
        ecoule = pygame.time.get_ticks() - self.debut_phase

        # Rien ne se passe tant que le chat n'a pas fini son pas en cours.
        if self.phase == "jeu" and not self.en_mouvement():
            if self.action_en_attente is not None:
                # Touche appuyee pendant le pas precedent.
                self.bouger(self.action_en_attente)
                self.action_en_attente = None
            elif self.auto and not self.pause and pygame.time.get_ticks() - self.dernier_pas >= DELAIS_PAS[self.vitesse]:
                # Lecture automatique de la solution : un pas toutes les DELAI_PAS millisecondes.
                if self.pas_auto < len(self.solution):
                    self.bouger(self.solution[self.pas_auto])
                    self.pas_auto = self.pas_auto + 1
                    self.dernier_pas = pygame.time.get_ticks()
                else:
                    self.auto = False

        if self.phase == "jeu":
            # On attend la fin de l'animation pour voir la derniere caisse arriver sur sa cible.
            # Le test le moins cher d'abord : isGoal (qui parcourt la grille) n'est appele qu'a l'arret.
            if not self.en_mouvement() and self.etat.isGoal():
                self.debut_victoire = pygame.time.get_ticks()
                self.duree_niveau = (self.debut_victoire - self.debut_niveau) / 1000.0
                self.nb_etoiles = self.calculer_etoiles()
                if self.nb_etoiles > self.etoiles.get(self.numero, 0):
                    self.etoiles[self.numero] = self.nb_etoiles
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
                self.changer_phase("bravo")     # la pancarte attend que le joueur choisisse
                self.lancer_confettis()
        elif self.phase == "glisse":
            if ecoule >= DUREE_GLISSE:
                self.phase = "jeu"
                self.ancien_monde = None

    def chemin_vers_porte(self):
        # Chemin (liste de cases) du chat jusqu'a la case juste devant la porte.
        # On essaie d'abord en evitant murs et caisses ; si une caisse bloque la sortie, on refait le chemin en
        # laissant passer sur les caisses : le chat sautera par-dessus (voir dessiner_chat_sortie).
        # Si la caisse est juste devant la porte, le chemin finit sur la porte elle-meme : il saute et entre.
        # C'est pour l'animation seulement : ce n'est pas un coup du jeu, donc ni les coups ni le cout ne changent.
        grille = self.etat.grid
        depart = self.etat.player_pos
        if self.porte is None:
            return [depart]
        arrivee = (self.porte[0] + 1, self.porte[1])
        chemin = self.parcours(depart, arrivee, False)
        if chemin is None:
            chemin = self.parcours(depart, arrivee, True)
        if chemin is None:
            return [depart]          # porte inaccessible : le chat reste ou il est
        if self.est_caisse(arrivee):
            chemin.append(self.porte)
        return chemin

    def est_caisse(self, case):
        # Vrai s'il y a une caisse (sur une cible ou non) sur la case (ligne, colonne).
        symbole = self.etat.grid[case[0]][case[1]]
        return symbole == "B" or symbole == "*"

    def parcours(self, depart, arrivee, saute):
        # Parcours en largeur sur les cases du depart a l'arrivee. Les murs bloquent toujours ;
        # les caisses bloquent sauf si saute est vrai. Retourne la liste des cases, ou None.
        grille = self.etat.grid
        parent = {depart: None}
        file = deque([depart])
        while len(file) > 0:
            r, c = file.popleft()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                voisine = (r + dr, c + dc)
                if voisine in parent or grille[voisine[0]][voisine[1]] == "O":
                    continue
                if self.est_caisse(voisine) and not saute:
                    continue
                parent[voisine] = (r, c)
                file.append(voisine)
        if arrivee not in parent:
            return None
        chemin = []
        case = arrivee
        while case is not None:
            chemin.append(case)
            case = parent[case]
        chemin.reverse()
        return chemin

    def trouver_porte(self):
        # La porte de sortie est posee sur un mur visible du haut du niveau, avec du sol juste en dessous
        # (de preference au milieu). Retourne (ligne, colonne) ou None. C'est seulement un dessin :
        # la case reste un mur, les regles du jeu ne changent pas.
        # On parcourt les lignes de haut en bas ; dans la premiere ligne qui a une place possible,
        # on garde celle qui est la plus proche du milieu.
        grille = self.etat.grid
        milieu = len(grille[0]) // 2
        meilleure = None
        for r in range(len(grille) - 1):
            for c in range(len(grille[r])):
                if grille[r][c] == "O" and touche_le_sol(grille, r, c) and grille[r + 1][c] != "O":
                    if meilleure is None or abs(c - milieu) < abs(meilleure[1] - milieu):
                        meilleure = (r, c)
            if meilleure is not None:
                return meilleure
        return None

    def case_libre(self, wr, wc):
        # Vrai si la case (wr, wc) de la zone de jeu est de l'herbe visible : hors du niveau, ou case de mur
        # qui ne touche pas le sol (donc non dessinee). On peut y poser du decor.
        # Le niveau peut etre decale d'une demi-case : une case de la zone recouvre alors deux cases du niveau,
        # on regarde les deux (si le decalage est entier, elles sont identiques).
        grille = self.etat.grid
        lignes = [int(math.floor(wr - self.decalage_ligne)), int(math.ceil(wr - self.decalage_ligne))]
        colonnes = [int(math.floor(wc - self.decalage_colonne)), int(math.ceil(wc - self.decalage_colonne))]
        for r in lignes:
            for c in colonnes:
                if 0 <= r < len(grille) and 0 <= c < len(grille[r]):
                    if not (grille[r][c] == "O" and not touche_le_sol(grille, r, c)):
                        return False
        return True

    def dessiner_cible(self, x, y, allumee):
        # La cible est une plaque de pierre carree avec un contour dore (dessinee avec pygame.draw,
        # il n'y a pas de sprite pour ca dans le pack). Quand une caisse est dessus, le contour
        # brille et un halo dore deborde autour de la caisse.
        plaque = pygame.Rect(x + 4, y + 4, TAILLE - 8, TAILLE - 8)
        pygame.draw.rect(self.monde, COULEUR_PLAQUE, plaque, 0, 6)
        if allumee:
            self.monde.blit(self.halo_cible, (x + TAILLE // 2 - TAILLE, y + TAILLE // 2 - TAILLE))
            pygame.draw.rect(self.monde, COULEUR_CONTOUR_ALLUME, plaque, 4, 6)
        else:
            pygame.draw.rect(self.monde, COULEUR_CONTOUR, plaque, 4, 6)

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
        return grille[r][c] == "O" and touche_le_sol(grille, r, c)

    def poser(self, nom, wr, wc, ombre=False):
        # Pose un objet du decor, les pieds en bas de la case (wr, wc) de la zone de jeu, centre sur la colonne.
        # On verifie TOUTES les cases que l'image recouvre : si l'une touche le niveau ou un autre objet,
        # on ne pose rien. Ainsi le meme decor marche pour les petits et les grands niveaux.
        # ombre : dessine une ombre au sol (pour les arbres, dont l'image n'a pas d'ombre).
        image = self.sprites[nom]
        x = wc * TAILLE + (TAILLE - image.get_width()) // 2
        y = (wr + 1) * TAILLE - image.get_height()
        cases = []
        for r in range(y // TAILLE, wr + 1):
            for c in range(x // TAILLE, (x + image.get_width() - 1) // TAILLE + 1):
                if r < 0 or c < 0 or r >= self.cases_hauteur or c >= self.cases_largeur:
                    return
                if not self.case_libre(r, c) or (r, c) in self.cases_decor:
                    return
                cases.append((r, c))
        for case in cases:
            self.cases_decor.append(case)
        if ombre:
            self.dessiner_ombre(x + image.get_width() // 2, (wr + 1) * TAILLE - 4, image.get_width() * 2 // 3)
        self.monde.blit(image, (x, y))

    def dessiner_ombre(self, centre_x, bas_y, largeur):
        # Ombre douce au sol : une ellipse noire transparente, centree en centre_x, posee sur bas_y.
        hauteur = max(4, largeur // 3)
        ombre = pygame.transform.smoothscale(self.image_ombre, (largeur, hauteur))
        self.monde.blit(ombre, (centre_x - largeur // 2, bas_y - hauteur // 2))

    def dessiner_decor(self):
        # Decor identique dans tous les niveaux, place par des regles fixes (pas de hasard).
        # Les objets qui ne tiennent pas (niveau trop grand) ne sont simplement pas poses (voir poser).
        self.cases_decor = []
        bas_fenetre = self.cases_hauteur - 2
        droite_fenetre = self.cases_largeur - 2

        # Deux totems poses sur le mur du haut, de chaque cote de la porte (jamais dans le vide).
        # On essaie a 3 cases de la porte, sinon a 2 cases (niveaux etroits).
        if self.porte is not None:
            # Les cases au-dessus de la porte sont reservees a son arche (dessinee plus tard).
            for dc in (-1, 0, 1, 2):
                self.cases_decor.append((self.porte[0] + self.ligne0 - 1, self.porte[1] + self.colonne0 + dc))
            for sens in (-1, 1):
                for distance in (3, 2):
                    colonne = self.porte[1] + sens * distance
                    if self.mur_visible(self.porte[0], colonne):
                        self.poser("totem", self.porte[0] + self.ligne0 - 1, colonne + self.colonne0)
                        break

        # Sous le niveau : un banc au milieu, des vases a gauche, des tonneaux a droite.
        grille = self.etat.grid
        bas = min(self.ligne0 + len(grille), bas_fenetre)
        gauche = self.colonne0
        droite = self.colonne0 + len(grille[0]) - 1
        self.poser("banc", bas, (gauche + droite) // 2)
        self.poser("vase", bas, gauche)
        self.poser("pot", bas, gauche + 1)
        self.poser("tonneau", bas, droite)
        self.poser("tonneau", bas, droite - 1)
        self.poser("tonneau", bas - 1, droite + 1)

        # Un arbre dans chaque coin de la fenetre, puis des objets le long des bords.
        self.poser("arbre1", 4, 2, True)
        self.poser("arbre3", 4, droite_fenetre - 1, True)
        self.poser("arbre2", bas_fenetre, 2, True)
        self.poser("arbre1", bas_fenetre, droite_fenetre - 1, True)
        self.poser("statue", 7, 1)
        self.poser("statue", 7, droite_fenetre)
        self.poser("lanterne", 9, 1)
        self.poser("lanterne", 9, droite_fenetre)
        self.poser("pilier_casse", 3, 5)
        self.poser("panneau", 2, droite_fenetre - 4)
        self.poser("coffre", bas_fenetre - 1, droite_fenetre - 3)
        self.poser("rocher", bas_fenetre - 2, 1)
        self.poser("vase2", bas_fenetre, 5)

        # Petits cailloux semes dans l'herbe libre (positions donnees par une formule).
        for wr in range(1, self.cases_hauteur - 1):
            for wc in range(1, self.cases_largeur - 1):
                if (wr * 13 + wc * 7) % 11 == 0:
                    self.poser(["caillou", "caillou2"][(wr + wc) % 2], wr, wc)

    def sur_la_case(self, image, r, c):
        # Coin haut gauche ou dessiner une image posee sur la case (r, c) du niveau :
        # centree en largeur, le bas de l'image sur le bas de la case.
        x, y = self.ecran_case(r, c)
        return x + (TAILLE - image.get_width()) // 2, y + TAILLE - image.get_height()

    def position_porte(self):
        # Sprite de la porte (fermee ou ouverte) et coin haut gauche ou la dessiner, sur sa case de mur.
        sprite = self.sprites["porte"]
        if self.phase in PHASES_PORTE_OUVERTE:
            sprite = self.sprites["porte_ouverte"]
        x, y = self.sur_la_case(sprite, self.porte[0], self.porte[1])
        return sprite, x, y

    def dessiner_trajectoire(self):
        # Trace le chemin que le chat va suivre : une ligne bleue entre les centres des cases,
        # avec un point sur chaque case et un gros point a l'arrivee.
        # On ne dessine que ce qu'il reste a parcourir : le trait raccourcit pendant la lecture.
        points = []
        for (r, c) in self.trajectoire[self.pas_auto:]:
            x, y = self.ecran_case(r, c)
            points.append((x + TAILLE // 2, y + TAILLE // 2))
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

    def choisir_face(self, grille, r, c):
        # Type de la face de mur de la case (r, c), choisi selon sa position : le plus souvent une face simple
        # (dans l'ombre, deux variantes), parfois fissuree ou couverte de mousse, et une fenetre eclairee
        # (sauf pres de la porte).
        hasard = (r * 5 + c * 3) % 9
        loin_de_la_porte = self.porte is None or abs(c - self.porte[1]) > 1
        if hasard == 0 and loin_de_la_porte:
            return "mur_clair1"
        if hasard == 3:
            return "mur_sombre2"
        if hasard == 5:
            return "mur_sombre3"
        return "mur_sombre" + str((r + c) % 2)

    def preparer_fond(self):
        # Dessine une seule fois, au chargement du niveau, tout ce qui ne bouge jamais :
        # herbe, haie, decor, murs et sol. A chaque image, on recopie juste ce fond (bien plus rapide).
        grille = self.etat.grid
        self.dessiner_herbe()
        self.dessiner_haie()
        self.dessiner_decor()
        for r in range(len(grille)):
            for c in range(len(grille[r])):
                x, y = self.ecran_case(r, c)
                if grille[r][c] == "O":
                    if touche_le_sol(grille, r, c):
                        if est_sol(grille, r + 1, c):
                            # Du sol juste en dessous : on voit la face du mur (briques).
                            self.monde.blit(self.sprites[self.choisir_face(grille, r, c)], (x, y))
                        else:
                            # Sinon on ne voit que le dessus du mur (pierres claires).
                            self.monde.blit(self.sprites["mur_cap"], (x, y))
                else:
                    # Toutes les autres cases sont du sol de jeu (dalle de pierre) ; l'herbe reste a l'exterieur.
                    self.monde.blit(self.sprites["sol" + str(1 + (r * 3 + c * 5) % 2)], (x, y))
                    # Ombre douce du mur au-dessus, a gauche et a droite.
                    if not est_sol(grille, r - 1, c):
                        ombre = "ombre_nord"
                        if est_sol(grille, r - 2, c):
                            ombre = "ombre_nord_forte"       # le mur au-dessus est dans l'ombre
                        self.monde.blit(self.sprites[ombre], (x, y))
                    if not est_sol(grille, r, c - 1):
                        self.monde.blit(self.sprites["ombre_ouest"], (x, y))
                    if not est_sol(grille, r, c + 1):
                        self.monde.blit(self.sprites["ombre_est"], (x + TAILLE - self.sprites["ombre_est"].get_width(), y))
        self.fond = self.monde.copy()

    def dessiner_niveau(self):
        # Dessine le niveau sur self.monde : le fond tout pret, puis les cibles, la trajectoire,
        # les caisses, le chat et la porte (ce qui peut changer d'une image a l'autre).
        grille = self.etat.grid
        self.monde.blit(self.fond, (0, 0))

        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                if case == "S" or case == "." or case == "*":
                    x, y = self.ecran_case(r, c)
                    self.dessiner_cible(x, y, case == "*")

        # La trajectoire est dessinee sur le sol, sous les caisses et le chat.
        self.dessiner_trajectoire()

        # Les caisses (celle qu'on vient de pousser glisse vers sa nouvelle case), avec leur ombre.
        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                if case == "B" or case == "*":
                    x, y = self.ecran_case(r, c)
                    if self.anim_caisse is not None and self.anim_caisse[1] == (r, c):
                        x, y = self.glisser(self.anim_caisse[0], self.anim_caisse[1], self.avancement())
                    self.dessiner_ombre(x + TAILLE // 2 + 3, y + TAILLE - 3, TAILLE - 4)
                    image = self.sprites["caisse"]
                    bx = x
                    by = y
                    if self.pop_caisse is not None and self.pop_caisse[0] == (r, c):
                        age = pygame.time.get_ticks() - self.pop_caisse[1]
                        if 0 <= age < 350:
                            # La caisse grossit un instant puis reprend sa taille.
                            cote = int(TAILLE * (1 + 0.22 * math.sin(math.pi * age / 350.0)))
                            image = pygame.transform.smoothscale(image, (cote, cote))
                            bx = x - (cote - TAILLE) // 2
                            by = y - (cote - TAILLE)
                    self.monde.blit(image, (bx, by))
                    if case == "*":
                        # Caisse bien placee : contour vert, pour la reperer de loin.
                        pygame.draw.rect(self.monde, COULEUR_BON, (x, y, TAILLE, TAILLE), 3, 6)

        # Le chat par-dessus (pendant la marche vers la porte, il est dessine a part, voir plus bas).
        if self.phase != "marche" and self.phase != "queue" and self.phase != "bravo":
            self.dessiner_chat()

        # Porte de sortie, dessinee par-dessus le mur choisi (fermee, puis ouverte avec de la lumiere derriere).
        if self.porte is not None:
            sprite, x, y = self.position_porte()
            # L'arche en pierre est toujours autour de la porte.
            arche = self.sprites["arche_porte"]
            self.monde.blit(arche, self.sur_la_case(arche, self.porte[0], self.porte[1]))
            if self.phase in PHASES_PORTE_OUVERTE:
                pygame.draw.rect(self.monde, (255, 245, 190), (x + 4, y + 8, sprite.get_width() - 8, sprite.get_height() - 8))
            self.monde.blit(sprite, (x, y))

        # Le chat qui marche vers la porte, puis remue la queue devant (par-dessus la porte et l'arche).
        if self.phase == "marche" or self.phase == "queue" or self.phase == "bravo":
            self.dessiner_chat_sortie()

        self.dessiner_effets()

    def dessiner_effets(self):
        # Ce qui rend le decor vivant : etincelles et poussiere, lucioles.
        maintenant = pygame.time.get_ticks()

        # Particules : elles partent en ligne droite et rapetissent jusqu'a disparaitre.
        restantes = []
        for (x, y, vx, vy, naissance, couleur) in self.particules:
            age = (maintenant - naissance) / float(DUREE_PARTICULE)     # 0 a la naissance, 1 a la fin
            if age < 1:
                restantes.append((x, y, vx, vy, naissance, couleur))
                secondes = (maintenant - naissance) / 1000.0
                rayon = max(1, int(5 * (1 - age)))
                pygame.draw.circle(self.monde, couleur, (int(x + vx * secondes), int(y + vy * secondes)), rayon)
        self.particules = restantes

        # Lucioles : elles flottent autour de leur place et clignotent doucement.
        for (x0, y0, vitesse, decalage) in self.lucioles:
            t = maintenant / 1000.0 * vitesse + decalage
            x = x0 + math.sin(t * 0.7) * 30
            y = y0 + math.cos(t * 0.9) * 20
            eclat = (math.sin(t * 2.5) + 1) / 2
            self.lueur.set_alpha(int(60 + 195 * eclat))
            self.monde.blit(self.lueur, (int(x) - 10, int(y) - 10))

        # Petales : ils descendent en se balancant, et reviennent par l'autre cote quand ils sortent.
        largeur = self.monde.get_width()
        hauteur = self.monde.get_height()
        secondes = maintenant / 1000.0
        for (x0, y0, vx, vy, decalage) in self.petales:
            x = (x0 + vx * secondes + math.sin(secondes * 1.3 + decalage) * 25) % largeur
            y = (y0 + vy * secondes) % hauteur
            pygame.draw.ellipse(self.monde, (255, 180, 205), (int(x), int(y), 7, 4))
            pygame.draw.ellipse(self.monde, (255, 225, 235), (int(x) + 1, int(y), 3, 2))

    def ecran_case(self, r, c):
        # Coin haut gauche (en pixels) de la case (r, c) du niveau ; r et c peuvent etre a virgule.
        return int((c + self.decalage_colonne) * TAILLE), int((r + self.decalage_ligne) * TAILLE)

    def glisser(self, depart, arrivee, p):
        # Position (en pixels) d'un objet entre deux cases : p = 0 sur depart, p = 1 sur arrivee.
        r = depart[0] + (arrivee[0] - depart[0]) * p
        c = depart[1] + (arrivee[1] - depart[1]) * p
        return self.ecran_case(r, c)

    def dessiner_chat(self):
        # Le chat sur sa case, ou en train de glisser vers elle (avec un petit saut),
        # ou qui fait un petit "choc" contre l'obstacle quand le coup est refuse.
        r, c = self.etat.player_pos
        x, y = self.ecran_case(r, c)
        saut = 0
        pas = 0        # image de la marche (0 a 3)
        if self.anim_joueur is not None and self.anim_joueur[1] == (r, c) and self.en_mouvement():
            t = (pygame.time.get_ticks() - self.anim_debut) / float(DUREE_MOUVEMENT)
            if self.anim_joueur[0] != self.anim_joueur[1]:
                pas = min(3, int(t * 4))
                x, y = self.glisser(self.anim_joueur[0], self.anim_joueur[1], self.avancement())
                saut = int(math.sin(math.pi * t) * 6)
            else:
                choc = math.sin(math.pi * t) * 5
                x = x + int(self.anim_direction[1] * choc)
                y = y + int(self.anim_direction[0] * choc)

        image = self.image_joueur(self.anim_direction, 0, None, pas)
        if not self.en_mouvement():
            # A l'arret, le chat respire (il monte et descend d'un pixel) et remue la queue de temps en temps.
            maintenant = pygame.time.get_ticks()
            y = y + int(round(math.sin(maintenant / 350.0)))
            if maintenant % 4000 < 600:
                image = self.image_joueur(self.anim_direction, 1 + (maintenant // 150) % 2)
        self.poser_chat(image, x, y, saut)

    def poser_chat(self, image, x, y, saut):
        # Dessine le chat dans la case dont le coin haut gauche est (x, y), tourne du bon cote,
        # avec son ombre sous les pattes (plus petite quand il est en l'air, saut = hauteur du saut).
        self.dessiner_ombre(x + TAILLE // 2, y + TAILLE - 4, max(10, TAILLE * 2 // 3 - saut))
        # Le chat est plus haut qu'une case : on aligne ses pieds sur le bas de la case.
        self.monde.blit(image, (x + (TAILLE - image.get_width()) // 2, y + TAILLE - image.get_height() - saut))

    def dessiner_chat_sortie(self):
        # Le chat glisse d'une case a la suivante le long de self.chemin_chat, en faisant de petits sauts,
        # puis il remue la queue devant la porte.
        ecoule = pygame.time.get_ticks() - self.debut_phase
        chemin = self.chemin_chat
        rang = ecoule / float(DELAI_CASE)
        if self.phase != "marche" or rang > len(chemin) - 1:
            rang = len(chemin) - 1.0
        i = int(rang)
        suivante = min(i + 1, len(chemin) - 1)
        x, y = self.glisser(chemin[i], chemin[suivante], rang - i)

        # Saut par-dessus une caisse : le chat monte a la hauteur HAUTEUR_SAUT en arrivant sur la case d'une caisse,
        # reste en l'air au-dessus d'elle, puis redescend a la case suivante.
        hauteur_a = 0
        hauteur_b = 0
        if self.est_caisse(chemin[i]):
            hauteur_a = HAUTEUR_SAUT
        if self.est_caisse(chemin[suivante]):
            hauteur_b = HAUTEUR_SAUT
        avance = rang - i
        if hauteur_b > hauteur_a:
            avance = math.sin(avance * math.pi / 2)         # il s'elance : monte vite puis ralentit
        elif hauteur_b < hauteur_a:
            avance = 1 - math.cos(avance * math.pi / 2)     # il retombe : de plus en plus vite
        saut = int(hauteur_a + (hauteur_b - hauteur_a) * avance)

        direction = (0, 0)
        if self.phase != "marche":
            # Arrive devant la porte : le personnage est content, il saute sur place (queue qui remue, ou dandinement)
            # et lance des etincelles a chaque rebond.
            maintenant = pygame.time.get_ticks()
            saut = saut + int(abs(math.sin(maintenant / 200.0)) * 18)
            if self.personnage == "jack":
                image = self.image_joueur(direction, 3)
            else:
                image = self.image_joueur(direction, 1 + (maintenant // 150) % 2)
            rebond = int(maintenant / 628.0)
            if rebond != self.dernier_rebond:
                self.dernier_rebond = rebond
                self.ajouter_particules(chemin[-1], 8, (255, 225, 110), 120)
        else:
            saut = saut + int(abs(math.sin(ecoule / 90.0)) * 4)
            direction = (chemin[suivante][0] - chemin[i][0], chemin[suivante][1] - chemin[i][1])
            image = self.image_joueur(direction, 0, None, int(rang * 4) % 4)
        self.poser_chat(image, x, y, saut)

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
        # Pancarte en bois "Bravo" qui descend du haut de l'ecran jusqu'au milieu de la zone de jeu,
        # avec le nombre de coups et trois boutons : Rejouer, Niveau suivant, Menu.
        progression = min(1.0, ecoule / float(DUREE_PANCARTE))
        progression = 1 - (1 - progression) * (1 - progression)      # ralentit a l'arrivee
        decalage = int((self.pancarte.bottom + 40) * (progression - 1))   # negatif tant qu'elle descend
        planche = self.pancarte.move(0, decalage)
        x = planche.x
        y = planche.y
        largeur = planche.width
        hauteur = planche.height

        # Deux poteaux, puis la planche en bois.
        pygame.draw.rect(self.ecran, (95, 60, 30), (x + 50, y + hauteur - 10, 24, 50))
        pygame.draw.rect(self.ecran, (95, 60, 30), (x + largeur - 74, y + hauteur - 10, 24, 50))
        self.dessiner_planche(planche, 12)

        texte = str(self.coups) + " coups en " + "%.1f" % self.duree_niveau + " s"
        self.ecrire_ombre("BRAVO !", 56, (255, 235, 170), planche.centerx, y + 12, True)
        self.ecrire_ombre(texte, 20, (255, 240, 200), planche.centerx, y + 80, True)
        if self.aide:
            self.ecrire_ombre("Resolu par l algorithme", 16, (130, 225, 255), planche.centerx, y + 116, True)
        else:
            # Les etoiles apparaissent une par une en grossissant ; objectif = nombre de coups minimal.
            for k in range(3):
                apparition = max(0.0, min(1.0, (ecoule - 300 - k * 250) / 200.0))
                if apparition > 0:
                    couleur = COULEUR_ETOILE_VIDE
                    if k < self.nb_etoiles:
                        couleur = COULEUR_ETOILE
                    dessiner_etoile(self.ecran, planche.centerx + (k - 1) * 56, y + 130, int(20 * apparition), couleur)

        # Les boutons suivent la pancarte pendant qu'elle descend.
        nom_suivant = "Niveau suivant"
        if self.numero == len(LEVELS) - 1:
            nom_suivant = "Niveau 1"
        self.dessiner_bouton(self.bouton_rejouer.move(0, decalage), "Rejouer")
        self.dessiner_bouton(self.bouton_suivant.move(0, decalage), nom_suivant)
        self.dessiner_bouton(self.bouton_menu_bravo.move(0, decalage), "Menu")

    def ecrire_ombre(self, texte, taille, couleur, x, y, centre=False):
        # Ecrit un texte avec une ombre sombre decalee de 2 pixels (plus lisible sur le bois et l'herbe).
        # Si centre est vrai, x est le milieu du texte (et pas son bord gauche).
        image = self.ecrire(texte, taille, couleur)
        if centre:
            x = x - image.get_width() // 2
        self.ecran.blit(self.ecrire(texte, taille, (40, 25, 10)), (x + 2, y + 2))
        self.ecran.blit(image, (x, y))

    def dessiner_planche(self, rectangle, arrondi):
        # Planche en bois : ombre portee, bois avec des veines, contour fonce et filet clair en haut.
        ombre = pygame.Surface((rectangle.width, rectangle.height), pygame.SRCALPHA)
        pygame.draw.rect(ombre, (0, 0, 0, 90), ombre.get_rect(), 0, arrondi)
        self.ecran.blit(ombre, (rectangle.x + 5, rectangle.y + 6))
        pygame.draw.rect(self.ecran, (150, 100, 52), rectangle, 0, arrondi)
        for k in range(1, rectangle.height // 22 + 1):
            y = rectangle.y + k * 22
            pygame.draw.line(self.ecran, (135, 88, 44), (rectangle.x + 10, y), (rectangle.right - 10, y), 2)
        pygame.draw.line(self.ecran, (190, 140, 85), (rectangle.x + arrondi, rectangle.y + 3), (rectangle.right - arrondi, rectangle.y + 3), 2)
        pygame.draw.rect(self.ecran, (85, 52, 25), rectangle, 4, arrondi)

    def dessiner_apercu(self, grille, x, y, cote):
        # Petite carte du niveau : une case = un carre de cote pixels (murs du bord seulement).
        couleurs = {"O": (110, 95, 80), " ": (190, 185, 170), "S": (235, 180, 60), "B": (170, 110, 50),
                    "*": (110, 190, 90), "R": (240, 140, 60), ".": (240, 140, 60)}
        for r in range(len(grille)):
            for c in range(len(grille[r])):
                case = grille[r][c]
                if case != "O" or touche_le_sol(grille, r, c):
                    pygame.draw.rect(self.ecran, couleurs[case], (x + c * cote, y + r * cote, cote, cote))

    def dessiner_accueil(self):
        # Ecran d'accueil : herbe et haie (avec les lucioles), une grande planche avec le titre et trois boutons.
        self.monde.blit(self.fond_menu, (0, 0))
        self.dessiner_effets()
        self.ecran.blit(self.monde, (0, 0))
        largeur = self.monde.get_width()
        self.dessiner_planche(pygame.Rect(largeur // 2 - 240, 40, 480, 456), 14)
        maintenant = pygame.time.get_ticks()
        flotte = int(math.sin(maintenant / 450.0) * 4)       # le titre monte et descend doucement
        self.ecrire_ombre("SOKOBAN", 72, (255, 235, 170), largeur // 2, 64 + flotte, True)
        self.ecrire_ombre("BFS et A*  -  M1 Visual Computing", 16, (255, 240, 200), largeur // 2, 160, True)
        self.dessiner_bouton(self.bouton_jouer, "Jouer")
        self.dessiner_bouton(self.bouton_comparer_tout, "Comparer (tous les niveaux)")
        self.dessiner_bouton(self.bouton_quitter, "Quitter")

        # Le chat va et vient entre deux caisses, avec de petits sauts.
        sol = 470
        caisse = self.sprites["caisse"]
        self.ecran.blit(caisse, (largeur // 2 - 130 - TAILLE // 2, sol - TAILLE))
        self.ecran.blit(caisse, (largeur // 2 + 130 - TAILLE // 2, sol - TAILLE))
        phase = maintenant / 900.0
        x = largeur // 2 + math.sin(phase) * 70
        saut = abs(math.sin(maintenant / 110.0)) * 5
        direction = (0, 1)
        if math.cos(phase) < 0:
            direction = (0, -1)
        chat = self.image_joueur(direction, 0, None, int(maintenant / 110.0) % 4)
        self.dessiner_ombre_ecran(int(x), sol - 2, 28)
        self.ecran.blit(chat, (int(x) - chat.get_width() // 2, sol - chat.get_height() - int(saut)))

    def dessiner_ombre_ecran(self, centre_x, bas_y, largeur):
        # Meme ombre que dessiner_ombre, mais directement sur l'ecran.
        ombre = pygame.transform.smoothscale(self.image_ombre, (largeur, max(4, largeur // 3)))
        self.ecran.blit(ombre, (centre_x - largeur // 2, bas_y - ombre.get_height() // 2))

    def dessiner_menu(self):
        # Menu : herbe et haie (avec les lucioles), une grande planche avec le titre,
        # puis une carte par niveau de la page : grand apercu, numero, nom et etoiles gagnees.
        self.monde.blit(self.fond_menu, (0, 0))
        self.dessiner_effets()
        self.ecran.blit(self.monde, (0, 0))

        largeur = self.monde.get_width()
        hauteur = self.monde.get_height()
        self.dessiner_planche(pygame.Rect(largeur // 2 - 480, 24, 960, hauteur - 36), 14)
        self.ecrire_ombre("SOKOBAN", 56, (255, 235, 170), largeur // 2, 36, True)
        page = self.choix_menu // PAR_PAGE
        nb_pages = (len(LEVELS) + PAR_PAGE - 1) // PAR_PAGE
        self.ecrire_ombre("Choisis un niveau", 20, (255, 240, 200), largeur // 2, 100, True)

        debut = page * PAR_PAGE
        for k in range(PAR_PAGE):
            i = debut + k
            if i >= len(LEVELS):
                break
            carte = self.boutons_niveaux[k]
            fond = (120, 78, 38)
            bord = (200, 160, 100)
            if i == self.choix_menu:
                # La carte choisie (sous la souris) se souleve un peu, plus claire, avec un contour dore.
                carte = carte.move(0, -4)
                fond = (175, 120, 65)
                bord = (255, 225, 120)
            pygame.draw.rect(self.ecran, (60, 38, 18), carte.move(0, 5), 0, 10)     # epaisseur sous la carte
            pygame.draw.rect(self.ecran, fond, carte, 0, 10)
            pygame.draw.rect(self.ecran, bord, carte, 3, 10)

            # Apercu du niveau a gauche de la carte, centre dans un carre de 76 x 76.
            grille = LEVELS[i]["grid"]
            largeur_grille = 0
            for ligne in grille:
                largeur_grille = max(largeur_grille, len(ligne))
            cote = 76 // max(len(grille), largeur_grille)
            self.dessiner_apercu(grille, carte.x + 10 + (76 - cote * largeur_grille) // 2, carte.y + 12 + (76 - cote * len(grille)) // 2, cote)
            self.ecrire_ombre(str(i + 1), 30, (255, 225, 120), carte.x + 98, carte.y + 8)
            self.ecrire_ombre(LEVELS[i]["name"], 16, (255, 245, 215), carte.x + 98, carte.y + 44)
            # Etoiles gagnees (grises tant que le niveau n'est pas reussi).
            for e in range(3):
                couleur = COULEUR_ETOILE_VIDE
                if e < self.etoiles.get(i, 0):
                    couleur = COULEUR_ETOILE
                dessiner_etoile(self.ecran, carte.x + 108 + e * 26, carte.y + 78, 9, couleur)

        # Choix du personnage : le bouton du personnage actuel est doré.
        self.ecrire_ombre("Personnage :", 18, (255, 240, 200), largeur // 2 - 446, hauteur - 54)
        for k in range(len(PERSONNAGES)):
            bouton = self.boutons_perso[k]
            choisi = PERSONNAGES[k][1] == self.personnage
            fond = (120, 78, 38)
            bord = (200, 160, 100)
            if choisi:
                fond = (175, 120, 65)
                bord = (255, 225, 120)
            elif bouton.collidepoint(pygame.mouse.get_pos()):
                fond = (150, 100, 52)
            pygame.draw.rect(self.ecran, (60, 38, 18), bouton.move(0, 4), 0, 10)
            pygame.draw.rect(self.ecran, fond, bouton, 0, 10)
            pygame.draw.rect(self.ecran, bord, bouton, 3, 10)
            image = self.image_joueur((0, 0), 0, PERSONNAGES[k][1])
            self.ecran.blit(image, (bouton.x + 12, bouton.bottom - 4 - image.get_height()))
            self.ecrire_ombre(PERSONNAGES[k][0], 18, (255, 245, 215), bouton.x + 66, bouton.y + 14)

        # Boutons de page (seulement s'il y a plusieurs pages) et numero de la page.
        if nb_pages > 1:
            self.dessiner_bouton(self.bouton_page_avant, "<")
            self.dessiner_bouton(self.bouton_page_apres, ">")
            self.ecrire_ombre(str(page + 1) + " / " + str(nb_pages), 18, (255, 240, 200), largeur // 2 + 320, self.bouton_page_avant.y + 8, True)

    def dessiner_bouton(self, rectangle, texte, allume=False):
        # Bouton en bois avec un peu de relief : plus clair sous la souris, enfonce quand on clique.
        souris = pygame.mouse.get_pos()
        survole = rectangle.collidepoint(souris)
        enfonce = survole and pygame.mouse.get_pressed()[0]
        couleur = (150, 100, 52)
        if allume:
            couleur = (70, 150, 85)          # bouton allume (ex : Deadlock) : vert
        if survole:
            couleur = (couleur[0] + 30, couleur[1] + 22, couleur[2] + 18)
        if survole:
            rectangle = rectangle.inflate(6, 4)       # le bouton grossit sous la souris
        pygame.draw.rect(self.ecran, (60, 38, 18), rectangle.move(0, 3), 0, 8)    # epaisseur du bouton
        if enfonce:
            rectangle = rectangle.move(0, 2)
        pygame.draw.rect(self.ecran, couleur, rectangle, 0, 8)
        pygame.draw.line(self.ecran, (215, 165, 105), (rectangle.x + 8, rectangle.y + 3), (rectangle.right - 8, rectangle.y + 3), 2)
        pygame.draw.rect(self.ecran, (230, 200, 130), rectangle, 2, 8)
        image = self.ecrire(texte, 16, (255, 245, 215))
        self.ecran.blit(image, (rectangle.x + (rectangle.width - image.get_width()) // 2, rectangle.y + (rectangle.height - image.get_height()) // 2))

    def dessiner_barre(self):
        # Barre d'infos en bas : texte a gauche (niveau, coups, algorithme, resultat), boutons a droite.
        haut = self.monde.get_height()
        largeur = self.ecran.get_width()
        # Fond en bois sombre, avec un filet dore en haut.
        pygame.draw.rect(self.ecran, (72, 47, 26), (0, haut, largeur, HAUTEUR_BARRE))
        pygame.draw.line(self.ecran, (230, 200, 130), (0, haut), (largeur, haut), 3)
        pygame.draw.line(self.ecran, (120, 80, 40), (0, haut + 3), (largeur, haut + 3), 2)

        for y in range(haut + 28, haut + HAUTEUR_BARRE, 28):
            pygame.draw.line(self.ecran, (62, 40, 22), (0, y), (largeur, y), 2)       # joints des planches

        if self.phase == "accueil":
            self.ecrire_ombre("Accueil", 20, (255, 235, 170), 14, haut + 14)
            self.ecrire_ombre("Jouer : J ou Entree   Comparer : C   Quitter : Echap", 16, (255, 245, 215), 14, haut + 50)
            self.ecrire_ombre("S : son", 14, (220, 200, 170), 14, haut + 90)
            return
        if self.phase == "menu":
            self.ecrire_ombre("Menu", 20, (255, 235, 170), 14, haut + 14)
            self.ecrire_ombre("Clic, touche 1 a " + str(min(9, len(LEVELS))) + ", ou fleches + Entree", 16, (255, 245, 215), 14, haut + 50)
            self.ecrire_ombre("Tab : changer de personnage   S : son   Echap : accueil", 14, (220, 200, 170), 14, haut + 90)
            return

        # Texte a gauche : niveau, coups (et objectif), algorithme choisi, resultat.
        self.ecrire_ombre("Niveau " + str(self.numero + 1) + " / " + str(len(LEVELS)) + "  " + self.niveau["name"], 18, (255, 235, 170), 14, haut + 10)
        self.ecrire_ombre("Coups : " + str(self.coups) + "   Objectif : " + str(self.optimal), 16, (255, 245, 215), 14, haut + 36)
        nom = ALGOS[self.algo_choisi][0]
        if self.deadlock and ALGOS[self.algo_choisi][1] is not None:
            nom = nom + " + deadlock"
        ligne = "Algo : " + nom + "   Vitesse : " + str(self.vitesse + 1) + "/" + str(len(DELAIS_PAS))
        if self.auto and self.pause:
            ligne = ligne + "   PAUSE"
        elif self.auto and self.phase == "jeu":
            ligne = ligne + "   lecture..."
        self.ecrire_ombre(ligne, 14, (255, 245, 215), 14, haut + 62)
        if self.resultat != "":
            self.ecrire_ombre(self.resultat, 14, (130, 225, 255), 14, haut + 86)
        else:
            self.ecrire_ombre("Choisis un algorithme pour voir sa solution", 14, (220, 200, 170), 14, haut + 86)

        for k in range(len(ALGOS)):
            self.dessiner_bouton(self.boutons_algos[k], ALGOS[k][0])
        if self.deadlock:
            self.dessiner_bouton(self.bouton_deadlock, "Deadlock : oui", True)
        else:
            self.dessiner_bouton(self.bouton_deadlock, "Deadlock : non")
        self.dessiner_bouton(self.bouton_comparer, "Comparer")
        self.dessiner_bouton(self.bouton_annuler, "Annuler")
        self.dessiner_bouton(self.bouton_recommencer, "Recommencer")
        self.dessiner_bouton(self.bouton_menu, "Menu")
        if self.pause:
            self.dessiner_bouton(self.bouton_pause, "Reprendre")
        else:
            self.dessiner_bouton(self.bouton_pause, "Pause")
        self.dessiner_bouton(self.bouton_moins, "-")
        self.dessiner_bouton(self.bouton_plus, "+")
        aide = "Z annuler  R rejouer  B 1 2 3 algo  D deadlock  C comparer  P pause  + - vitesse  Echap menu"
        self.ecran.blit(self.ecrire(aide, 12, (210, 185, 150)), (14, haut + HAUTEUR_BARRE - 18))

    def dessiner_comparaison(self):
        # Tableau "Comparer" : deux groupes de colonnes, SANS deadlock (dore) et AVEC deadlock (vert), chacun avec
        # cout, steps et temps. Sous chaque ligne A*, deux barres de steps (doree = sans, verte = avec).
        largeur = self.monde.get_width()
        planche = pygame.Rect(0, 0, 920, 118 + 46 * (len(self.comparaison) - 1) + 96)
        planche.center = (largeur // 2, self.monde.get_height() // 2)
        self.dessiner_planche(planche, 12)
        self.ecrire_ombre("Comparaison - " + self.niveau["name"], 22, (255, 235, 170), planche.centerx, planche.y + 14, True)

        # Les barres grandissent pendant une demi-seconde ; elles sont proportionnelles au plus grand nombre de steps.
        plus_grand = 1
        for sans, avec in self.barres:
            plus_grand = max(plus_grand, sans)
        croissance = min(1.0, (pygame.time.get_ticks() - self.debut_comparaison) / 600.0)
        longueur_max = planche.width - 48

        # Colonnes : algo, puis 3 colonnes sans deadlock, 3 colonnes avec, puis le gain.
        milieux = []
        for decalage in (80, 195, 295, 395, 535, 635, 735, 850):
            milieux.append(planche.x + decalage)

        # Titres des deux groupes, soulignes de leur couleur.
        y = planche.y + 52
        self.ecrire_ombre("SANS deadlock", 17, COULEUR_SANS_DL, planche.x + 295, y, True)
        self.ecrire_ombre("AVEC deadlock", 17, COULEUR_DL, planche.x + 635, y, True)
        pygame.draw.line(self.ecran, COULEUR_SANS_DL, (planche.x + 150, y + 26), (planche.x + 440, y + 26), 4)
        pygame.draw.line(self.ecran, COULEUR_DL, (planche.x + 490, y + 26), (planche.x + 780, y + 26), 4)

        for i in range(len(self.comparaison)):
            if i == 0:
                y = planche.y + 90
            else:
                y = planche.y + 118 + 46 * (i - 1)
            for j in range(len(milieux)):
                couleur = (255, 245, 215)
                if i == 0:
                    couleur = (255, 225, 120)
                elif j >= 4:
                    couleur = COULEUR_DL
                self.ecrire_ombre(self.comparaison[i][j], 17, couleur, milieux[j], y, True)
            if i > 0:
                sans, avec = self.barres[i - 1]
                pygame.draw.rect(self.ecran, COULEUR_SANS_DL, (planche.x + 24, y + 26, max(2, int(longueur_max * sans / float(plus_grand) * croissance)), 6), 0, 3)
                if avec is not None:
                    pygame.draw.rect(self.ecran, COULEUR_DL, (planche.x + 24, y + 33, max(2, int(longueur_max * avec / float(plus_grand) * croissance)), 6), 0, 3)

        bas = planche.y + 118 + 46 * (len(self.comparaison) - 1)
        self.ecrire_ombre(self.note_comparaison, 14, (130, 225, 255), planche.centerx, bas + 4, True)
        self.ecrire_ombre("barres : steps (doree = sans deadlock, verte = avec)", 14, (230, 205, 160), planche.centerx, bas + 26, True)
        self.ecrire_ombre("(une touche ou un clic pour fermer)", 13, (230, 205, 160), planche.centerx, planche.bottom - 26, True)

    def dessiner_tableau_global(self):
        # Tableau de tous les niveaux : une ligne par niveau ; colonnes BFS, A* h1 h2 h3, puis les memes A* avec
        # detection de deadlock (+DL, en vert). Steps ou temps, au choix (bouton ou touche T).
        largeur = self.monde.get_width()
        hauteur = self.monde.get_height()
        planche = pygame.Rect(10, 10, largeur - 20, hauteur - 20)
        self.dessiner_planche(planche, 12)
        if self.vue_temps:
            titre = "Comparaison de tous les niveaux : temps de calcul (s)"
        else:
            titre = "Comparaison de tous les niveaux : steps (noeuds developpes)"
        self.ecrire_ombre(titre, 20, (255, 235, 170), planche.centerx, planche.y + 12, True)
        self.ecrire_ombre("+DL = avec detection de deadlock (caisses perdues ignorees)", 14, COULEUR_DL, planche.centerx, planche.y + 42, True)

        # Colonnes : niveau (a gauche), cout optimal, puis une colonne par entree de ALGOS_TOUS.
        entetes = ["Niveau", "Cout"]
        milieux = [planche.x + 100, planche.x + 215]
        for k in range(len(ALGOS_TOUS)):
            entetes.append(ALGOS_TOUS[k][0])
            milieux.append(planche.x + 320 + k * 100)
        y = planche.y + 74
        for j in range(len(entetes)):
            couleur = (255, 225, 120)
            if j >= 2 and ALGOS_TOUS[j - 2][2]:
                couleur = COULEUR_DL
            self.ecrire_ombre(entetes[j], 15, couleur, milieux[j], y, True)
        pygame.draw.line(self.ecran, (85, 52, 25), (planche.x + 16, y + 24), (planche.right - 16, y + 24), 3)
        for i in range(len(self.tableau_global)):
            nom, cout, steps, temps = self.tableau_global[i]
            y = planche.y + 106 + 30 * i
            valeurs = [nom, cout]
            for k in range(len(ALGOS_TOUS)):
                if self.vue_temps:
                    valeurs.append("%.3f" % temps[k])
                else:
                    valeurs.append(str(steps[k]))
            for j in range(len(valeurs)):
                couleur = (255, 245, 215)
                if j >= 2 and ALGOS_TOUS[j - 2][2]:
                    couleur = COULEUR_DL
                self.ecrire_ombre(valeurs[j], 15, couleur, milieux[j], y, True)
        if self.vue_temps:
            self.dessiner_bouton(self.bouton_vue, "Voir steps")
        else:
            self.dessiner_bouton(self.bouton_vue, "Voir temps")
        self.dessiner_bouton(self.bouton_fermer, "Fermer")

    def draw(self):
        ecoule = pygame.time.get_ticks() - self.debut_phase
        if self.phase == "accueil" or self.phase == "menu":
            if self.phase == "accueil":
                self.dessiner_accueil()
            else:
                self.dessiner_menu()
            if self.vue_globale:
                self.dessiner_tableau_global()
            self.dessiner_barre()
            self.dessiner_fondu()
            pygame.display.flip()
            return

        if self.phase == "glisse":
            # L'ancien niveau sort a gauche pendant que le nouveau (deja dessine) entre par la droite.
            progression = min(1.0, ecoule / float(DUREE_GLISSE))
            decalage = int(progression * self.monde.get_width())
            self.ecran.blit(self.ancien_monde, (-decalage, 0))
            self.ecran.blit(self.monde, (self.monde.get_width() - decalage, 0))
        else:
            self.dessiner_niveau()
            self.ecran.blit(self.monde, (0, 0))
            self.ecran.blit(self.vignette, (0, 0))

        if self.phase in PHASES_PORTE_OUVERTE:
            # La lumiere reste allumee depuis le moment de la victoire.
            self.dessiner_lumiere(pygame.time.get_ticks() - self.debut_victoire)
        if self.phase == "bravo":
            self.dessiner_confettis(ecoule)
            self.dessiner_pancarte(ecoule)

        if len(self.comparaison) > 0:
            self.dessiner_comparaison()
        self.dessiner_barre()
        self.dessiner_message()
        self.dessiner_fondu()
        pygame.display.flip()

    def dessiner_message(self):
        # Petit panneau en haut de la zone de jeu, qui disparait tout seul.
        if pygame.time.get_ticks() > self.fin_message:
            return
        image = self.ecrire(self.message, 18, (255, 245, 215))
        planche = pygame.Rect(0, 0, image.get_width() + 40, 44)
        planche.midtop = (self.monde.get_width() // 2, 12)
        self.dessiner_planche(planche, 10)
        self.ecrire_ombre(self.message, 18, (255, 245, 215), planche.centerx, planche.y + 8, True)

    def dessiner_fondu(self):
        # Au debut d'un ecran, un voile noir de plus en plus transparent : l'ecran apparait en douceur.
        age = pygame.time.get_ticks() - self.debut_fondu
        if age < DUREE_FONDU:
            voile = pygame.Surface(self.ecran.get_size())
            voile.set_alpha(int(255 * (1 - age / float(DUREE_FONDU))))
            self.ecran.blit(voile, (0, 0))
