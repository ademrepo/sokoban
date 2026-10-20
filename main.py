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
    # Lance le BFS sur un niveau et retourne (noeud but ou None, steps, temps en secondes).
    etat_initial = SokobanPuzzle(niveau["grid"])
    debut = time.time()
    noeud, steps = BFS(etat_initial, lambda st: st.successorFunction(), lambda st: st.isGoal())
    duree = time.time() - debut
    return noeud, steps, duree


def mode_console():
    # Resout chaque niveau et affiche la solution, le cout, les steps (noeuds developpes) et le temps.
    for niveau in LEVELS:
        print("=== " + niveau["name"] + " ===")
        print(SokobanPuzzle(niveau["grid"]))
        noeud, steps, duree = resoudre_niveau(niveau)
        if noeud is None:
            print("Aucune solution")
        else:
            print("Solution :", " ".join(noeud.getSolution()))
            print("Cout (g) :", noeud.g)
        print("Steps (noeuds developpes) :", steps)
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
            position = sys.argv.index("--niveau") + 1
            # On verifie que le numero existe, sinon on explique au lieu de planter.
            if position >= len(sys.argv) or not sys.argv[position].isdigit() or not 1 <= int(sys.argv[position]) <= len(LEVELS):
                print("Usage : python main.py --niveau N   (N entre 1 et " + str(len(LEVELS)) + ")")
                return
            numero = int(sys.argv[position]) - 1
            menu = False
        jeu = Game(numero, menu)
        jeu.run()


if __name__ == "__main__":
    main()
