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
DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(DOSSIER_PROJET, "assets", "Pixel Art Top Down - Basic v1.2.3", "Texture") + os.sep
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


def charger_jack(sprites, hauteur_voulue):
    # Jack le chat : njack.png est une planche de poses (avec des titres ecrits dessus). Chaque pose est un rectangle
    # (x, y, largeur, hauteur) trouve a la main. Toutes les poses sont reduites du meme facteur
    # (la pose de face fait hauteur_voulue pixels de haut).
    feuille = pygame.image.load(os.path.join(DOSSIER_PROJET, "assets", "njack.png")).convert_alpha()
    poses = {
        "jack_face": (19, 29, 66, 77),
        "jack_content": (107, 29, 62, 77),
        "jack_queue1": (295, 30, 73, 76),      # de face, la queue remue
        "jack_queue2": (382, 30, 71, 76),
        "jack_dos": (2, 243, 57, 70),
    }
    # Marche de profil : 4 images vers la gauche et 4 vers la droite (elles alternent dans la planche).
    x_marche = [6, 103, 199, 292, 410, 507, 602, 699]
    for k in range(4):
        poses["jack_gauche" + str(k)] = (x_marche[2 * k], 135, 88, 80)
        poses["jack_droite" + str(k)] = (x_marche[2 * k + 1], 135, 88, 80)
    facteur = hauteur_voulue / 77.0
    for nom in poses:
        x, y, largeur, hauteur = poses[nom]
        morceau = feuille.subsurface(pygame.Rect(x, y, largeur, hauteur))
        morceau = morceau.subsurface(morceau.get_bounding_rect())      # on enleve les bords vides
        taille = (int(morceau.get_width() * facteur), int(morceau.get_height() * facteur))
        sprites[nom] = pygame.transform.smoothscale(morceau, taille)


def charger_pingouin(sprites, hauteur_voulue):
    # Pingouin de pingu.png : une feuille de 4 images (face, droite, dos, gauche) sur fond blanc.
    # Le fond blanc est rendu transparent en partant des bords (le blanc du visage est entoure de noir : il reste).
    chemin = os.path.join(DOSSIER_PROJET, "assets", "Pixel Art Top Down - Basic v1.2.3", "pingu.png")
    feuille = pygame.image.load(chemin).convert_alpha()
    largeur, haut = feuille.get_size()
    a_voir = []
    for x in range(largeur):
        a_voir.append((x, 0))
        a_voir.append((x, haut - 1))
    for y in range(haut):
        a_voir.append((0, y))
        a_voir.append((largeur - 1, y))
    while len(a_voir) > 0:
        x, y = a_voir.pop()
        if 0 <= x < largeur and 0 <= y < haut:
            rouge, vert, bleu, alpha = feuille.get_at((x, y))
            if alpha != 0 and rouge >= 235 and vert >= 235 and bleu >= 235:
                feuille.set_at((x, y), (0, 0, 0, 0))
                a_voir.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    # Les 4 images sont separees par des colonnes vides : on repere chaque bloc de colonnes non vides.
    blocs = []
    debut = None
    for x in range(largeur + 1):
        plein = False
        if x < largeur:
            for y in range(haut):
                if feuille.get_at((x, y))[3] > 0:
                    plein = True
                    break
        if plein and debut is None:
            debut = x
        if not plein and debut is not None:
            blocs.append((debut, x - debut))
            debut = None

    # Toutes les images sont reduites du meme facteur (la plus haute fait hauteur_voulue pixels).
    noms = ["pingu_face", "pingu_droite", "pingu_dos", "pingu_gauche"]
    facteur = hauteur_voulue / float(feuille.subsurface(pygame.Rect(blocs[0][0], 0, blocs[0][1], haut)).get_bounding_rect().height)
    for k in range(4):
        morceau = feuille.subsurface(pygame.Rect(blocs[k][0], 0, blocs[k][1], haut))
        morceau = morceau.subsurface(morceau.get_bounding_rect())
        taille = (int(morceau.get_width() * facteur), int(morceau.get_height() * facteur))
        sprites[noms[k]] = pygame.transform.smoothscale(morceau, taille)


