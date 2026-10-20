# Tests "console" avec de simples assert (pas de pytest).
# Sera complété au fur et à mesure des etapes 2, 3, 4 et 5.

from sokoban import SokobanPuzzle
from node import Node
from search import BFS
from levels import LEVELS


def testMurBloqueDeplacement():
    grille = ["OOO", "ORO", "OOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert actions == []


def testPousserCaisseDansMurEstIllegale():
    # Joueur a gauche d'une caisse, mur juste apres la caisse : poussee impossible.
    grille = ["OOOO", "ORBO", "OOOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert "RIGHT" not in actions


def testPousserDeuxCaissesEstIllegale():
    # Joueur puis deux caisses d'affilee : la premiere ne peut pas etre poussee.
    grille = ["OOOOO", "ORBBO", "OOOOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert "RIGHT" not in actions


def testPousserCaisseSurCibleDonneEtoile():
    grille = ["OOOOO", "ORBSO", "OOOOO"]
    etat = SokobanPuzzle(grille)
    successeurs = dict(etat.successorFunction())
    nouvelEtat = successeurs["RIGHT"]
    assert nouvelEtat.grid == ("OOOOO", "O R*O", "OOOOO")


def testMarcherSurCibleEtLaQuitter():
    # Le joueur marche sur une cible (S -> .), puis en repart (. -> S).
    grille = ["OOOO", "ORSO", "OOOO"]
    etat = SokobanPuzzle(grille)
    successeurs = dict(etat.successorFunction())
    etatSurCible = successeurs["RIGHT"]
    assert etatSurCible.grid[1] == "O .O"

    successeursRetour = dict(etatSurCible.successorFunction())
    etatRetour = successeursRetour["LEFT"]
    assert etatRetour.grid[1] == "ORSO"


def testIsGoalFauxAuDepartVraiSurPlateauResolu():
    etatDepart = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    assert not etatDepart.isGoal()

    etatResolu = SokobanPuzzle(["OOOO", "OR *", "OOOO"])
    assert etatResolu.isGoal()


def testIsGoalFauxAuDepartPourTousLesNiveaux():
    for niveau in LEVELS:
        etat = SokobanPuzzle(niveau["grid"])
        assert not etat.isGoal(), niveau["name"]


def testSuccesseursNeModifientPasLEtatParent():
    etat = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    grilleAvant = etat.grid
    etat.successorFunction()
    assert etat.grid == grilleAvant


def testNodeRacine():
    etat = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    racine = Node(etat)
    assert racine.parent is None
    assert racine.action is None
    assert racine.g == 0
    assert racine.getPath() == [etat]
    assert racine.getSolution() == []


def testNodeChaineDeTroisNoeuds():
    # Chaine construite a la main : racine -> RIGHT -> RIGHT (poussee de la caisse).
    etat0 = SokobanPuzzle(["OOOOO", "OR BS", "OOOOO"])
    etat1 = etat0.successorFunction()[0][1]
    action1 = etat0.successorFunction()[0][0]
    n0 = Node(etat0)
    n1 = Node(etat1, n0, action1)
    n2 = Node(etat1, n1, "RIGHT")
    assert n1.g == 1
    assert n2.g == 2
    assert n2.parent is n1
    assert n2.getPath() == [etat0, etat1, etat1]
    assert n2.getSolution() == [action1, "RIGHT"]
    assert n1.getSolution() == [action1]


def lancerBFS(etat):
    return BFS(etat, lambda st: st.successorFunction(), lambda st: st.isGoal())


def testBFSEtatInitialDejaBut():
    etat = SokobanPuzzle(["OOOO", "OR *", "OOOO"])
    noeud = lancerBFS(etat)
    assert noeud.g == 0
    assert noeud.getSolution() == []


def testBFSUnePoussee():
    etat = SokobanPuzzle(["OOOOO", "ORBSO", "OOOOO"])
    noeud = lancerBFS(etat)
    assert noeud.getSolution() == ["RIGHT"]
    assert noeud.g == 1
    assert noeud.state.isGoal()


def testBFSSansSolution():
    # Cible a gauche, caisse collee au mur de droite, joueur entre les deux :
    # le joueur ne peut pas passer derriere la caisse, donc aucune solution.
    assert lancerBFS(SokobanPuzzle(["OOOOO", "OSRBO", "OOOOO"])) is None


def testBFSSolutionRejoueeArriveAuBut():
    # On rejoue les actions de la solution avec successorFunction : on doit finir sur un but.
    etat = SokobanPuzzle(LEVELS[0]["grid"])
    noeud = lancerBFS(etat)
    assert noeud is not None
    courant = etat
    for action in noeud.getSolution():
        suivant = None
        for a, st in courant.successorFunction():
            if a == action:
                suivant = st
        assert suivant is not None
        courant = suivant
    assert courant.isGoal()
    assert len(noeud.getSolution()) == noeud.g


if __name__ == "__main__":
    testMurBloqueDeplacement()
    testPousserCaisseDansMurEstIllegale()
    testPousserDeuxCaissesEstIllegale()
    testPousserCaisseSurCibleDonneEtoile()
    testMarcherSurCibleEtLaQuitter()
    testIsGoalFauxAuDepartVraiSurPlateauResolu()
    testIsGoalFauxAuDepartPourTousLesNiveaux()
    testSuccesseursNeModifientPasLEtatParent()
    testNodeRacine()
    testNodeChaineDeTroisNoeuds()
    testBFSEtatInitialDejaBut()
    testBFSUnePoussee()
    testBFSSansSolution()
    testBFSSolutionRejoueeArriveAuBut()
    print("Tous les tests sont passes.")
