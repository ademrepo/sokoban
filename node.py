# Classe Node : brique de base de l'arbre de recherche (voir cours chapitre 1).
# Contient uniquement state, parent, action, g (le coût g vaut la profondeur car chaque pas coûte 1).


class Node:

    def __init__(self, state, parent=None, action=None):
        pass

    def getPath(self):
        # Retourne la liste des états depuis l'état initial jusqu'à ce noeud.
        pass

    def getSolution(self):
        # Retourne la liste des actions depuis l'état initial jusqu'à ce noeud.
        pass
