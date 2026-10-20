# Interface Pygame du jeu (classe Game).
# - menu de choix du niveau, avec un apercu de chaque niveau (au lancement, ou touche M / bouton "Menu") ;
# - rendu d'un niveau avec les sprites du pack, decor autour et effets (lucioles, etincelles) ;
# - jeu manuel : le chat et les caisses glissent d'une case a l'autre, compteur de coups,
#   annuler (Z), recommencer ;
# - bouton "Resoudre (BFS)" : cout, steps (noeuds developpes) et temps de calcul, puis trajectoire tracee
#   et lecture automatique de la solution ;
# - fin de niveau : la porte s'ouvre et s'illumine, le chat va devant la porte et remue la queue,
#   une pancarte "Bravo" descend avec ses boutons (Rejouer, Niveau suivant, Menu) ;
# - sons crees par le code (ambiance de prairie, bruit de pas), touche S pour couper.

import math
import random
import time
from collections import deque
import pygame

from levels import LEVELS
from sokoban import SokobanPuzzle, ACTIONS
from search import BFS
from assets_loader import load_sprites, load_sounds

TAILLE = 44            # taille d'une case en pixels
MARGE = 2              # marge autour du plus grand niveau, en nombre de cases (sert de decor)
HAUTEUR_BARRE = 112    # hauteur de la barre d'infos en bas de la fenetre, en pixels
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
DUREE_GLISSE = 900       # le glissement vers le niveau suivant

# La porte est ouverte (et la lumiere allumee) pendant toutes ces phases.
PHASES_PORTE_OUVERTE = ("ouverture", "marche", "queue", "bravo")

# Temps entre deux pas quand le programme joue la solution tout seul, en millisecondes.
DELAI_PAS = 260
COULEUR_TRAJET = (90, 210, 255)

# Effets du decor vivant.
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


