# Chargement et decoupage des sprites utilises par la GUI.
# Les images viennent du pack "Pixel Art Top Down - Basic" (dossier assets/, ne pas modifier).
# Chaque sprite est decoupe dans une feuille avec un rectangle (x, y, largeur, hauteur)
# trouve a la main en regardant la feuille.

import math
import os
import random
from array import array
import pygame

# Chemin a partir du dossier de ce fichier : le jeu marche meme lance depuis un autre dossier.
DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Pixel Art Top Down - Basic v1.2.3", "Texture") + os.sep
DOSSIER_OMBRES = DOSSIER + "Extra/"   # memes feuilles, mais avec les ombres au sol

# Pour rendre l'herbe aussi vive que dans l'apercu du pack (on ajoute ces valeurs R, V, B a chaque pixel).
ECLAIRCIR_HERBE = (30, 32, 0)
ECLAIRCIR_MUR = (45, 38, 28)


def charger_feuille(nom, dossier=DOSSIER):
    # convert_alpha garde la transparence des images PNG.
    return pygame.image.load(dossier + nom).convert_alpha()


def decouper(feuille, x, y, largeur, hauteur, taille):
    # Decoupe un rectangle dans une feuille et le met en carre taille x taille.
    morceau = feuille.subsurface(pygame.Rect(x, y, largeur, hauteur))
    return pygame.transform.scale(morceau, (taille, taille))


def decouper_hauteur(feuille, x, y, largeur, hauteur, hauteur_voulue):
    # Pareil, mais on garde les proportions : on fixe seulement la hauteur finale.
    morceau = feuille.subsurface(pygame.Rect(x, y, largeur, hauteur))
    largeur_voulue = largeur * hauteur_voulue // hauteur
    return pygame.transform.scale(morceau, (largeur_voulue, hauteur_voulue))


def creer_joueur(taille, queue):
    # Petit chat orange dessine avec pygame.draw (le pack n'a qu'un bloc de pierre rectangulaire),
    # avec un chapeau vert pointu. queue = 0, 1 ou 2 : trois positions de la queue (pour la faire bouger).
    u = taille / 48.0
    image = pygame.Surface((taille, int(taille * 1.2)), pygame.SRCALPHA)
    orange = (235, 150, 70)
    clair = (250, 225, 190)
    contour = (95, 55, 25)

    def p(x, y):
        return (int(x * u), int(y * u))

    # Queue : chaque position est une petite ligne brisee.
    queues = [[(34, 52), (44, 47), (44, 38)], [(34, 52), (46, 51), (47, 43)], [(34, 52), (42, 45), (38, 37)]]
    points = [p(x, y) for (x, y) in queues[queue]]
    pygame.draw.lines(image, contour, False, points, int(7 * u))
    pygame.draw.lines(image, orange, False, points, int(4 * u))

    # Corps avec un ventre clair.
    pygame.draw.ellipse(image, contour, (int(10 * u), int(34 * u), int(28 * u), int(22 * u)))
    pygame.draw.ellipse(image, orange, (int(12 * u), int(36 * u), int(24 * u), int(18 * u)))
    pygame.draw.ellipse(image, clair, (int(18 * u), int(41 * u), int(12 * u), int(12 * u)))

    # Oreilles puis tete.
    for oreille in ([(9, 28), (10, 14), (21, 22)], [(39, 28), (38, 14), (27, 22)]):
        points = [p(x, y) for (x, y) in oreille]
        pygame.draw.polygon(image, orange, points)
        pygame.draw.polygon(image, contour, points, 2)
    pygame.draw.circle(image, contour, p(24, 30), int(16 * u))
    pygame.draw.circle(image, orange, p(24, 30), int(14 * u))
    pygame.draw.ellipse(image, clair, (int(16 * u), int(33 * u), int(16 * u), int(11 * u)))

    # Grands yeux verts, nez rose.
    for x in (17, 31):
        pygame.draw.circle(image, (255, 255, 255), p(x, 31), int(4 * u))
        pygame.draw.circle(image, (60, 160, 80), p(x, 31), int(3 * u))
        pygame.draw.circle(image, (20, 20, 20), p(x, 31), int(1.5 * u) + 1)
    pygame.draw.circle(image, (255, 130, 150), p(24, 37), int(2 * u) + 1)

    # Chapeau vert pointu avec un bandeau clair.
    chapeau = [p(9, 26), p(39, 26), p(36, 13), p(33, 3), p(21, 9)]
    pygame.draw.polygon(image, (50, 160, 60), chapeau)
    pygame.draw.polygon(image, (20, 85, 30), chapeau, 2)
    pygame.draw.rect(image, (235, 220, 120), (int(9 * u), int(23 * u), int(30 * u), int(5 * u)))
    return image


