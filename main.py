# Point d'entree du programme.
# Usage : python main.py           -> lance l'interface graphique (Pygame), en commencant par le menu
#         python main.py --niveau N -> ouvre directement le niveau numero N (1 a 8)
#         python main.py --console -> mode console : BFS sur tous les niveaux

import sys
import time

from levels import LEVELS
from sokoban import SokobanPuzzle
from search import BFS
from gui import Game


def resoudre_niveau(niveau):
    # Lance le BFS sur un niveau et retourne (noeud but ou None, temps en secondes).
    etatInitial = SokobanPuzzle(niveau["grid"])
    debut = time.time()
    noeud = BFS(etatInitial, lambda st: st.successorFunction(), lambda st: st.isGoal())
    duree = time.time() - debut
    return noeud, duree


def mode_console():
    # Resout chaque niveau et affiche la solution, le cout et le temps de calcul.
    for niveau in LEVELS:
        print("=== " + niveau["name"] + " ===")
        print(SokobanPuzzle(niveau["grid"]))
        noeud, duree = resoudre_niveau(niveau)
        if noeud is None:
            print("Aucune solution")
        else:
            actions = noeud.getSolution()
            print("Solution :", " ".join(actions))
            print("Cout (g) :", noeud.g, "| Nombre de pas :", len(actions))
        print("Temps BFS : %.3f s" % duree)
        print()


def main():
    if "--console" in sys.argv:
        mode_console()
    else:
        # Sans option, le jeu commence par le menu de choix du niveau.
        # Option : python main.py --niveau 3 ouvre directement le niveau numero 3 (1 = Exemple 1).
        numero = 0
        menu = True
        if "--niveau" in sys.argv:
            numero = int(sys.argv[sys.argv.index("--niveau") + 1]) - 1
            menu = False
        jeu = Game(numero, menu)
        jeu.run()


if __name__ == "__main__":
    main()
