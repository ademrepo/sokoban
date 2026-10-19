# Tests "console" avec de simples assert (pas de pytest).
# Sera complété au fur et à mesure des etapes 2, 3, 4 et 5.

from sokoban import SokobanPuzzle
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


if __name__ == "__main__":
    testMurBloqueDeplacement()
    testPousserCaisseDansMurEstIllegale()
    testPousserDeuxCaissesEstIllegale()
    testPousserCaisseSurCibleDonneEtoile()
    testMarcherSurCibleEtLaQuitter()
    testIsGoalFauxAuDepartVraiSurPlateauResolu()
    testIsGoalFauxAuDepartPourTousLesNiveaux()
    testSuccesseursNeModifientPasLEtatParent()
    print("Tous les tests sont passes.")
