# Algorithme BFS (Breadth-First Search), voir cours chapitre 1, section 1.3.3.1, Figure 1.19.
#
# Proprietes (donnees par le cours) :
# - complet : trouve une solution si elle existe (le but le moins profond est a une profondeur finie d) ;
# - optimal : seulement si toutes les actions ont le meme cout (c'est le cas ici, chaque pas coute 1) ;
# - complexite en temps : O(b^d) ;
# - complexite en espace : O(b^d) (taille maximale de la liste Open).


def BFS(s, successorsFn, isGoal):
    # s : etat initial
    # successorsFn : fonction qui retourne la liste des (action, successeur) pour un etat
    # isGoal : fonction qui teste si un etat est un etat but
    # Retourne le noeud but trouve, ou None si aucune solution.
    pass