def load_sprites(taille):
    # Charge les feuilles de sprites et retourne un dictionnaire d'images.
    # Doit etre appele apres pygame.display.set_mode (convert_alpha en a besoin).
    sprites = {}

    herbe = charger_feuille("TX Tileset Grass.png")
    sprites["herbe"] = decouper(herbe, 0, 0, 32, 32, taille)
    sprites["herbe_fleurs"] = decouper(herbe, 125, 35, 32, 32, taille)
    sprites["herbe"].fill(ECLAIRCIR_HERBE, special_flags=pygame.BLEND_RGB_ADD)
    sprites["herbe_fleurs"].fill(ECLAIRCIR_HERBE, special_flags=pygame.BLEND_RGB_ADD)

    # Sol de jeu : dalles de pierre claire (plain et avec un clou), l'herbe reste a l'exterieur.
    sol_pierre = charger_feuille("TX Tileset Stone Ground.png")
    sprites["sol1"] = decouper(sol_pierre, 16, 16, 32, 32, taille)
    sprites["sol2"] = decouper(sol_pierre, 177, 14, 32, 32, taille)
    for nom in ("sol1", "sol2"):
        pygame.draw.rect(sprites[nom], (95, 90, 75), (0, 0, taille, taille), 1)   # fin contour : on voit les cases

    # Murs : blocs de 64x64 de la feuille des murs (dessus clair, briques, bas), 2 variantes.
    # Eclaircis par code pour rester lisibles sur l'herbe vive.
    mur = charger_feuille("TX Tileset Wall.png")
    sprites["mur1"] = decouper(mur, 32, 288, 64, 64, taille)
    sprites["mur2"] = decouper(mur, 128, 288, 64, 64, taille)
    sprites["mur1"].fill(ECLAIRCIR_MUR, special_flags=pygame.BLEND_RGB_ADD)
    sprites["mur2"].fill(ECLAIRCIR_MUR, special_flags=pygame.BLEND_RGB_ADD)

    props = charger_feuille("TX Props.png")
    sprites["caisse"] = decouper(props, 160, 18, 32, 23, taille)

    sprites["joueur"] = creer_joueur(taille, 0)
    sprites["joueur_queue1"] = creer_joueur(taille, 1)    # positions de la queue qui bouge
    sprites["joueur_queue2"] = creer_joueur(taille, 2)

    # Decor autour du niveau : feuilles "avec ombres", proportions gardees (on fixe la hauteur).
    props_ombres = charger_feuille("TX Props with Shadow.png", DOSSIER_OMBRES)
    # Buissons choisis par l'equipe (feuille des plantes sans ombre) et petites touffes d'herbe.
    plantes_sans_ombre = charger_feuille("TX Plant.png")
    sprites["buisson"] = decouper_hauteur(plantes_sans_ombre, 98, 195, 27, 25, taille * 3 // 4)
    sprites["buisson2"] = decouper_hauteur(plantes_sans_ombre, 156, 190, 38, 32, taille)
    touffes = [(74, 427, 13, 9), (102, 394, 15, 11), (73, 394, 15, 10), (41, 394, 16, 10), (8, 394, 17, 9)]
    for k in range(len(touffes)):
        x, y, largeur, hauteur = touffes[k]
        sprites["touffe" + str(k)] = decouper_hauteur(plantes_sans_ombre, x, y, largeur, hauteur, hauteur * 2)
    # Arbres (feuille des plantes, sans ombre : la GUI dessine leur ombre).
    sprites["arbre1"] = decouper_hauteur(plantes_sans_ombre, 24, 14, 114, 142, taille * 3)
    sprites["arbre2"] = decouper_hauteur(plantes_sans_ombre, 160, 16, 100, 140, taille * 3)
    sprites["arbre3"] = decouper_hauteur(plantes_sans_ombre, 292, 28, 84, 126, taille * 5 // 2)

    # Decor (feuille "avec ombres") et la porte de sortie.
    # (rectangles trouves en regardant les feuilles, hauteur voulue ensuite ; les proportions sont gardees)
    sprites["totem"] = decouper_hauteur(props_ombres, 348, 170, 44, 90, taille * 2)
    sprites["tonneau"] = decouper_hauteur(props_ombres, 160, 150, 36, 42, taille)
    sprites["statue"] = decouper_hauteur(props_ombres, 440, 16, 48, 80, taille * 2)
    sprites["banc"] = decouper_hauteur(props_ombres, 288, 16, 64, 48, taille)
    sprites["coffre"] = decouper_hauteur(props_ombres, 96, 26, 36, 38, taille)
    sprites["panneau"] = decouper_hauteur(props_ombres, 96, 160, 34, 34, taille)
    sprites["vase"] = decouper_hauteur(props_ombres, 160, 214, 32, 40, taille)
    sprites["pot"] = decouper_hauteur(props_ombres, 160, 284, 32, 34, taille * 3 // 4)
    sprites["vase2"] = decouper_hauteur(props_ombres, 160, 344, 32, 42, taille)
    sprites["rocher"] = decouper_hauteur(props_ombres, 0, 426, 64, 52, taille * 5 // 4)
    sprites["caillou"] = decouper_hauteur(props_ombres, 128, 476, 34, 32, taille * 2 // 3)
    sprites["caillou2"] = decouper_hauteur(props_ombres, 66, 480, 28, 26, taille // 2)
    sprites["pilier_casse"] = decouper_hauteur(props_ombres, 414, 190, 36, 62, taille * 3 // 2)
    sprites["lanterne"] = decouper_hauteur(props_ombres, 448, 114, 32, 44, taille)
    sprites["porte"] = decouper_hauteur(props_ombres, 27, 101, 42, 54, taille * 5 // 4)   # sortie du niveau
    sprites["porte_ouverte"] = decouper_hauteur(props_ombres, 27, 164, 42, 58, taille * 5 // 4)

    # Arche en pierre (feuille des structures) : elle encadre seulement la porte de sortie.
    structures = charger_feuille("TX Struct.png")
    sprites["arche_porte"] = decouper_hauteur(structures, 408, 27, 80, 64, taille * 2)

    return sprites


# ---------------------------------------------------------------------------------------------
# Sons : ils sont calcules par le code, echantillon par echantillon,
# il n'y a aucun fichier audio. Un echantillon = un nombre entre -32767 et 32767.


def faire_son(echantillons):
    # Transforme une liste de valeurs entre -1 et 1 en son pygame (16 bits signes).
    # Si le mixer est en stereo, on ecrit chaque echantillon deux fois (gauche et droite).
    canaux = pygame.mixer.get_init()[2]
    donnees = array("h")
    for valeur in echantillons:
        valeur = max(-1.0, min(1.0, valeur))
        for k in range(canaux):
            donnees.append(int(valeur * 32767))
    return pygame.mixer.Sound(buffer=donnees.tobytes())


def creer_ambiance(frequence):
    # Ambiance de prairie de 6 secondes, jouee en boucle : du vent (bruit aleatoire adouci)
    # qui monte et descend, et quelques chants d'oiseau.
    duree = 6.0
    total = int(frequence * duree)
    hasard = random.Random(7)       # graine fixe : le son est toujours le meme
    echantillons = []
    adouci = 0.0
    for i in range(total):
        t = i / float(frequence)
        # Le vent : on adoucit le bruit (filtre passe-bas tout simple) pour qu'il souffle au lieu de gresiller.
        adouci = adouci + 0.03 * (hasard.uniform(-1, 1) - adouci)
        # Le volume du vent passe par 0 au debut et a la fin : la boucle ne fait pas de "clic".
        rafale = math.sin(math.pi * t / duree) ** 2
        echantillons.append(adouci * 1.6 * (0.3 + 0.7 * rafale))

    # Chants d'oiseau : de petits "cui" (note qui monte vite), a deux moments de la boucle.
    for debut in (1.3, 1.5, 1.7, 4.2, 4.4):
        depart = int(debut * frequence)
        longueur = int(0.09 * frequence)
        phase = 0.0
        for i in range(longueur):
            avance = i / float(longueur)
            note = 2600 + 1400 * avance
            phase = phase + 2 * math.pi * note / frequence
            enveloppe = math.sin(math.pi * avance)
            echantillons[depart + i] = echantillons[depart + i] + 0.12 * enveloppe * math.sin(phase)
    return faire_son(echantillons)


def creer_pas(frequence):
    # Bruit de pas : un petit "pof" tres court (bruit adouci qui s'eteint vite).
    total = int(frequence * 0.08)
    hasard = random.Random(3)
    echantillons = []
    adouci = 0.0
    for i in range(total):
        adouci = adouci + 0.25 * (hasard.uniform(-1, 1) - adouci)
        enveloppe = math.exp(-i / (total / 5.0))
        echantillons.append(adouci * 1.2 * enveloppe)
    return faire_son(echantillons)


def load_sounds():
    # Retourne un dictionnaire de sons, ou un dictionnaire vide si l'ordinateur n'a pas de son
    # (le jeu marche alors sans son). Doit etre appele apres pygame.init().
    if not pygame.mixer.get_init():
        return {}
    frequence = pygame.mixer.get_init()[0]
    sons = {}
    sons["ambiance"] = creer_ambiance(frequence)
    sons["pas"] = creer_pas(frequence)
    sons["ambiance"].set_volume(0.35)
    sons["pas"].set_volume(0.5)
    return sons
