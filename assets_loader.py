# Chargement et decoupage des sprites utilises par la GUI.
# Les images viennent du pack "Pixel Art Top Down - Basic" (dossier assets/, ne pas modifier).
# Chaque sprite est decoupe dans une feuille avec un rectangle (x, y, largeur, hauteur)
# trouve a la main en regardant la feuille.

import pygame

DOSSIER = "assets/Pixel Art Top Down - Basic v1.2.3/Texture/"
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


def creer_joueur(taille):
    # Petit chat dessine avec pygame.draw (le pack n'a qu'un bloc de pierre rectangulaire),
    # avec un chapeau vert pointu. Toutes les mesures sont des fractions de la taille d'une case.
    u = taille / 48.0
    image = pygame.Surface((taille, int(taille * 1.2)), pygame.SRCALPHA)
    fourrure = (200, 190, 165)
    contour = (90, 70, 50)

    def p(x, y):
        return (int(x * u), int(y * u))

    # Queue, corps et pattes.
    pygame.draw.line(image, contour, p(34, 52), p(44, 40), int(5 * u) + 1)
    pygame.draw.line(image, fourrure, p(34, 52), p(44, 40), int(3 * u) + 1)
    pygame.draw.ellipse(image, contour, (int(10 * u), int(36 * u), int(28 * u), int(21 * u)))
    pygame.draw.ellipse(image, fourrure, (int(12 * u), int(38 * u), int(24 * u), int(17 * u)))

    # Oreilles, puis tete.
    for oreille in ([(8, 26), (9, 14), (18, 22)], [(40, 26), (39, 14), (30, 22)]):
        points = [p(x, y) for (x, y) in oreille]
        pygame.draw.polygon(image, fourrure, points)
        pygame.draw.polygon(image, contour, points, 2)
    pygame.draw.circle(image, contour, p(24, 29), int(15 * u))
    pygame.draw.circle(image, fourrure, p(24, 29), int(13 * u))

    # Yeux bleus, nez rose.
    pygame.draw.circle(image, (60, 120, 190), p(18, 31), int(3 * u))
    pygame.draw.circle(image, (60, 120, 190), p(30, 31), int(3 * u))
    pygame.draw.circle(image, (255, 150, 160), p(24, 35), int(2 * u))

    # Chapeau vert pointu avec un bandeau clair.
    vert = (50, 160, 60)
    sombre = (20, 85, 30)
    chapeau = [p(9, 24), p(39, 24), p(36, 12), p(33, 3), p(21, 8)]
    pygame.draw.polygon(image, vert, chapeau)
    pygame.draw.polygon(image, sombre, chapeau, 2)
    pygame.draw.rect(image, (235, 220, 120), (int(9 * u), int(21 * u), int(30 * u), int(5 * u)))
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

    sprites["joueur"] = creer_joueur(taille)

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
    sprites["vase"] = decouper_hauteur(props_ombres, 160, 210, 36, 46, taille)
    sprites["statue"] = decouper_hauteur(props_ombres, 440, 14, 52, 84, taille * 2)
    sprites["lanterne"] = decouper_hauteur(props_ombres, 446, 110, 36, 50, taille * 6 // 5)
    sprites["totem"] = decouper_hauteur(props_ombres, 348, 170, 44, 90, taille * 2)
    sprites["coffre"] = decouper_hauteur(props_ombres, 94, 26, 40, 40, taille)
    sprites["tonneau"] = decouper_hauteur(props_ombres, 160, 150, 36, 42, taille)
    sprites["panneau"] = decouper_hauteur(props_ombres, 94, 156, 36, 42, taille)
    sprites["tombe"] = decouper_hauteur(props_ombres, 222, 236, 40, 48, taille)
    sprites["banc"] = decouper_hauteur(props_ombres, 288, 16, 66, 46, taille)
    # Variantes (memes familles d'objets, autres formes), rectangles lus avec voir_assets.py.
    sprites["banc2"] = decouper_hauteur(props_ombres, 286, 85, 74, 44, taille)
    sprites["vase2"] = decouper_hauteur(props_ombres, 162, 286, 35, 35, taille)
    sprites["vase3"] = decouper_hauteur(props_ombres, 163, 346, 31, 40, taille)
    sprites["tombe2"] = decouper_hauteur(props_ombres, 287, 249, 38, 35, taille)
    sprites["stele"] = decouper_hauteur(props_ombres, 225, 7, 34, 58, taille * 3 // 2)
    sprites["totem2"] = decouper_hauteur(props_ombres, 414, 192, 40, 61, taille * 3 // 2)
    sprites["rocher"] = decouper_hauteur(props_ombres, 1, 428, 66, 50, taille)
    # Autres variantes du pack : (nom, rectangle, hauteur voulue).
    autres = [
        ("coffre2", (94, 74, 38, 54), taille),
        ("panneau2", (94, 222, 34, 36), taille),
        ("stele2", (225, 89, 34, 70), taille * 3 // 2),
        ("stele3", (225, 181, 34, 42), taille),
        ("tombe3", (225, 301, 34, 44), taille),
        ("tombe4", (286, 304, 38, 50), taille),
        ("sarcophage", (286, 156, 38, 61), taille * 3 // 2),
        ("dalle_haute", (385, 0, 34, 65), taille * 3 // 2),
        ("dalle_haute2", (385, 96, 34, 65), taille * 3 // 2),
        ("ruine", (418, 357, 61, 53), taille),
        ("caisses", (158, 16, 40, 54), taille * 3 // 2),
        ("caisse_petite", (161, 84, 32, 44), taille),
        ("porte", (27, 101, 42, 54), taille * 5 // 4),   # sert de sortie du niveau (voir gui.py)
        ("porte_ouverte", (27, 164, 42, 58), taille * 5 // 4),
    ]
    for nom, rect, hauteur_voulue in autres:
        sprites[nom] = decouper_hauteur(props_ombres, rect[0], rect[1], rect[2], rect[3], hauteur_voulue)

    # Arches et escaliers de la feuille des structures.
    structures = charger_feuille("TX Struct.png")
    sprites["arche"] = decouper_hauteur(structures, 408, 27, 80, 64, taille * 3 // 2)
    sprites["arche_porte"] = decouper_hauteur(structures, 408, 27, 80, 64, taille * 2)   # encadre la porte de sortie
    sprites["arche2"] = decouper_hauteur(structures, 416, 128, 64, 64, taille * 3 // 2)
    sprites["escalier"] = decouper_hauteur(structures, 48, 288, 90, 96, taille * 3 // 2)
    sprites["escalier2"] = decouper_hauteur(structures, 176, 288, 90, 96, taille * 3 // 2)

    return sprites
