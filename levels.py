# Niveaux du jeu : liste de dictionnaires {"name": ..., "grid": [...]}.
# Les 5 premiers niveaux sont transcrits depuis la Figure 4 (Exemples 1 a 5) de l'enonce.
# Les 3 derniers sont des niveaux maison, simples a moyens.
# Symboles : R=joueur, O=mur, ' '=case vide, S=case cible, B=caisse,
#            .=joueur sur case cible, *=caisse sur case cible.

LEVELS = [
    {
        "name": "Exemple 1",
        "grid": [
            "OOOOOO",
            "OS B O",
            "O OR O",
            "O    O",
            "O    O",
            "OOOOOO",
        ],
    },
    {
        "name": "Exemple 2",
        "grid": [
            "OOOOOOOOOO",
            "O        O",
            "O        O",
            "O  OOOO  O",
            "O   OO.  O",
            "O     O  O",
            "O  B  OO O",
            "O     OO O",
            "O     OO O",
            "OOOOOOOOOO",
        ],
    },
    {
        "name": "Exemple 3",
        "grid": [
            "OOOOOOOO",
            "O   O  O",
            "O  BR  O",
            "O   OB O",
            "O   O  O",
            "OOOOO SO",
            "OOOOO SO",
            "OOOOOOOO",
        ],
    },
    {
        "name": "Exemple 4",
        "grid": [
            "OOOOOOO",
            "OO  OOO",
            "OO  OOO",
            "OO *  O",
            "OOBOB O",
            "O SRS O",
            "O    OO",
            "OOO  OO",
            "OOOOOOO",
        ],
    },
    {
        "name": "Exemple 5",
        "grid": [
            "OOOOOOOOO",
            "OOOSO  OO",
            "O    B OO",
            "O B R  SO",
            "OOO O OOO",
            "OOO O OOO",
            "OOOBO OOO",
            "OOO  SOOO",
            "OOOOOOOOO",
        ],
    },
    {
        # Niveau maison 1 : solution optimale en 2 coups (droite, bas).
        "name": "Maison 1",
        "grid": [
            "OOOOO",
            "OR  O",
            "O B O",
            "O S O",
            "OOOOO",
        ],
    },
    {
        # Niveau maison 2 : solution en 5 coups (pas de mur adjacent a la caisse).
        "name": "Maison 2",
        "grid": [
            "OOOOOOO",
            "O R   O",
            "O     O",
            "O B S O",
            "OOOOOOO",
        ],
    },
    {
        # Niveau maison 3 : deux caisses, deux cibles, solution en 12 coups.
        "name": "Maison 3",
        "grid": [
            "OOOOOOO",
            "O R   O",
            "O B B O",
            "OS   SO",
            "O     O",
            "OOOOOOO",
        ],
    },
]
