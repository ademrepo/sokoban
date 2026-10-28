# - optimal si l'heuristique est admissible (h ne depasse jamais le vrai cout restant) ;
# - complexite : dans le pire cas O(b^d) comme le BFS, mais une bonne heuristique la reduit beaucoup
#   (le nombre de noeuds developpes, steps, est plus petit)
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
    #|xb - xs| + |yb - ys|
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def h1(etat):
    #:nombre de caisses pas encore sur une cible
    return len(positions(etat, "B"))

def h2(etat):
    #2*h1 + somme, pour chaque caisse hors cible
    #Cibles libres='S' (cible vide) et '.' (le joueur est dessus).
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
    #h2 + le trajet du joueur jusqu'a la caisse la plus proche
    caisses = positions(etat, "B")
    if len(caisses) == 0:
        return 0
    joueur = etat.player_pos
    plus_proche = None
    for caisse in caisses:
        d = distance_manhattan(joueur, caisse)
        if plus_proche is None or d < plus_proche:
            plus_proche = d
    return h2(etat) + plus_proche - 1


def AStar(s, successorsFn, isGoal, h):
    # s : etat initial ; successorsFn:retourne la liste des(action, successeur);isGoal:test du but
    # Retourne deux valeurs : (noeud but ou None ; steps), steps = nombre de noeuds developpes (comme le BFS).
    racine = Node(s, None, None)        #init_node.g = 0 (fait par Node)
    racine.setF(h)                      #init_node.f=h(init_node)

    # Open : file de priorite ordonnee par f. On utilise heapq : la liste ouvert est un tas,
    # donc ouvert[0] est toujours l'element de plus petit f.
    # Chaque element est (f, numero, noeud) ; le numero departage les egalites (premier arrive,
    # premier sorti) et evite de comparer deux noeuds entre eux.
    ouvert = []
    numero = 0
    heapq.heappush(ouvert, (racine.f, numero, racine))
    ferme = []                          # Closed : liste des noeuds deja developpes

    # Optimisation de vitesse uniquement (comme les sets du BFS) : ces deux dictionnaires contiennent les
    # memes etats que ouvert et ferme, avec le f de leur noeud. Ils servent a tester vite "etat in Open /
    # in Closed" et "avec un f plus grand ?" sans parcourir la liste.
    ouvertF = {}
    fermeF = {}
    ouvertF[racine.state] = racine.f

    steps = 0
    while len(ouvert) > 0:
        f, n, courant = heapq.heappop(ouvert)      # le noeud de plus petit f dans Open
        del ouvertF[courant.state]
        if isGoal(courant.state):
            return courant, steps                  # le but est teste a la sortie de Open
        steps = steps + 1
        ferme.append(courant)
        fermeF[courant.state] = courant.f

        for action, successeur in successorsFn(courant.state):
            enfant = Node(successeur, courant, action)      # child.g = current.g + 1
            enfant.setF(h)                                  # child.f = child.g + h(child)

            if enfant.state not in ouvertF and enfant.state not in fermeF:
                numero = numero + 1
                heapq.heappush(ouvert, (enfant.f, numero, enfant))
                ouvertF[enfant.state] = enfant.f
            elif enfant.state in ouvertF:
                # Meme etat deja dans Open : s'il a un f plus grand, on remplace ce noeud par l'enfant.
                if ouvertF[enfant.state] > enfant.f:
                    for k in range(len(ouvert)):
                        if ouvert[k][2].state == enfant.state:
                            numero = numero + 1
                            ouvert[k] = (enfant.f, numero, enfant)
                            heapq.heapify(ouvert)           #order the queue
                            break
                    ouvertF[enfant.state] = enfant.f
            else:
                # Meme etat deja dans Closed : s'il a un f plus grand, on enleve ce noeud de Closed
                # et on met l'enfant dans Open.
                if fermeF[enfant.state] > enfant.f:
                    for k in range(len(ferme)):
                        if ferme[k].state == enfant.state:
                            ferme.pop(k)
                            break
                    del fermeF[enfant.state]
                    numero = numero + 1
                    heapq.heappush(ouvert, (enfant.f, numero, enfant))
                    ouvertF[enfant.state] = enfant.f

    return None, steps
