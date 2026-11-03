# Point d'entree du programme.
# Usage : python main.py           -> lance l'interface graphique (Pygame), en commencant par le menu
#         python main.py --niveau N -> ouvre directement le niveau numero N (1 a 8)
#         python main.py --console -> mode console : BFS sur tous les niveaux
#         python main.py --compare -> mode console : BFS et A* (h1, h2, h3) sur tous les niveaux, tableau de comparaison
#                                     puis tableau A* sans / avec detection de deadlock
#         python main.py --deadlock -> mode console : seulement le tableau A* sans / avec detection de deadlock

import sys
import time

from levels import LEVELS
from sokoban import SokobanPuzzle
from search import BFS
from astar import AStar, AStarDeadlock, h1, h2, h3
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


def mode_comparaison():
    # Compare BFS et A* (h1, h2, h3) : pour chaque niveau, cout, steps (noeuds developpes) et temps.
    algos = [("BFS", None), ("A* h1", h1), ("A* h2", h2), ("A* h3", h3)]
    print("%-10s %-7s %6s %9s %9s" % ("Niveau", "Algo", "Cout", "Steps", "Temps"))
    for niveau in LEVELS:
        for nom, h in algos:
            etat = SokobanPuzzle(niveau["grid"])
            debut = time.time()
            if h is None:
                noeud, steps = BFS(etat, lambda st: st.successorFunction(), lambda st: st.isGoal())
            else:
                noeud, steps = AStar(etat, lambda st: st.successorFunction(), lambda st: st.isGoal(), h)
            duree = time.time() - debut
            cout = "-"
            if noeud is not None:
                cout = noeud.g
            print("%-10s %-7s %6s %9d %7.3f s" % (niveau["name"], nom, cout, steps, duree))
        print()


def mode_deadlock():
    # Compare A* sans et avec elagage des deadlocks sur les niveaux Deadlock 1 et 2 (et sur les autres, pour verifier
    # que le cout reste le meme). Gain = part des noeuds developpes qu'on ne developpe plus.
    print("A* sans / avec detection de deadlock")
    print("Niveau".ljust(11) + "Algo".ljust(8) + "Cout".rjust(5) + "Steps sans".rjust(12) + "Steps avec".rjust(12) + "Gain".rjust(8))
    for niveau in LEVELS:
        for nom, h in [("A* h1", h1), ("A* h2", h2), ("A* h3", h3)]:
            etat = SokobanPuzzle(niveau["grid"])
            sans, steps_sans = AStar(etat, lambda st: st.successorFunction(), lambda st: st.isGoal(), h)
            avec, steps_avec = AStarDeadlock(etat, lambda st: st.successorFunction(), lambda st: st.isGoal(), h)
            gain = 100.0 * (steps_sans - steps_avec) / steps_sans
            print(niveau["name"].ljust(11) + nom.ljust(8) + str(avec.g).rjust(5) + str(steps_sans).rjust(12)
                  + str(steps_avec).rjust(12) + ("%.1f %%" % gain).rjust(8))
        print()


def main():
    if "--compare" in sys.argv:
        mode_comparaison()
        mode_deadlock()
    elif "--deadlock" in sys.argv:
        mode_deadlock()
    elif "--console" in sys.argv:
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