def load_sprites(taille):
    # Charge les feuilles de sprites et retourne un dictionnaire d'images.
    # Doit etre appele apres pygame.display.set_mode (convert_alpha en a besoin).
    sprites = {}

    herbe = charger_feuille("TX Tileset Grass.png")
    sprites["herbe"] = decouper(herbe, 0, 0, 32, 32, taille)
    sprites["herbe_fleurs"] = decouper(herbe, 125, 35, 32, 32, taille)
    for nom in ("herbe", "herbe_fleurs"):
        sprites[nom].fill(ECLAIRCIR_HERBE, special_flags=pygame.BLEND_RGB_ADD)

    # Sol de jeu : dalles de pierre claire (plain et avec un clou), l'herbe reste a l'exterieur.
    sol_pierre = charger_feuille("TX Tileset Stone Ground.png")
    sprites["sol1"] = decouper(sol_pierre, 16, 16, 32, 32, taille)
    sprites["sol2"] = decouper(sol_pierre, 177, 14, 32, 32, taille)
    for nom in ("sol1", "sol2"):
        pygame.draw.rect(sprites[nom], (95, 90, 75), (0, 0, taille, taille), 1)   # fin contour : on voit les cases

    # Murs : TOUS les murs viennent de la feuille fwall.png (dossier assets/), pour qu'ils aient le meme style.
    # Rangee du haut = faces de mur eclairees (simple, fenetre, fissure, mousse), rangee du bas = les memes
    # dans l'ombre (x de chaque type dans x_types).
    feuille_mur = pygame.image.load(os.path.join(DOSSIER_PROJET, "assets", "fwall.png")).convert_alpha()
    # On enleve 4 pixels de cadre a gauche et a droite de chaque face pour que les murs voisins se raccordent.
    x_types = [14, 77, 139, 202]
    for k in range(4):
        clair = feuille_mur.subsurface(pygame.Rect(x_types[k] + 4, 26, 41, 53))
        sombre = feuille_mur.subsurface(pygame.Rect(x_types[k] + 4, 108, 41, 49))
        sprites["mur_clair" + str(k)] = pygame.transform.smoothscale(clair, (taille, taille))
        sprites["mur_sombre" + str(k)] = pygame.transform.smoothscale(sombre, (taille, taille))
        sprites["mur_sombre" + str(k)].fill((22, 19, 14), special_flags=pygame.BLEND_RGB_ADD)    # un peu moins sombre

    # Ombres douces posees sur le sol, le long des murs : de plus en plus transparentes en s'eloignant du mur.
    epaisseur = taille // 3
    sprites["ombre_nord"] = pygame.Surface((taille, epaisseur), pygame.SRCALPHA)
    sprites["ombre_ouest"] = pygame.Surface((epaisseur // 2, taille), pygame.SRCALPHA)
    for k in range(epaisseur):
        alpha = int(100 * (1 - k / float(epaisseur)) ** 2)
        pygame.draw.line(sprites["ombre_nord"], (0, 0, 0, alpha), (0, k), (taille, k))
        if k < epaisseur // 2:
            pygame.draw.line(sprites["ombre_ouest"], (0, 0, 0, alpha), (k, 0), (k, taille))
    sprites["ombre_est"] = pygame.transform.flip(sprites["ombre_ouest"], True, False)

    props = charger_feuille("TX Props.png")
    sprites["caisse"] = decouper(props, 160, 18, 32, 23, taille)

    charger_jack(sprites, int(taille * 1.1))

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

    charger_pingouin(sprites, int(taille * 1.15))
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
    # Ambiance de prairie de 6 secondes, jouee en boucle : du vent (bruit aleatoire adouci) qui monte et descend.
    duree = 6.0
    total = int(frequence * duree)
    hasard = random.Random(7)       # graine fixe : le son est toujours le meme
    echantillons = []
    adouci = 0.0
    for i in range(total):
        # On adoucit le bruit (chaque valeur se rapproche un peu du nouveau tirage) pour qu'il souffle au lieu de gresiller.
        adouci = adouci + 0.03 * (hasard.uniform(-1, 1) - adouci)
        # Le volume suit une bosse : 0 au debut, maximum au milieu, 0 a la fin (la boucle ne fait pas de "clic").
        rafale = math.sin(math.pi * i / total)
        echantillons.append(adouci * 1.6 * (0.3 + 0.7 * rafale))
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

