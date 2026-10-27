# Algorithme A* (A etoile), voir cours chapitre 1, section 1.3.4.1, Figure 1.29, et heuristiques de l'enonce (partie B).
#
# Proprietes (donnees par le cours) :
# - complet ;
# - optimal si l'heuristique est admissible (h ne depasse jamais le vrai cout restant) ;
# - complexite : dans le pire cas O(b^d) comme le BFS, mais une bonne heuristique la reduit beaucoup
#   (le nombre de noeuds developpes, steps, est plus petit). Voir le tableau de comparaison dans les logs.


import heapq
from node import Node


def positions(etat, symboles):
    # Retourne la liste des positions (ligne, colonne) des cases dont le symbole est dans symboles.
    liste = []
    for r in range(len(etat.grid)):
        for c in range(len(etat.grid[r])):
            if etat.grid[r][c] in symboles:
                liste.append((r, c))
    return liste


def distance_manhattan(a, b):
    # Equation 2 de l'enonce : |xb - xs| + |yb - ys|.
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h1(etat):
    # Heuristique 1 (equation 1) : nombre de caisses pas encore sur une cible.
    # Une caisse hors cible est un 'B' dans la grille.
    return len(positions(etat, "B"))


def h2(etat):
    # Heuristique 2 (equation 3) : 2 * h1 + somme, pour chaque caisse hors cible,
    # de la distance de Manhattan jusqu'a la cible libre la plus proche.
    # Cibles libres = 'S' (cible vide) et '.' (le joueur est dessus).
    caisses = positions(etat, "B")
    cibles = positions(etat, "S.")
    total = 2 * len(caisses)
    for caisse in caisses:
        plus_proche = None
        for cible in cibles:
            d = distance_manhattan(caisse, cible)
            if plus_proche is None or d < plus_proche:
                plus_proche = d
        total = total + plus_proche
    return total


def h3(etat):
    # Heuristique 3 (proposee), deux idees d'un joueur humain :
    # 1) Une cible ne peut recevoir qu'une seule caisse. h2 laisse deux caisses viser la meme cible,
    #    ce qui sous-estime le travail. Ici chaque caisse prend la cible libre la plus proche
    #    parmi celles que les caisses precedentes n'ont pas deja prises.
    # 2) Chaque deplacement coute 1, meme sans pousser : le joueur doit d'abord marcher jusqu'a une caisse.
    #    On ajoute la distance joueur -> caisse la plus proche, moins 1 (il doit etre colle a la caisse).
    # Pas de detection de blocage (deadlock) : on reste simple.
    caisses = positions(etat, "B")
    if len(caisses) == 0:
        return 0
    cibles = positions(etat, "S.")
    prises = []
    total = 2 * len(caisses)
    for caisse in caisses:
        plus_proche = None
        for cible in cibles:
            if cible not in prises:
                if plus_proche is None or distance_manhattan(caisse, cible) < distance_manhattan(caisse, plus_proche):
                    plus_proche = cible
        prises.append(plus_proche)
        total = total + distance_manhattan(caisse, plus_proche)
    joueur = etat.player_pos
    trajet = None
    for caisse in caisses:
        d = distance_manhattan(joueur, caisse)
        if trajet is None or d < trajet:
            trajet = d
    return total + trajet - 1


def AStar(s, successorsFn, isGoal, h):
    # s : etat initial ; successorsFn : retourne la liste des (action, successeur) ; isGoal : test du but
    # h : heuristique (fonction qui prend un etat et retourne un nombre)
    # Retourne deux valeurs : (noeud but ou None ; steps), steps = nombre de noeuds developpes (comme le BFS).
    racine = Node(s, None, None)
    racine.setF(h)

    # Open : file de priorite ordonnee par f. On utilise heapq (tas) : le plus petit f sort en premier.
    # Chaque element est (f, numero, noeud) ; le numero departage les egalites (premier arrive, premier sorti)
    # et evite de comparer deux noeuds entre eux.
    ouvert = []
    numero = 0
    heapq.heappush(ouvert, (racine.f, numero, racine))
    # ouvertDict : etat -> noeud actuellement dans Open (permet le test "etat in Open" et de lire son f).
    # Un noeud remplace dans Open reste dans le tas mais n'est plus dans ouvertDict : on l'ignore a sa sortie.
    ouvertDict = {}
    ouvertDict[racine.state] = racine
    ferme = {}            # Closed : etat -> noeud deja developpe

    steps = 0
    while len(ouvert) > 0:
        f, n, courant = heapq.heappop(ouvert)
        if ouvertDict.get(courant.state) is not courant:
            continue                    # noeud remplace par un meilleur : on l'ignore
        del ouvertDict[courant.state]
        if isGoal(courant.state):
            return courant, steps       # le test du but se fait a la sortie de Open (Figure 1.29)
        steps = steps + 1
        ferme[courant.state] = courant

        for action, successeur in successorsFn(courant.state):
            enfant = Node(successeur, courant, action)
            enfant.setF(h)
            if enfant.state not in ouvertDict and enfant.state not in ferme:
                numero = numero + 1
                heapq.heappush(ouvert, (enfant.f, numero, enfant))
                ouvertDict[enfant.state] = enfant
            elif enfant.state in ouvertDict:
                if enfant.f < ouvertDict[enfant.state].f:
                    # Meme etat deja dans Open avec un f plus grand : on le remplace par l'enfant.
                    numero = numero + 1
                    heapq.heappush(ouvert, (enfant.f, numero, enfant))
                    ouvertDict[enfant.state] = enfant
            else:
                if enfant.f < ferme[enfant.state].f:
                    # Meme etat deja dans Closed avec un f plus grand : on l'enleve de Closed
                    # et on remet l'enfant dans Open.
                    del ferme[enfant.state]
                    numero = numero + 1
                    heapq.heappush(ouvert, (enfant.f, numero, enfant))
                    ouvertDict[enfant.state] = enfant

    return None, steps
