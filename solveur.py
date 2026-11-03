# Lance un algorithme de recherche sur un etat et mesure le temps de calcul.
# Utilise par main.py (console) et gui.py (interface), pour ne pas ecrire deux fois les memes lignes.

import time

from search import BFS
from astar import AStar, AStarDeadlock


def resoudre(etat, h=None, deadlock=False):
    # h = None : BFS. Sinon A* avec l'heuristique h, et avec elagage des deadlocks si deadlock est vrai.
    # Retourne (noeud but ou None, steps, temps de calcul en secondes).
    successeurs = lambda s: s.successorFunction()
    but = lambda s: s.isGoal()
    debut = time.time()
    if h is None:
        noeud, steps = BFS(etat, successeurs, but)
    elif deadlock:
        noeud, steps = AStarDeadlock(etat, successeurs, but, h)
    else:
        noeud, steps = AStar(etat, successeurs, but, h)
    return noeud, steps, time.time() - debut
