# Classe Node : brique de base de l'arbre de recherche (voir cours chapitre 1).
# Contient uniquement state, parent, action, g (le coût g vaut la profondeur car chaque pas coûte 1).


class Node:

    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        if parent is None:
            self.g = 0
        else:
            self.g = parent.g + 1

    def getPath(self):
        # Retourne la liste des états depuis l'état initial jusqu'à ce noeud.
        chemin = []
        noeud = self
        while noeud is not None:
            chemin.append(noeud.state)
            noeud = noeud.parent
        chemin.reverse()
        return chemin

    def getSolution(self):
        # Retourne la liste des actions depuis l'état initial jusqu'à ce noeud.
        # La racine n'a pas d'action (None), on ne la met pas dans la liste.
        actions = []
        noeud = self
        while noeud.parent is not None:
            actions.append(noeud.action)
            noeud = noeud.parent
        actions.reverse()
        return actions
