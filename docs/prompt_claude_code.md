# Prompt pour Claude Code — Sokoban (suite et fin)

> Coller ce texte au début d'une nouvelle session Claude Code dans le dépôt.
> Aucun PDF n'est nécessaire : tout ce qu'il faut savoir est écrit ici.

---

## Contexte du projet

Projet Sokoban en Python 3 + Pygame, module M1 Visual Computing, USTHB, Prof. Dr. Meriem SEBAI.
Repo : https://github.com/ademrepo/sokoban  — branche `main`.

### Fichiers clés

```
sokoban.py      classe SokobanPuzzle (état + règles)
node.py         classe Node (parent, action, g, f, getPath, getSolution)
search.py       BFS — retourne (noeud, steps)
astar.py        A* + h1, h2, h3 — retourne (noeud, steps)
levels.py       10 niveaux (Exemples 1-5, Deadlock 1-2, Poussee, Le Detour, Le Carre)
gui.py          interface Pygame (classe Game)
main.py         python main.py | --niveau N | --console | --compare
test_core.py    tests assert (PAS pytest)
docs/PLAN.md    checklist des étapes (0 à 31 cochées)
docs/EXPLICATIONS.md  explications pour la soutenance
```

### Symboles de la grille

```
R  joueur
.  joueur sur cible
O  mur
   case vide (espace)
S  cible vide
B  caisse hors cible
*  caisse sur cible (goal)
```

### Règles du code (OBLIGATOIRES)

- Code style "étudiant" : classes, boucles, if. Pas de dataclasses, decorateurs, threading.
- Commentaires en **français**, identifiants en **anglais**.
- Imports : stdlib + pygame uniquement.
- Une étape de `docs/PLAN.md` par commit. Cocher, dater, loguer, committer, pusher, s'arrêter.
- Tests : `python test_core.py` (assert bruts, pas pytest). Lancer avant de cocher.
- Jamais `git push --force`.
- Ne JAMAIS modifier `docs/Project 1 Part 1.pdf`, `docs/Project 1 Part 3.pdf`, `docs/Chapter 1.pdf`.

---

## Ce qu'il reste à faire

### PRIORITÉ 1 — Interface Pygame (prof check l'interface DEMAIN)

La prof vérifiera l'interface en live. Il faut qu'elle soit irréprochable.

Lire `gui.py` en entier, puis appliquer ces améliorations dans l'ordre :

**A. Tableau de comparaison (`python main.py --compare` ET bouton in-game)**
- Le tableau doit afficher pour chaque algorithme (BFS, A*-h1, A*-h2, A*-h3) :
  - Coût optimal (nombre de coups de la solution)
  - Steps (noeuds développés — mesure de la complexité)
  - Temps de calcul en secondes
- Format lisible : colonnes alignées, entête clair, texte centré.
- Dans le terminal (`--compare`) : tableau texte propre avec `str.ljust` / `str.rjust`.
- In-game (bouton « Comparer ») : tableau Pygame affiché dans la fenêtre.

**B. Écran de sélection de niveau**
- Chaque niveau doit afficher son nom ET un mini-aperçu de la grille (grille dessinée en petit, ~4px par case).
- Boutons cliquables avec effet hover (couleur qui change quand la souris passe dessus).
- Flèches ou scroll si > 8 niveaux (on en a 10).

**C. Barre d'infos en jeu**
- Afficher en permanence : nom du niveau, compteur de coups (manuel), algorithme sélectionné.
- Après une résolution : coût, steps, temps — tout en bas de l'écran.
- Police lisible, fond semi-transparent si nécessaire.

**D. Simulation de la solution**
- Bouton « Simuler » : le chat se déplace automatiquement case par case.
- Vitesse réglable (bouton + / -) ou slider simple.
- Bouton « Pause / Reprendre » pendant la simulation.