def creer_halo(rayon, couleur, opacite):
    # Disque flou : opaque au centre (opacite entre 0 et 255), transparent au bord.
    # On dessine des cercles de plus en plus petits et de plus en plus opaques les uns sur les autres.
    image = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
    for k in range(rayon, 0, -1):
        alpha = int(opacite * (1 - k / float(rayon)))
        pygame.draw.circle(image, (couleur[0], couleur[1], couleur[2], alpha), (rayon, rayon), k)
    return image


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
            colonnes_max = max(colonnes_max, len(niveau["grid"][0]))
        self.cases_largeur = colonnes_max + 2 * MARGE
        self.cases_hauteur = lignes_max + 2 * MARGE
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
        self.polices = {}     # polices deja creees, rangees par taille (voir ecrire)

        # Sons : dictionnaire vide si l'ordinateur n'a pas de carte son (le jeu marche quand meme).
        self.sons = load_sounds()
        self.son_actif = False
        self.changer_son()

        # Les quatre boutons de la barre d'infos (rectangles cliquables).
        self.bouton_resoudre = pygame.Rect(14, hauteur + 56, 176, 34)
        self.bouton_annuler = pygame.Rect(202, hauteur + 56, 120, 34)
        self.bouton_recommencer = pygame.Rect(334, hauteur + 56, 150, 34)
        self.bouton_menu = pygame.Rect(496, hauteur + 56, 106, 34)

        # Cartes du menu : une par niveau, sur deux colonnes, au milieu de la zone de jeu.
        self.boutons_niveaux = []
        for i in range(len(LEVELS)):
            colonne = i % 2
            ligne = i // 2
            x = largeur // 2 - 266 + colonne * 272
            y = 190 + ligne * 74
            self.boutons_niveaux.append(pygame.Rect(x, y, 260, 62))
        self.choix_menu = 0     # carte selectionnee (souris ou fleches du clavier)

        # Pancarte "Bravo" (au milieu de la zone de jeu) et ses trois boutons, a leur place finale.
        centre_x = largeur // 2
        self.pancarte = pygame.Rect(centre_x - 230, hauteur // 2 - 100, 460, 190)
        self.bouton_rejouer = pygame.Rect(centre_x - 215, hauteur // 2 + 25, 130, 42)
        self.bouton_suivant = pygame.Rect(centre_x - 75, hauteur // 2 + 25, 170, 42)
        self.bouton_menu_bravo = pygame.Rect(centre_x + 105, hauteur // 2 + 25, 110, 42)

        # Le niveau est dessine sur "monde", puis recopie sur l'ecran (pratique pour faire glisser).
        self.monde = pygame.Surface((largeur, hauteur))
        self.ancien_monde = None
        # Fond du menu (herbe et haie), dessine une seule fois.
        self.dessiner_herbe()
        self.dessiner_haie()
        self.fond_menu = self.monde.copy()
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
        self.preparer_fond()
        # Phase : "menu" (choix du niveau), "jeu", puis la fin de niveau : "ouverture" (porte + lumiere),
        # "marche" et "queue" (le chat va a la porte), "bravo" (pancarte), "glisse" (vers le niveau suivant).
        self.phase = "jeu"
        self.debut_phase = 0
        self.debut_victoire = 0    # moment ou la porte s'est ouverte (pour la lumiere)
        self.chemin_chat = []      # cases que le chat traverse pour aller a la porte
        self.coups = 0          # nombre de deplacements faits (a la main ou par la lecture automatique)
        self.historique = []    # etats precedents, pour annuler un coup (touche Z)
        self.particules = []    # etincelles et poussiere : [x, y, vx, vy, naissance, couleur]

        # Animation du dernier deplacement : le chat glisse de anim_joueur[0] a anim_joueur[1],
        # et la caisse poussee (s'il y en a une) de anim_caisse[0] a anim_caisse[1].
        self.anim_debut = -DUREE_MOUVEMENT
        self.anim_joueur = None
        self.anim_caisse = None
        self.anim_direction = (0, 0)
        self.regarde_gauche = False     # le chat est dessine tourne vers la gauche
        self.action_en_attente = None   # touche appuyee pendant une animation : jouee juste apres
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
        # La carte du niveau qu'on quitte est deja selectionnee.
        self.annuler_solution()
        self.ancien_monde = None
        self.choix_menu = self.numero
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
            self.horloge.tick(60)      # 60 images par seconde : animations fluides
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
                if evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_n) and self.phase == "bravo":
                    self.niveau_suivant()
                if evenement.key == pygame.K_b and self.phase == "jeu":
                    self.resoudre()
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
                if self.bouton_resoudre.collidepoint(evenement.pos) and self.phase == "jeu":
                    self.resoudre()
                if self.bouton_annuler.collidepoint(evenement.pos) and self.phase == "jeu":
                    self.annuler_coup()
                if self.bouton_menu.collidepoint(evenement.pos):
                    self.ouvrir_menu()
                if self.phase == "bravo":
                    self.clic_pancarte(evenement.pos)

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
        # Dans le menu : clic sur une carte, touche 1 a 8, ou fleches + Entree ; Echap quitte le jeu.
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                self.en_cours = False
            if evenement.key == pygame.K_s:
                self.changer_son()
            if evenement.unicode.isdigit():
                numero = int(evenement.unicode) - 1
                if 0 <= numero < len(LEVELS):
                    self.charger_niveau(numero)
            # Fleches : on se deplace dans la grille de cartes (2 colonnes).
            deplacements = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1, pygame.K_UP: -2, pygame.K_DOWN: 2}
            if evenement.key in deplacements:
                nouveau = self.choix_menu + deplacements[evenement.key]
                if 0 <= nouveau < len(LEVELS):
                    self.choix_menu = nouveau
            if evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.charger_niveau(self.choix_menu)
        if evenement.type == pygame.MOUSEMOTION:
            for i in range(len(self.boutons_niveaux)):
                if self.boutons_niveaux[i].collidepoint(evenement.pos):
                    self.choix_menu = i
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            for i in range(len(self.boutons_niveaux)):
                if self.boutons_niveaux[i].collidepoint(evenement.pos):
                    self.charger_niveau(i)

    def bouger(self, action):
        # Un deplacement (touche flechee ou lecture automatique de la solution).
        # On ne re-ecrit AUCUNE regle ici : on demande a successorFunction la liste des coups possibles
        # et on prend celui qui correspond a la touche. Le reste ne sert qu'a l'animation.
        dr, dc = ACTIONS[action]
        if dc != 0:
            self.regarde_gauche = dc < 0
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
                # Si une caisse etait sur la case d'arrivee, c'est qu'elle a ete poussee d'une case.
                case = ancien.grid[arrivee[0]][arrivee[1]]
                if case == "B" or case == "*":
                    caisse = (arrivee[0] + dr, arrivee[1] + dc)
                    self.anim_caisse = (arrivee, caisse)
                    # Un peu de poussiere derriere la caisse poussee, et des etincelles si elle arrive sur une cible.
                    self.ajouter_particules(arrivee, 5, (200, 190, 160), 60)
                    if suivant.grid[caisse[0]][caisse[1]] == "*":
                        self.ajouter_particules(caisse, 16, (255, 220, 90), 180)
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

    def resoudre(self):
        # Lance le BFS depuis la position actuelle, mesure le temps de calcul, trace la trajectoire
        # du chat (positions de chaque etat du chemin) et demarre la lecture automatique.
        self.annuler_solution()
        debut = time.time()
        noeud, steps = BFS(self.etat, lambda s: s.successorFunction(), lambda s: s.isGoal())
        duree = time.time() - debut
        # cout = longueur de la solution ; steps = noeuds developpes par le BFS (travail de la recherche).
        if noeud is None:
            self.resultat = "BFS : aucune solution | " + str(steps) + " steps"
        else:
            self.solution = noeud.getSolution()
            self.trajectoire = [etat.player_pos for etat in noeud.getPath()]
            self.auto = True
            self.dernier_pas = pygame.time.get_ticks()
            self.resultat = "BFS : cout " + str(noeud.g) + " | " + str(steps) + " steps | " + "%.3f" % duree + " s"

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
            elif self.auto and pygame.time.get_ticks() - self.dernier_pas >= DELAI_PAS:
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
        grille = self.etat.grid
        r = wr - self.decalage_ligne
        c = wc - self.decalage_colonne
        if r < 0 or r >= len(grille) or c < 0 or c >= len(grille[r]):
            return True
        return grille[r][c] == "O" and not touche_le_sol(grille, r, c)

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
            for dc in (-1, 0, 1):
                self.cases_decor.append((self.porte[0] + self.decalage_ligne - 1, self.porte[1] + self.decalage_colonne + dc))
            for sens in (-1, 1):
                for distance in (3, 2):
                    colonne = self.porte[1] + sens * distance
                    if self.mur_visible(self.porte[0], colonne):
                        self.poser("totem", self.porte[0] + self.decalage_ligne - 1, colonne + self.decalage_colonne)
                        break

        # Sous le niveau : un banc au milieu, des vases a gauche, des tonneaux a droite.
        grille = self.etat.grid
        bas = min(self.decalage_ligne + len(grille), bas_fenetre)
        gauche = self.decalage_colonne
        droite = self.decalage_colonne + len(grille[0]) - 1
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
                        self.monde.blit(self.sprites["mur" + str(1 + (r + c) % 2)], (x, y))
                else:
                    # Toutes les autres cases sont du sol de jeu (dalle de pierre) ; l'herbe reste a l'exterieur.
                    self.monde.blit(self.sprites["sol" + str(1 + (r * 3 + c * 5) % 2)], (x, y))
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
                    self.monde.blit(self.sprites["caisse"], (x, y))
                    if case == "*":
                        # Caisse bien placee : contour vert, pour la reperer de loin.
                        pygame.draw.rect(self.monde, COULEUR_BON, (x, y, TAILLE, TAILLE), 3, 6)

        # Le chat par-dessus (pendant la marche vers la porte, il est dessine a part, voir plus bas).
        if self.phase != "marche" and self.phase != "queue":
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
        if self.phase == "marche" or self.phase == "queue":
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
        if self.anim_joueur is not None and self.anim_joueur[1] == (r, c) and self.en_mouvement():
            t = (pygame.time.get_ticks() - self.anim_debut) / float(DUREE_MOUVEMENT)
            if self.anim_joueur[0] != self.anim_joueur[1]:
                x, y = self.glisser(self.anim_joueur[0], self.anim_joueur[1], self.avancement())
                saut = int(math.sin(math.pi * t) * 6)
            else:
                choc = math.sin(math.pi * t) * 5
                x = x + int(self.anim_direction[1] * choc)
                y = y + int(self.anim_direction[0] * choc)

        image = self.sprites["joueur"]
        if not self.en_mouvement():
            # A l'arret, le chat respire (il monte et descend d'un pixel) et remue la queue de temps en temps.
            maintenant = pygame.time.get_ticks()
            y = y + int(round(math.sin(maintenant / 350.0)))
            if maintenant % 4000 < 600:
                image = self.sprites["joueur_queue" + str(1 + (maintenant // 150) % 2)]
        self.poser_chat(image, x, y, saut)

    def poser_chat(self, image, x, y, saut):
        # Dessine le chat dans la case dont le coin haut gauche est (x, y), tourne du bon cote,
        # avec son ombre sous les pattes (plus petite quand il est en l'air, saut = hauteur du saut).
        if self.regarde_gauche:
            image = pygame.transform.flip(image, True, False)
        self.dessiner_ombre(x + TAILLE // 2, y + TAILLE - 4, TAILLE * 2 // 3 - saut * 2)
        # Le chat est plus haut qu'une case : on aligne ses pieds sur le bas de la case.
        self.monde.blit(image, (x + (TAILLE - image.get_width()) // 2, y + TAILLE - image.get_height() - saut))

    def dessiner_chat_sortie(self):
        # Le chat glisse d'une case a la suivante le long de self.chemin_chat, en faisant de petits sauts,
        # puis il remue la queue devant la porte.
        ecoule = pygame.time.get_ticks() - self.debut_phase
        chemin = self.chemin_chat
        rang = ecoule / float(DELAI_CASE)
        if self.phase == "queue" or rang > len(chemin) - 1:
            rang = len(chemin) - 1.0
        i = int(rang)
        suivante = min(i + 1, len(chemin) - 1)
        x, y = self.glisser(chemin[i], chemin[suivante], rang - i)

        image = self.sprites["joueur"]
        saut = 0
        if self.phase == "queue":
            image = self.sprites["joueur_queue" + str(1 + (ecoule // 150) % 2)]
        else:
            saut = int(abs(math.sin(ecoule / 90.0)) * 4)
            if chemin[suivante][1] != chemin[i][1]:
                self.regarde_gauche = chemin[suivante][1] < chemin[i][1]
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

        texte = "Niveau " + str(self.numero + 1) + " reussi en " + str(self.coups) + " coups"
        self.ecrire_ombre("BRAVO !", 56, (255, 235, 170), planche.centerx, y + 12, True)
        self.ecrire_ombre(texte, 20, (255, 240, 200), planche.centerx, y + 80, True)

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

    def dessiner_menu(self):
        # Menu : herbe et haie (avec les lucioles), une grande planche avec le titre,
        # puis une carte par niveau : apercu du niveau, numero et nom.
        self.monde.blit(self.fond_menu, (0, 0))
        self.dessiner_effets()
        self.ecran.blit(self.monde, (0, 0))

        largeur = self.monde.get_width()
        lignes = (len(LEVELS) + 1) // 2
        self.dessiner_planche(pygame.Rect(largeur // 2 - 290, 60, 580, 130 + 74 * lignes + 10), 14)
        self.ecrire_ombre("SOKOBAN", 64, (255, 235, 170), largeur // 2, 74, True)
        self.ecrire_ombre("Choisis un niveau", 22, (255, 240, 200), largeur // 2, 146, True)

        for i in range(len(LEVELS)):
            carte = self.boutons_niveaux[i]
            fond = (120, 78, 38)
            bord = (200, 160, 100)
            if i == self.choix_menu:
                # La carte choisie se souleve un peu, plus claire, avec un contour dore.
                carte = carte.move(0, -3)
                fond = (175, 120, 65)
                bord = (255, 225, 120)
            pygame.draw.rect(self.ecran, (60, 38, 18), carte.move(0, 4), 0, 8)     # epaisseur sous la carte
            pygame.draw.rect(self.ecran, fond, carte, 0, 8)
            pygame.draw.rect(self.ecran, bord, carte, 3, 8)

            # Apercu du niveau a gauche de la carte, centre dans un carre de 50 x 50.
            grille = LEVELS[i]["grid"]
            cote = 50 // max(len(grille), len(grille[0]))
            self.dessiner_apercu(grille, carte.x + 8 + (50 - cote * len(grille[0])) // 2, carte.y + 6 + (50 - cote * len(grille)) // 2, cote)
            self.ecrire_ombre(str(i + 1), 28, (255, 225, 120), carte.x + 70, carte.y + 14)
            self.ecrire_ombre(LEVELS[i]["name"], 18, (255, 245, 215), carte.x + 108, carte.y + 21)

    def dessiner_bouton(self, rectangle, texte):
        # Bouton en bois avec un peu de relief : plus clair sous la souris, enfonce quand on clique.
        souris = pygame.mouse.get_pos()
        survole = rectangle.collidepoint(souris)
        enfonce = survole and pygame.mouse.get_pressed()[0]
        couleur = (150, 100, 52)
        if survole:
            couleur = (185, 128, 70)
        pygame.draw.rect(self.ecran, (60, 38, 18), rectangle.move(0, 3), 0, 8)    # epaisseur du bouton
        if enfonce:
            rectangle = rectangle.move(0, 2)
        pygame.draw.rect(self.ecran, couleur, rectangle, 0, 8)
        pygame.draw.line(self.ecran, (215, 165, 105), (rectangle.x + 8, rectangle.y + 3), (rectangle.right - 8, rectangle.y + 3), 2)
        pygame.draw.rect(self.ecran, (230, 200, 130), rectangle, 2, 8)
        image = self.ecrire(texte, 16, (255, 245, 215))
        self.ecran.blit(image, (rectangle.x + (rectangle.width - image.get_width()) // 2, rectangle.y + (rectangle.height - image.get_height()) // 2))

    def dessiner_barre(self):
        # Barre d'infos en bas : niveau et coups, resultat du BFS (ou une astuce), boutons, rappel des touches.
        haut = self.monde.get_height()
        largeur = self.ecran.get_width()
        # Fond en bois sombre, avec un filet dore en haut.
        pygame.draw.rect(self.ecran, (72, 47, 26), (0, haut, largeur, HAUTEUR_BARRE))
        pygame.draw.line(self.ecran, (230, 200, 130), (0, haut), (largeur, haut), 3)
        pygame.draw.line(self.ecran, (120, 80, 40), (0, haut + 3), (largeur, haut + 3), 2)

        if self.phase == "menu":
            self.ecrire_ombre("Menu", 20, (255, 235, 170), 14, haut + 12)
            self.ecrire_ombre("Clic, touche 1 a " + str(len(LEVELS)) + ", ou fleches + Entree", 16, (255, 245, 215), 14, haut + 44)
            self.ecrire_ombre("S : son   Echap : quitter", 14, (220, 200, 170), 14, haut + 88)
            return

        self.ecrire_ombre("Niveau " + str(self.numero + 1) + " / " + str(len(LEVELS)) + "  " + self.niveau["name"], 18, (255, 235, 170), 14, haut + 10)
        coups = self.ecrire("Coups : " + str(self.coups), 18, (255, 245, 215))
        self.ecrire_ombre("Coups : " + str(self.coups), 18, (255, 245, 215), largeur - coups.get_width() - 14, haut + 10)
        if self.resultat != "":
            self.ecrire_ombre(self.resultat, 16, (130, 225, 255), 14, haut + 34)
        else:
            self.ecrire_ombre("Astuce : B pour voir la solution du BFS", 16, (220, 200, 170), 14, haut + 34)

        self.dessiner_bouton(self.bouton_resoudre, "Resoudre (BFS)")
        self.dessiner_bouton(self.bouton_annuler, "Annuler")
        self.dessiner_bouton(self.bouton_recommencer, "Recommencer")
        self.dessiner_bouton(self.bouton_menu, "Menu")
        aide = "Fleches: bouger  Z: annuler  R: rejouer  B: BFS  M: menu  S: son"
        self.ecran.blit(self.ecrire(aide, 12, (210, 185, 150)), (14, haut + 96))

    def draw(self):
        ecoule = pygame.time.get_ticks() - self.debut_phase
        if self.phase == "menu":
            self.dessiner_menu()
            self.dessiner_barre()
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

        if self.phase in PHASES_PORTE_OUVERTE:
            # La lumiere reste allumee depuis le moment de la victoire.
            self.dessiner_lumiere(pygame.time.get_ticks() - self.debut_victoire)
        if self.phase == "bravo":
            self.dessiner_pancarte(ecoule)

        self.dessiner_barre()
        pygame.display.flip()
