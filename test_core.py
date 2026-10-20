# Tests "console" avec de simples assert (pas de pytest).
# On teste les regles (SokobanPuzzle), le Node et le BFS. Lancer : python test_core.py

from sokoban import SokobanPuzzle
from node import Node
from search import BFS
from levels import LEVELS


def test_mur_bloque_deplacement():
    grille = ["OOO", "ORO", "OOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert actions == []


def test_pousser_caisse_dans_mur_est_illegale():
    # Joueur a gauche d'une caisse, mur juste apres la caisse : poussee impossible.
    grille = ["OOOO", "ORBO", "OOOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert "RIGHT" not in actions


def test_pousser_deux_caisses_est_illegale():
    # Joueur puis deux caisses d'affilee : la premiere ne peut pas etre poussee.
    grille = ["OOOOO", "ORBBO", "OOOOO"]
    etat = SokobanPuzzle(grille)
    actions = [action for action, suivant in etat.successorFunction()]
    assert "RIGHT" not in actions


def test_pousser_caisse_sur_cible_donne_etoile():
    grille = ["OOOOO", "ORBSO", "OOOOO"]
    etat = SokobanPuzzle(grille)
    successeurs = dict(etat.successorFunction())
    nouvel_etat = successeurs["RIGHT"]
    assert nouvel_etat.grid == ("OOOOO", "O R*O", "OOOOO")


def test_marcher_sur_cible_et_la_quitter():
    # Le joueur marche sur une cible (S -> .), puis en repart (. -> S).
    grille = ["OOOO", "ORSO", "OOOO"]
    etat = SokobanPuzzle(grille)
    successeurs = dict(etat.successorFunction())
    etat_sur_cible = successeurs["RIGHT"]
    assert etat_sur_cible.grid[1] == "O .O"

    successeurs_retour = dict(etat_sur_cible.successorFunction())
    etat_retour = successeurs_retour["LEFT"]
    assert etat_retour.grid[1] == "ORSO"


def test_pousser_caisse_hors_d_une_cible():
    # La caisse quitte la cible (* -> .) : le joueur se retrouve sur la cible et la caisse redevient B.
    grille = ["OOOOOO", "OR* SO", "OOOOOO"]
    etat = SokobanPuzzle(grille)
    successeurs = dict(etat.successorFunction())
    assert successeurs["RIGHT"].grid[1] == "O .BSO"


def test_niveaux_bien_formes():
    # Chaque niveau : un seul joueur, autant de caisses que de cibles, lignes de meme largeur,
    # et des murs sur tout le bord (le joueur ne peut pas sortir de la grille).
    for niveau in LEVELS:
        grille = niveau["grid"]
        texte = "".join(grille)
        assert texte.count("R") + texte.count(".") == 1, niveau["name"]
        assert texte.count("B") + texte.count("*") == texte.count("S") + texte.count("*") + texte.count("."), niveau["name"]
        for ligne in grille:
            assert len(ligne) == len(grille[0]), niveau["name"]
            assert ligne[0] == "O" and ligne[-1] == "O", niveau["name"]
        assert grille[0] == "O" * len(grille[0]) and grille[-1] == "O" * len(grille[0]), niveau["name"]


def test_is_goal_faux_au_depart_vrai_sur_plateau_resolu():
    etat_depart = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    assert not etat_depart.isGoal()

    etat_resolu = SokobanPuzzle(["OOOO", "OR *", "OOOO"])
    assert etat_resolu.isGoal()


def test_is_goal_faux_au_depart_pour_tous_les_niveaux():
    for niveau in LEVELS:
        etat = SokobanPuzzle(niveau["grid"])
        assert not etat.isGoal(), niveau["name"]


def test_successeurs_ne_modifient_pas_l_etat_parent():
    etat = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    grille_avant = etat.grid
    etat.successorFunction()
    assert etat.grid == grille_avant


def test_node_racine():
    etat = SokobanPuzzle(["OOOO", "ORBS", "OOOO"])
    racine = Node(etat)
    assert racine.parent is None
    assert racine.action is None
    assert racine.g == 0
    assert racine.getPath() == [etat]
    assert racine.getSolution() == []


def test_node_chaine_de_trois_noeuds():
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


def lancer_bfs(etat):
    # Retourne seulement le noeud but (ou None) ; les steps sont testes a part.
    noeud, steps = BFS(etat, lambda st: st.successorFunction(), lambda st: st.isGoal())
    return noeud


def lancer_bfs_steps(etat):
    noeud, steps = BFS(etat, lambda st: st.successorFunction(), lambda st: st.isGoal())
    return steps


def test_bfs_etat_initial_deja_but():
    etat = SokobanPuzzle(["OOOO", "OR *", "OOOO"])
    noeud = lancer_bfs(etat)
    assert noeud.g == 0
    assert noeud.getSolution() == []
    assert lancer_bfs_steps(etat) == 0      # aucun noeud developpe


def test_bfs_une_poussee():
    etat = SokobanPuzzle(["OOOOO", "ORBSO", "OOOOO"])
    noeud = lancer_bfs(etat)
    assert noeud.getSolution() == ["RIGHT"]
    assert noeud.g == 1
    assert noeud.state.isGoal()
    assert lancer_bfs_steps(etat) == 1      # seule la racine est developpee : son enfant est le but


def test_bfs_sans_solution():
    # Cible a gauche, caisse collee au mur de droite, joueur entre les deux :
    # le joueur ne peut pas passer derriere la caisse, donc aucune solution.
    etat = SokobanPuzzle(["OOOOO", "OSRBO", "OOOOO"])
    assert lancer_bfs(etat) is None
    # Les deux seuls etats possibles (joueur a sa place, joueur sur la cible) ont ete developpes.
    assert lancer_bfs_steps(etat) == 2


def test_bfs_solution_rejouee_arrive_au_but():
    # On rejoue les actions de la solution avec successorFunction : on doit finir sur un but.
    etat = SokobanPuzzle(LEVELS[0]["grid"])
    noeud = lancer_bfs(etat)
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


def test_bfs_resout_tous_les_niveaux():
    # Chaque niveau de levels.py a une solution, et la rejouer mene bien a un etat but.
    # On verifie aussi le cout : ce sont les couts minimaux, confirmes par un autre solveur (log session 13).
    # Les steps (noeuds developpes) sont toujours les memes, car les successeurs sont toujours
    # generes dans le meme ordre : si ces nombres changent, c'est que le BFS a ete modifie.
    couts_optimaux = [4, 35, 36, 30, 28, 2, 5, 10]
    steps_attendus = [11, 1806, 6013, 6051, 11659, 3, 12, 571]
    for i in range(len(LEVELS)):
        niveau = LEVELS[i]
        etat = SokobanPuzzle(niveau["grid"])
        noeud, steps = BFS(etat, lambda st: st.successorFunction(), lambda st: st.isGoal())
        assert noeud is not None, niveau["name"]
        assert noeud.g == couts_optimaux[i], niveau["name"]
        assert steps == steps_attendus[i], niveau["name"]
        courant = etat
        for action in noeud.getSolution():
            for a, st in courant.successorFunction():
                if a == action:
                    courant = st
                    break
        assert courant.isGoal(), niveau["name"]


if __name__ == "__main__":
    test_mur_bloque_deplacement()
    test_pousser_caisse_dans_mur_est_illegale()
    test_pousser_deux_caisses_est_illegale()
    test_pousser_caisse_sur_cible_donne_etoile()
    test_marcher_sur_cible_et_la_quitter()
    test_pousser_caisse_hors_d_une_cible()
    test_niveaux_bien_formes()
    test_is_goal_faux_au_depart_vrai_sur_plateau_resolu()
    test_is_goal_faux_au_depart_pour_tous_les_niveaux()
    test_successeurs_ne_modifient_pas_l_etat_parent()
    test_node_racine()
    test_node_chaine_de_trois_noeuds()
    test_bfs_etat_initial_deja_but()
    test_bfs_une_poussee()
    test_bfs_sans_solution()
    test_bfs_solution_rejouee_arrive_au_but()
    test_bfs_resout_tous_les_niveaux()
    print("Tous les tests sont passes.")