**E. Écran de victoire**
- Afficher : « Bravo ! », nombre de coups, temps, boutons « Rejouer », « Niveau suivant », « Menu ».
- Petite animation : le joueur fait une danse ou les caisses scintillent (simple : clignotement de couleur).

**F. Menu principal**
- Titre du jeu en grand.
- Boutons : « Jouer », « Comparer (tous les niveaux) », « Quitter ».
- Fond coloré ou dégradé, pas un fond noir uni.

**G. Polissage général**
- Fenêtre redimensionnable OU taille fixe adaptée au plus grand niveau (grille 10×10 max visible).
- FPS stable (60 FPS avec `clock.tick(60)`).
- Touche `Échap` → retour au menu depuis n'importe quel écran.
- Touche `Z` → annuler le dernier coup (undo, déjà implémenté — vérifier que ça marche).
- Touche `R` → recommencer le niveau.
- Pas de freeze pendant le calcul BFS/A* : afficher « Calcul en cours... » pendant que l'algo tourne.
  (Le calcul est bloquant en Python pur ; afficher le message AVANT d'appeler BFS/A*, puis `pygame.display.flip()`.)

---

### PRIORITÉ 2 — Détection de deadlock (Partie D de l'énoncé)

#### D.1 — Fonction `is_deadlock(etat)` dans `sokoban.py`

Ajouter à la fin de `sokoban.py` (PAS dans une classe séparée, juste des fonctions libres).

**Deadlock d'angle (corner deadlock)**

Une caisse est dans un deadlock d'angle si :
- elle est sur une case qui n'est PAS une cible (`grid[r][c] == 'B'`, pas `*`)
- deux de ses côtés perpendiculaires sont des murs

Les quatre coins possibles à tester :
- haut + gauche : `grid[r-1][c] == 'O'` et `grid[r][c-1] == 'O'`
- haut + droite : `grid[r-1][c] == 'O'` et `grid[r][c+1] == 'O'`
- bas + gauche : `grid[r+1][c] == 'O'` et `grid[r][c-1] == 'O'`
- bas + droite : `grid[r+1][c] == 'O'` et `grid[r][c+1] == 'O'`

```python
def est_coin_deadlock(grid, r, c):
    # Retourne True si la caisse en (r,c) est coincée dans un coin (deux murs perpendiculaires).
    # Ne s'applique qu'aux caisses hors cible ('B'), pas aux '*'.
    if grid[r][c] != 'B':
        return False
    mur_haut  = grid[r-1][c] == 'O'
    mur_bas   = grid[r+1][c] == 'O'
    mur_gauche = grid[r][c-1] == 'O'
    mur_droite = grid[r][c+1] == 'O'
    return (mur_haut and mur_gauche) or (mur_haut and mur_droite) \
        or (mur_bas  and mur_gauche) or (mur_bas  and mur_droite)
```

**Deadlock de ligne (line deadlock / freeze deadlock)**

Une rangée de caisses entre deux positions de corner-deadlock, le long d'un mur, est un deadlock de ligne si :
1. Identifier toutes les positions de corner-deadlock dans la grille.
2. Pour chaque paire de positions de corner-deadlock sur la même ligne (même `r`) :
   - Si toutes les cases entre elles sur cette ligne contiennent `'B'` ou `'O'`
   - ET tous les côtés d'un seul côté (haut OU bas) de cette ligne sont des murs (`'O'`)
   - Alors toutes les caisses dans cette tranche sont en deadlock de ligne.
3. Même chose pour les colonnes (même `c`).

Implémentation suggérée :

```python
def positions_coins_deadlock(grid):
    # Retourne la liste des (r,c) qui sont des positions de corner-deadlock
    # (cases non-cible où deux murs perpendiculaires bloquent).
    coins = []
    for r in range(1, len(grid) - 1):
        for c in range(1, len(grid[r]) - 1):
            if grid[r][c] == 'O':
                continue
            # Case potentiellement accessible : tester les 4 coins
            mur_haut   = grid[r-1][c] == 'O'
            mur_bas    = grid[r+1][c] == 'O'
            mur_gauche = grid[r][c-1] == 'O'
            mur_droite = grid[r][c+1] == 'O'
            if (mur_haut or mur_bas) and (mur_gauche or mur_droite):
                coins.append((r, c))
    return coins

def est_ligne_deadlock(grid, coins):
    # Retourne True si l'état contient un deadlock de ligne.
    # Un deadlock de ligne existe quand, entre deux positions de corner-deadlock
    # sur la même ligne/colonne, toutes les cases contiennent des caisses ('B')
    # et l'intégralité d'un côté (haut ou bas, gauche ou droite) n'est que des murs.

    # --- Lignes horizontales ---
    for r in range(1, len(grid) - 1):
        coins_sur_ligne = sorted([c for (lr, c) in coins if lr == r])
        for i in range(len(coins_sur_ligne)):
            for j in range(i + 1, len(coins_sur_ligne)):
                c1, c2 = coins_sur_ligne[i], coins_sur_ligne[j]
                # Vérifier que toutes les cases entre c1 et c2 sont B ou O
                cases = [grid[r][c] for c in range(c1, c2 + 1)]
                if any(s not in ('B', 'O', 'S', '*') for s in cases):
                    continue
                # Au moins une caisse hors cible dans la tranche
                if 'B' not in cases:
                    continue
                # Vérifier qu'un côté entier (haut ou bas) est mur
                tout_mur_haut = all(grid[r-1][c] == 'O' for c in range(c1, c2 + 1))
                tout_mur_bas  = all(grid[r+1][c] == 'O' for c in range(c1, c2 + 1))
                if tout_mur_haut or tout_mur_bas:
                    return True

    # --- Colonnes verticales ---
    nb_cols = len(grid[0]) if grid else 0
    for c in range(1, nb_cols - 1):
        coins_sur_col = sorted([r for (r, lc) in coins if lc == c])
        for i in range(len(coins_sur_col)):
            for j in range(i + 1, len(coins_sur_col)):
                r1, r2 = coins_sur_col[i], coins_sur_col[j]
                cases = [grid[r][c] for r in range(r1, r2 + 1)]
                if any(s not in ('B', 'O', 'S', '*') for s in cases):
                    continue
                if 'B' not in cases:
                    continue
                tout_mur_gauche = all(grid[r][c-1] == 'O' for r in range(r1, r2 + 1))
                tout_mur_droite = all(grid[r][c+1] == 'O' for r in range(r1, r2 + 1))
                if tout_mur_gauche or tout_mur_droite:
                    return True

    return False

def is_deadlock(etat):
    # Retourne True si l'état est un deadlock (aucune solution possible).
    # Teste d'abord le deadlock d'angle (le moins cher), puis le deadlock de ligne.
    grid = etat.grid
    for r in range(1, len(grid) - 1):
        for c in range(1, len(grid[r]) - 1):
            if est_coin_deadlock(grid, r, c):
                return True
    coins = positions_coins_deadlock(grid)
    return est_ligne_deadlock(grid, coins)
```

#### D.2 — A* avec élagage des deadlocks dans `astar.py`

Ajouter la fonction suivante à la fin de `astar.py` :

```python
from sokoban import is_deadlock   # importer la nouvelle fonction

def AStarDeadlock(s, successorsFn, isGoal, h):
    # Identique à AStar, mais avant d'ajouter un enfant dans Open,
    # on vérifie si son état est un deadlock : si oui, on l'ignore.
    # Cela réduit considérablement le nombre de noeuds développés
    # sur les niveaux Deadlock 1 et Deadlock 2.
    racine = Node(s, None, None)
    racine.setF(h)
    ouvert = []
    numero = 0
    heapq.heappush(ouvert, (racine.f, numero, racine))
    ferme = []
    ouvertF = {}
    fermeF = {}
    ouvertF[racine.state] = racine.f
    steps = 0
    while len(ouvert) > 0:
        f, n, courant = heapq.heappop(ouvert)
        del ouvertF[courant.state]
        if isGoal(courant.state):
            return courant, steps
        steps = steps + 1
        ferme.append(courant)
        fermeF[courant.state] = courant.f
        for action, successeur in successorsFn(courant.state):
            enfant = Node(successeur, courant, action)
            enfant.setF(h)
            # --- élagage deadlock ---
            if is_deadlock(enfant.state):
                continue
            # --- fin élagage ---
            if enfant.state not in ouvertF and enfant.state not in fermeF:
                numero = numero + 1
                heapq.heappush(ouvert, (enfant.f, numero, enfant))
                ouvertF[enfant.state] = enfant.f
            elif enfant.state in ouvertF:
                if ouvertF[enfant.state] > enfant.f:
                    for k in range(len(ouvert)):
                        if ouvert[k][2].state == enfant.state:
                            numero = numero + 1
                            ouvert[k] = (enfant.f, numero, enfant)
                            heapq.heapify(ouvert)
                            break
                    ouvertF[enfant.state] = enfant.f
            else:
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
```

**Attention à l'import circulaire** : `sokoban.py` importe rien d'`astar.py`, mais `astar.py` doit importer `is_deadlock` depuis `sokoban.py`. C'est OK — pas de cycle.

#### D.3 — Test de comparaison sur les niveaux Deadlock 1 et 2

Dans `main.py`, ajouter à l'option `--compare` (ou créer `--deadlock`) un tableau qui compare, pour les niveaux "Deadlock 1" et "Deadlock 2" :

| Algorithme        | Coût | Steps sans deadlock | Steps avec deadlock | Gain (%) |
|-------------------|------|---------------------|---------------------|----------|
| A* h3             | ...  | ...                 | ...                 | ...      |

Afficher aussi ce tableau dans l'interface Pygame (bouton « Deadlock » ou dans le tableau « Comparer »).

---

### PRIORITÉ 3 — Tests

Ajouter dans `test_core.py` (après les tests A* existants) :

```python
# ============================================================
# Tests de la détection de deadlock
# ============================================================
from sokoban import est_coin_deadlock, is_deadlock, SokobanPuzzle

def test_deadlock():
    # --- Deadlock d'angle : coin haut-gauche ---
    grille = [
        "OOOOO",
        "OB  O",
        "O   O",
        "O  SO",
        "OOOOO",
    ]
    etat = SokobanPuzzle(grille)
    # la caisse est en (1,1), avec mur au-dessus (0,1)=O et à gauche (1,0)=O
    assert est_coin_deadlock(etat.grid, 1, 1), "coin haut-gauche attendu"

    # --- Pas de deadlock : la case de la caisse est une cible ---
    grille2 = [
        "OOOOO",
        "O*  O",
        "O   O",
        "O   O",
        "OOOOO",
    ]
    etat2 = SokobanPuzzle(grille2)
    assert not est_coin_deadlock(etat2.grid, 1, 1), "caisse sur cible : pas de deadlock"

    # --- Deadlock d'angle : coin bas-droite ---
    grille3 = [
        "OOOOO",
        "O  SO",
        "O   O",
        "O  BO",
        "OOOOO",
    ]
    etat3 = SokobanPuzzle(grille3)
    assert est_coin_deadlock(etat3.grid, 3, 3), "coin bas-droite attendu"

    # --- is_deadlock : état global ---
    grille4 = [
        "OOOOO",
        "OB  O",
        "O   O",
        "O  SO",
        "OOOOO",
    ]
    assert is_deadlock(SokobanPuzzle(grille4)), "is_deadlock attendu True"

    # --- is_deadlock : état valide (caisse pas coincée) ---
    grille5 = [
        "OOOOO",
        "OR  O",
        "O B O",
        "O S O",
        "OOOOO",
    ]
    assert not is_deadlock(SokobanPuzzle(grille5)), "is_deadlock attendu False"

    # --- AStarDeadlock trouve la même solution qu'AStar sur Exemple 1 ---
    from levels import LEVELS
    from astar import AStar, AStarDeadlock, h3
    niveau = LEVELS[0]  # Exemple 1
    etat_init = SokobanPuzzle(niveau["grid"])
    noeud_astar, steps_astar = AStar(etat_init, etat_init.successorFunction, etat_init.isGoal, h3)
    noeud_dl,    steps_dl    = AStarDeadlock(etat_init, etat_init.successorFunction, etat_init.isGoal, h3)
    assert noeud_astar is not None and noeud_dl is not None
    assert noeud_astar.g == noeud_dl.g, "coût optimal identique avec et sans deadlock"
    # AStarDeadlock développe au plus autant de noeuds qu'AStar
    assert steps_dl <= steps_astar, "AStarDeadlock ne doit pas développer plus de noeuds"

    # --- AStarDeadlock réduit les steps sur les niveaux Deadlock ---
    dl1 = SokobanPuzzle(LEVELS[5]["grid"])   # Deadlock 1
    dl2 = SokobanPuzzle(LEVELS[6]["grid"])   # Deadlock 2
    for etat_dl in [dl1, dl2]:
        n_sans, s_sans = AStar(etat_dl, etat_dl.successorFunction, etat_dl.isGoal, h3)
        n_avec, s_avec = AStarDeadlock(etat_dl, etat_dl.successorFunction, etat_dl.isGoal, h3)
        assert n_sans is not None, "AStar doit trouver une solution"
        assert n_avec is not None, "AStarDeadlock doit trouver une solution"
        assert n_sans.g == n_avec.g, "même coût optimal"
        print(f"  {etat_dl} : steps sans={s_sans}, avec={s_avec}, gain={s_sans - s_avec}")

    print("Tests deadlock : OK")

test_deadlock()
```

---

### PRIORITÉ 4 — Documentation

#### `docs/EXPLICATIONS.md` — ajouter une section § Détection de deadlock

La section doit expliquer en français :

1. **Définition** : un deadlock est un état d'où il est impossible d'atteindre le but, même si le joueur peut encore bouger. L'A* standard continue d'explorer ces états inutilement.

2. **Deadlock d'angle** : une caisse hors cible coincée dans un angle formé par deux murs perpendiculaires ne peut jamais être poussée vers une cible. On la détecte en O(1) par case.

3. **Deadlock de ligne** : si une rangée de caisses forme une ligne le long d'un mur entre deux positions de corner-deadlock, et qu'aucune des cases de cette ligne n'est une cible, l'ensemble est bloqué. Détectée en O(n²) sur le nombre de coins.

4. **Élagage dans A*** : avant d'ajouter un état enfant dans Open, on appelle `is_deadlock()`. Si True, on ignore cet état. L'optimalité de A* est préservée car un état deadlock ne peut mener au but.

5. **Résultats** : montrer le tableau steps_sans vs steps_avec sur Deadlock 1 et 2. Commenter le gain.

#### `docs/PLAN.md` — ajouter l'étape 32

```
- [ ] Étape 32 — Deadlocks : is_deadlock (coin + ligne) dans sokoban.py ; AStarDeadlock dans astar.py ;
      tests dans test_core.py ; tableau comparatif dans main.py --compare et dans l'interface ;
      § deadlock dans EXPLICATIONS.md — AAAA-MM-JJ — docs/logs/AAAA-MM-JJ_session-NN.md
```

---

### PRIORITÉ 5 — Git

À la fin de l'étape 32 :

1. Lancer `python test_core.py` → tous les tests passent.
2. Lancer `python main.py --compare` → tableau s'affiche proprement.
3. Lancer `python main.py` → interface s'ouvre, niveaux Deadlock visibles dans le menu.
4. Cocher l'étape 32 dans `docs/PLAN.md`.
5. Créer `docs/logs/AAAA-MM-JJ_session-NN.md` avec le template habituel.
6. Committer :
   ```
   git add sokoban.py astar.py test_core.py main.py gui.py docs/PLAN.md docs/EXPLICATIONS.md docs/logs/
   git commit -m "Étape 32 : détection de deadlocks (coin + ligne), AStarDeadlock, interface polie"
   git push origin main
   ```

---

## Ordre de travail recommandé

L'interface est vérifiée par la prof DEMAIN. Travailler dans cet ordre :

1. **Interface en premier** (Priorité 1, sections A à G) — c'est ce qui compte demain.
2. Deadlock detection (Priorité 2) — une fois l'interface stable.
3. Tests deadlock (Priorité 3).
4. Documentation (Priorité 4).
5. Git commit final (Priorité 5).

Si le temps manque, sauter la documentation et faire le commit final quand même.

---

## Informations techniques de référence

### Signatures exactes des fonctions existantes

```python
# sokoban.py
class SokobanPuzzle:
    def __init__(self, grid, player_pos=None): ...  # grid = liste de strings
    def isGoal(self): ...                           # True si plus de 'B' dans la grille
    def successorFunction(self): ...                # retourne [(action, SokobanPuzzle), ...]
    # ACTIONS = {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}

# node.py
class Node:
    def __init__(self, state, parent=None, action=None): ...
    # self.g = 0 si racine, sinon parent.g + 1
    # self.f = 0 (calculé par setF)
    def setF(self, h): self.f = self.g + h(self.state)
    def getPath(self): ...    # liste d'états racine→ce noeud
    def getSolution(self): ... # liste d'actions racine→ce noeud

# search.py
def BFS(s, successorsFn, isGoal): ... # retourne (noeud ou None, steps)

# astar.py
def h1(etat): ...   # len(positions(etat, "B"))
def h2(etat): ...   # 2*h1 + somme manhattan(caisse, cible_la_plus_proche)
def h3(etat): ...   # h2 + (manhattan joueur→caisse la plus proche) - 1
def AStar(s, successorsFn, isGoal, h): ... # retourne (noeud ou None, steps)
```

### Niveaux Deadlock : structure

**Deadlock 1** (6 colonnes × 8 lignes) :
- 3 caisses en colonne 3, lignes 2-3-4
- 3 cibles en colonne 1, lignes 2-3-4
- Joueur en (6,2)
- Piège : colonne 4 adjacente au mur droit (col 5) → deadlock d'angle si caisse poussée là

**Deadlock 2** (9 colonnes × 7 lignes) :
- 3 caisses alignées en ligne 3, colonnes 3-4-5
- 3 cibles alignées en ligne 1, colonnes 3-4-5
- Mur intérieur en ligne 4 (cols 0-2 et 6-8), ouverture cols 3-5
- Joueur en (5,4)
- Pièges : coins inférieurs, murs du bas

### BFS / A* reference steps (pour validation)

Sur les 5 exemples (niveaux 0-4) :
- BFS steps :   [11, 1806, 6013, 6051, 11659]
- A*-h3 steps : [5,   979, 2777, 2577,  2241]

---

## Ce qui NE doit PAS être modifié

- `docs/Project 1 Part 1.pdf` et `docs/Project 1 Part 3.pdf` — originaux de la prof
- `docs/Chapter 1.pdf` — cours
- `docs/SPEC.md` — contrat technique (lire si un doute, jamais modifier)
- La logique de `SokobanPuzzle.successorFunction()` — les règles du jeu sont déjà correctes
- La logique de `BFS()` et `AStar()` — déjà corrects et testés

---

*Bonne chance pour la soutenance !*
