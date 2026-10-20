# Point d'entree du programme.
# Usage : python main.py           -> lance l'interface graphique (Pygame, etapes 6 a 9)
#         python main.py --console -> mode console : BFS sur tous les niveaux

import sys
import time

from levels import LEVELS
from sokoban import SokobanPuzzle
from search import BFS


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
        print("L'interface graphique sera ajoutee aux etapes 6 a 9. Utiliser --console pour l'instant.")


if __name__ == "__main__":
    main()
