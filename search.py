# Algorithme BFS (Breadth-First Search), voir cours chapitre 1, section 1.3.3.1, Figure 1.19.
#
# Proprietes (donnees par le cours) :
# - complet : trouve une solution si elle existe (le but le moins profond est a une profondeur finie d) ;
# - optimal : seulement si toutes les actions ont le meme cout (c'est le cas ici, chaque pas coute 1) ;
# - complexite en temps : O(b^d) ;
# - complexite en espace : O(b^d) (taille maximale de la liste Open).


from collections import deque
from node import Node


def BFS(s, successorsFn, isGoal):
    # s : etat initial
    # successorsFn : fonction qui retourne la liste des (action, successeur) pour un etat
    # isGoal : fonction qui teste si un etat est un etat but
    # Retourne le noeud but trouve, ou None si aucune solution.
    racine = Node(s, None, None)
    if isGoal(racine.state):
        return racine

    ouvert = deque()      # Open : file FIFO (on enleve a gauche, on ajoute a droite)
    ouvert.append(racine)
    ferme = []            # Closed : noeuds deja developpes

    # Optimisation de vitesse uniquement : ces deux ensembles contiennent les memes etats
    # que ouvert et ferme, mais tester "etat in ensemble" est bien plus rapide que dans
    # une liste. Ca ne change pas l'algorithme du cours. Ils restent synchronises avec ouvert/ferme.
    ouvertSet = set()
    fermeSet = set()
    ouvertSet.add(racine.state)

    while len(ouvert) > 0:
        courant = ouvert.popleft()     # le noeud le moins profond
        ouvertSet.remove(courant.state)
        ferme.append(courant)
        fermeSet.add(courant.state)

        for action, successeur in successorsFn(courant.state):
            enfant = Node(successeur, courant, action)
            if enfant.state not in fermeSet and enfant.state not in ouvertSet:
                if isGoal(enfant.state):
                    return enfant
                ouvert.append(enfant)
                ouvertSet.add(enfant.state)

    return None
