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


def ajouter_chapeau(image, taille):
    # Dessine un petit chapeau vert pointu sur la tete du chat (le pack n'en a pas).
    vert = (60, 150, 60)
    vert_fonce = (30, 90, 35)
    base = taille // 5
    pointe = [(taille // 6, base + 4), (taille - taille // 6, base + 4), (taille * 3 // 4, 0)]
    pygame.draw.polygon(image, vert, pointe)
    pygame.draw.polygon(image, vert_fonce, pointe, 2)
    pygame.draw.rect(image, vert_fonce, (taille // 6, base + 2, taille * 2 // 3 + 1, 5))


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

    joueur = charger_feuille("TX Player.png")
    sprites["joueur"] = decouper(joueur, 6, 14, 21, 44, taille)
    ajouter_chapeau(sprites["joueur"], taille)

    # Decor autour du niveau : feuilles "avec ombres", proportions gardees (on fixe la hauteur).
    plantes = charger_feuille("TX Plant with Shadow.png", DOSSIER_OMBRES)
    props_ombres = charger_feuille("TX Props with Shadow.png", DOSSIER_OMBRES)
    sprites["arbre"] = decouper_hauteur(plantes, 18, 8, 130, 172, taille * 2)
    sprites["arbre2"] = decouper_hauteur(plantes, 162, 10, 100, 150, taille * 2)
    sprites["buisson"] = decouper_hauteur(plantes, 210, 178, 60, 56, taille)
    sprites["buisson2"] = decouper_hauteur(plantes, 154, 184, 44, 40, taille)
    sprites["buisson3"] = decouper_hauteur(plantes, 280, 182, 44, 50, taille)
    sprites["vase"] = decouper_hauteur(props_ombres, 160, 210, 36, 46, taille)
    sprites["statue"] = decouper_hauteur(props_ombres, 440, 14, 52, 84, taille * 2)
    sprites["lanterne"] = decouper_hauteur(props_ombres, 446, 110, 36, 50, taille * 6 // 5)
    sprites["totem"] = decouper_hauteur(props_ombres, 348, 170, 44, 90, taille * 2)
    sprites["coffre"] = decouper_hauteur(props_ombres, 94, 26, 40, 40, taille)
    sprites["tonneau"] = decouper_hauteur(props_ombres, 160, 150, 36, 42, taille)
    sprites["panneau"] = decouper_hauteur(props_ombres, 94, 156, 36, 42, taille)
    sprites["tombe"] = decouper_hauteur(props_ombres, 222, 236, 40, 48, taille)
    sprites["banc"] = decouper_hauteur(props_ombres, 288, 16, 66, 46, taille)

    return sprites
