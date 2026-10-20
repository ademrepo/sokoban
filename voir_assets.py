# OUTIL TEMPORAIRE : ce fichier sera SUPPRIME du projet a l'etape 10b (nettoyage), avant le rendu.
#
# A quoi il sert : parcourir toutes les images (assets) du pack "Pixel Art Top Down - Basic" pour choisir
# celles qu'on veut dans le jeu. Il ne fait pas partie du jeu et n'est pas demande par l'enonce.
# Marche a suivre : on lance l'outil, on clique sur les objets voulus, ENTREE les enregistre dans
# choix_assets.txt (fichier ignore par git), puis on donne ce fichier a la personne qui modifie
# assets_loader.py pour ajouter les images au jeu.
#
# Lancer : python voir_assets.py
#
# Mode feuilles (par defaut) : chaque objet de la feuille est detecte automatiquement et numerote.
#   clic          : selectionne l'objet sous la souris (son rectangle s'affiche en bas)
#   ENTREE        : enregistre l'objet selectionne dans choix_assets.txt (a me donner : "regarde choix_assets.txt")
#   N / P         : feuille suivante / precedente
#   fleches ou molette : fait defiler la feuille (MAJ + molette = defilement horizontal)
#   Z             : zoom x1 / x2
#   C             : catalogue des sprites deja utilises par le jeu (re-appuyer pour revenir)
#   ECHAP         : quitter

import os
import pygame

from assets_loader import load_sprites, DOSSIER, DOSSIER_OMBRES

LARGEUR = 1000
HAUTEUR = 800
BANDEAU = 50                 # hauteur du bandeau d'infos en bas
FICHIER_CHOIX = "choix_assets.txt"


def lister_feuilles():
    # Retourne la liste des (nom affiche, chemin) de toutes les feuilles PNG du pack.
    feuilles = []
    for dossier in (DOSSIER, DOSSIER_OMBRES):
        for nom in sorted(os.listdir(dossier)):
            if nom.endswith(".png"):
                feuilles.append((dossier.split("/")[-2] + "/" + nom, dossier + nom))
    return feuilles


def detecter_objets(image):
    # Trouve les objets d'une feuille : groupes de pixels non transparents proches les uns des autres.
    # On "grossit" d'abord le masque de quelques pixels pour que les morceaux d'un meme objet
    # (ex. un arbre et son ombre) se touchent et ne forment qu'un seul rectangle.
    masque = pygame.mask.from_surface(image, 10)
    carre = pygame.mask.Mask((9, 9), fill=True)
    grossi = masque.convolve(carre, None, (-4, -4))
    resultat = []
    for rect in grossi.get_bounding_rects():
        rect = rect.clip(image.get_rect())
        # On rogne le rectangle avec les vrais pixels pour avoir un cadre serre.
        zone = pygame.mask.Mask(rect.size)
        zone.draw(masque, (-rect.x, -rect.y))
        serres = zone.get_bounding_rects()
        if len(serres) > 0:
            serre = serres[0].unionall(serres[1:])
            serre.move_ip(rect.x, rect.y)
            if serre.width >= 4 and serre.height >= 4:
                resultat.append(serre)
    # Tri de haut en bas puis de gauche a droite pour une numerotation lisible.
    resultat.sort(key=lambda r: (r.y // 40, r.x))
    return resultat


def dessiner_catalogue(ecran, police, sprites):
    ecran.fill((50, 50, 50))
    x = 10
    y = 10
    for nom in sorted(sprites):
        image = sprites[nom]
        pygame.draw.rect(ecran, (140, 150, 40), (x, y, 110, 130))
        ecran.blit(image, (x + 55 - image.get_width() // 2, y + 5))
        ecran.blit(police.render(nom, True, (255, 255, 255)), (x, y + 110))
        x += 120
        if x + 110 > ecran.get_width():
            x = 10
            y += 140


def main():
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Assets")
    police = pygame.font.SysFont("consolas", 15)
    petite = pygame.font.SysFont("consolas", 11)
    sprites = load_sprites(48)
    feuilles = lister_feuilles()

    numero = 0
    zoom = 2
    defil_x = 0
    defil_y = 0
    catalogue = False
    choisi = None            # rectangle (Rect, en pixels de la feuille) de l'objet selectionne
    nom_choisi = ""          # son nom ("objet #12" ou "tuile")
    message = "Clique sur un objet. ENTREE = l'enregistrer dans " + FICHIER_CHOIX
    chargee = None           # (numero de feuille, image, objets)
    en_cours = True

    while en_cours:
        if chargee is None or chargee[0] != numero:
            image = pygame.image.load(feuilles[numero][1]).convert_alpha()
            chargee = (numero, image, detecter_objets(image))
            choisi = None
            defil_x = 0
            defil_y = 0
        image = chargee[1]
        objets = chargee[2]
        maxi_x = max(0, image.get_width() * zoom - LARGEUR)
        maxi_y = max(0, image.get_height() * zoom - (HAUTEUR - BANDEAU))

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    en_cours = False
                if evenement.key == pygame.K_n:
                    numero = (numero + 1) % len(feuilles)
                if evenement.key == pygame.K_p:
                    numero = (numero - 1) % len(feuilles)
                if evenement.key == pygame.K_z:
                    zoom = 3 - zoom
                    defil_x = 0
                    defil_y = 0
                if evenement.key == pygame.K_c:
                    catalogue = not catalogue
                if evenement.key == pygame.K_DOWN:
                    defil_y += 60
                if evenement.key == pygame.K_UP:
                    defil_y -= 60
                if evenement.key == pygame.K_RIGHT:
                    defil_x += 60
                if evenement.key == pygame.K_LEFT:
                    defil_x -= 60
                if evenement.key == pygame.K_RETURN and choisi is not None:
                    r = choisi
                    ligne = feuilles[numero][0] + " " + nom_choisi + " : (" + str(r.x) + ", " + str(r.y) + ", " + str(r.width) + ", " + str(r.height) + ")"
                    fichier = open(FICHIER_CHOIX, "a", encoding="utf-8")
                    fichier.write(ligne + "\n")
                    fichier.close()
                    message = "ENREGISTRE : " + ligne
                    print(message)
            if evenement.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    defil_x -= evenement.y * 60
                else:
                    defil_y -= evenement.y * 60
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1 and not catalogue:
                sx = (evenement.pos[0] + defil_x) // zoom
                sy = (evenement.pos[1] + defil_y) // zoom
                choisi = None
                meilleure_aire = None
                for i in range(len(objets)):
                    if objets[i].collidepoint(sx, sy):
                        aire = objets[i].width * objets[i].height
                        if meilleure_aire is None or aire < meilleure_aire:
                            choisi = objets[i]
                            nom_choisi = "objet #" + str(i + 1)
                            meilleure_aire = aire
                # Les grandes feuilles de sol/herbe/mur sont un seul gros objet : on choisit alors
                # une tuile de 16 x 16 pixels (alignee sur 16) sous la souris.
                if choisi is not None and (choisi.width > 160 or choisi.height > 160):
                    choisi = pygame.Rect(sx // 16 * 16, sy // 16 * 16, 16, 16)
                    nom_choisi = "tuile"
                if choisi is not None:
                    r = choisi
                    message = nom_choisi + " : (" + str(r.x) + ", " + str(r.y) + ", " + str(r.width) + ", " + str(r.height) + ")   ENTREE = enregistrer"

        defil_x = max(0, min(defil_x, maxi_x))
        defil_y = max(0, min(defil_y, maxi_y))

        if catalogue:
            dessiner_catalogue(ecran, police, sprites)
            titre = "CATALOGUE des sprites deja utilises (C = revenir aux feuilles)"
        else:
            ecran.fill((95, 120, 95))
            grande = pygame.transform.scale(image, (image.get_width() * zoom, image.get_height() * zoom))
            ecran.blit(grande, (-defil_x, -defil_y))
            for i in range(len(objets)):
                r = objets[i]
                cadre = pygame.Rect(r.x * zoom - defil_x, r.y * zoom - defil_y, r.width * zoom, r.height * zoom)
                if r.width <= 160 and r.height <= 160:
                    pygame.draw.rect(ecran, (255, 255, 255), cadre, 1)
                if r.width <= 160 and r.height <= 160:
                    ecran.blit(petite.render(str(i + 1), True, (255, 255, 0)), (cadre.x + 1, cadre.y + 1))
            if choisi is not None:
                cadre = pygame.Rect(choisi.x * zoom - defil_x, choisi.y * zoom - defil_y, choisi.width * zoom, choisi.height * zoom)
                pygame.draw.rect(ecran, (255, 230, 0), cadre.inflate(4, 4), 3)
            titre = feuilles[numero][0] + "  (" + str(numero + 1) + "/" + str(len(feuilles)) + ")  " + str(len(objets)) + " objets   N/P = feuille, Z = zoom, C = catalogue, molette = defiler"

        pygame.draw.rect(ecran, (0, 0, 0), (0, HAUTEUR - BANDEAU, LARGEUR, BANDEAU))
        ecran.blit(police.render(titre, True, (255, 255, 255)), (6, HAUTEUR - BANDEAU + 5))
        ecran.blit(police.render(message, True, (255, 220, 80)), (6, HAUTEUR - BANDEAU + 27))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
