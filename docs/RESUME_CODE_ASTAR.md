# Résumé du code et explication de A* (heuristiques h1, h2, h3)

Document de synthèse : comment le projet est organisé, puis comment A* et ses heuristiques sont implémentés.
Les numéros de ligne et les noms viennent du code à la version `755e802`.

## 1. Vue d'ensemble

| Fichier | Rôle |
|---|---|
| `levels.py` | Les 8 niveaux (`LEVELS`) : liste de dictionnaires `{"name", "grid"}`, la grille est une liste de chaînes. |
| `sokoban.py` | Classe `SokobanPuzzle` : un **état** (la grille) + **toutes les règles** (`successorFunction`, `isGoal`). |
| `node.py` | Classe `Node` : un noeud de l'arbre de recherche (`state`, `parent`, `action`, `g`, `f`). |
| `search.py` | `BFS` (cours, Fig. 1.19). |
| `astar.py` | `AStar` (cours, Fig. 1.29) + les trois heuristiques `h1`, `h2`, `h3`. |
| `gui.py` | Interface Pygame (`Game`) : réutilise `successorFunction`, ne recode aucune règle. |
| `main.py` | Point d'entrée : jeu, `--console` (BFS), `--compare` (tableau BFS / A*), `--niveau N`. |
| `test_core.py` | Tests `assert` (`python test_core.py`). |

Principe central : **les algorithmes de recherche ne connaissent pas Sokoban**. Ils reçoivent trois choses :
un état initial, une fonction `successorsFn(état)` qui renvoie des `(action, état suivant)`, et un test `isGoal(état)`.
A* reçoit en plus une fonction `h(état)`. Les appels se font toujours ainsi :

```python
AStar(etat, lambda st: st.successorFunction(), lambda st: st.isGoal(), h)
```

## 2. Représentation d'un état

Symboles de la grille : `O` mur, ` ` vide, `S` cible vide, `B` caisse hors cible, `*` caisse sur cible,
`R` joueur, `.` joueur sur une cible.

- `SokobanPuzzle.grid` est un **tuple de chaînes** : immuable donc hashable. `__eq__` et `__hash__` portent sur la grille,
  ce qui permet d'utiliser un état comme clé de dictionnaire ou dans un `set` (indispensable pour Open/Closed).
- `player_pos` est stocké pour ne pas rechercher le joueur dans la grille à chaque état : un successeur reçoit directement
  sa nouvelle position (`n1`). `h3` s'en sert.
- `isGoal` : il n'y a plus de `B` dans la grille (autant de cibles que de caisses, donc toutes sont des `*`).
- `successorFunction` : pour UP, DOWN, LEFT, RIGHT (dans cet ordre, donc résultat déterministe) :
  case libre (` ` ou `S`) → le joueur avance ; caisse (`B` ou `*`) → poussée seulement si la case derrière est libre ; mur → rien.
  `nouvelle_grille` fabrique la nouvelle grille sans toucher à l'ancienne.
- **Chaque action coûte 1**, qu'on pousse ou non. Donc `g` = nombre de déplacements = profondeur du noeud.

## 3. Le noeud (`node.py`)

```
Node(state, parent, action)
  g = 0 si racine, sinon parent.g + 1
  f = 0 au départ ; setF(h) calcule f = g + h(state)
  getPath()     -> états de la racine à ce noeud
  getSolution() -> actions de la racine à ce noeud
```

Le BFS n'utilise pas `f`. A* appelle `enfant.setF(h)` pour chaque noeud créé : c'est le seul endroit où l'heuristique entre dans le code.
Une fois le noeud but trouvé, `getSolution()` remonte les `parent` pour reconstruire la liste d'actions.

## 4. L'algorithme A* (`astar.py`, fonction `AStar`)

Le code est recopié sur la Figure 1.29 du cours (commit `f85b3c2`) : Open = tas, Closed = liste, trois cas.

### 4.1 Idée

Le BFS développe toujours le noeud **le moins profond** (file FIFO). A* développe le noeud qui a le **plus petit f = g + h** :

- `g` : ce que l'on a **déjà payé** pour arriver à cet état (exact, = nombre de déplacements) ;
- `h` : une **estimation** de ce qu'il reste à payer jusqu'au but (donnée par l'heuristique) ;
- `f` : estimation du coût total d'une solution qui passe par cet état.

Avec `h = 0` partout, A* se comporte comme un BFS. Plus `h` est informative, moins A* développe de noeuds.

### 4.2 Les structures, une par une

| Variable | Type | Rôle |
|---|---|---|
| `ouvert` | liste gérée comme un **tas** par `heapq`, éléments `(f, numero, noeud)` | **Open**. `heappop` sort toujours le plus petit `f`. |
| `numero` | entier qui augmente à chaque ajout | Si deux noeuds ont le même `f`, Python compare l'élément suivant du tuple : le plus ancien sort d'abord. Sans lui, Python devrait comparer deux `Node` (impossible, erreur). |
| `ferme` | liste de `Node` | **Closed** : noeuds déjà développés. |
| `ouvertF` | dictionnaire `état -> f` | Copie de Open **pour la vitesse seulement**. Répond vite à « cet état est-il dans Open, avec quel f ? » sans parcourir le tas. |
| `fermeF` | dictionnaire `état -> f` | Pareil pour Closed. |
| `steps` | entier | Nombre de noeuds développés. C'est la mesure du travail, comparable au BFS. |

Les dictionnaires ne changent pas l'algorithme : ils contiennent exactement les mêmes états que `ouvert` et `ferme`
(on les met à jour à chaque ajout / retrait). C'est le même principe que `ouvertSet` et `fermeSet` dans `BFS`.
Un état peut être une clé car `SokobanPuzzle` définit `__hash__` et `__eq__`.

### 4.3 Déroulement, ligne par ligne

**Initialisation**
```python
racine = Node(s, None, None)   # g = 0
racine.setF(h)                 # f = 0 + h(état initial)
ouvert = [] ; heapq.heappush(ouvert, (racine.f, 0, racine))
ferme = [] ; ouvertF = {racine.state: racine.f} ; fermeF = {}
steps = 0
```

**Boucle principale** (`while len(ouvert) > 0`) :

1. `f, n, courant = heapq.heappop(ouvert)` : on prend le noeud de plus petit `f`. Les deux premières valeurs du tuple ne servent plus.
2. `del ouvertF[courant.state]` : il n'est plus dans Open.
3. `if isGoal(courant.state): return courant, steps` : **le but est testé ici, à la sortie de Open**, pas quand on crée l'enfant (voir 4.5).
4. Sinon : `steps += 1`, on met `courant` dans `ferme` et `fermeF` : il est développé.
5. Pour chaque `(action, successeur)` de `successorsFn(courant.state)` (donc `successorFunction`, les règles du jeu) :
   - `enfant = Node(successeur, courant, action)` → `enfant.g = courant.g + 1` ;
   - `enfant.setF(h)` → `enfant.f = enfant.g + h(successeur)` ;
   - puis **trois cas**, selon que l'état de l'enfant a déjà été vu :

| Cas | Condition | Ce que fait le code |
|---|---|---|
| **1. Nouvel état** | ni dans `ouvertF` ni dans `fermeF` | `heappush` dans Open, on note son `f` dans `ouvertF`. |
| **2. Déjà dans Open** | dans `ouvertF` | Si le `f` déjà dans Open est **plus grand** que celui de l'enfant (`ouvertF[état] > enfant.f`), l'enfant est un meilleur chemin vers le même état : on **cherche** l'ancien noeud dans `ouvert` (boucle sur `k`), on le **remplace** par `(enfant.f, numero, enfant)`, puis `heapq.heapify(ouvert)` **remet le tas en ordre**. Sinon on ignore l'enfant. |
| **3. Déjà dans Closed** | dans `fermeF` (l'`else`) | Si le `f` dans Closed est **plus grand** que celui de l'enfant, on **retire** l'ancien noeud de `ferme` (boucle + `pop(k)`) et de `fermeF`, et on met l'enfant dans Open (`heappush`). Cet état sera donc redéveloppé, avec son meilleur chemin. Sinon on ignore l'enfant. |

**Fin** : si Open est vide sans avoir trouvé de but → `return None, steps` (pas de solution).

### 4.4 Pourquoi les cas 2 et 3 existent

Le même état du jeu peut être atteint par plusieurs chemins (par exemple avancer puis reculer revient au même état). On ne garde que le
chemin de plus petit `f`. Le cas 3 (rouvrir un état de Closed) est nécessaire parce que, avec une heuristique qui n'est pas « cohérente »,
un état déjà développé peut être retrouvé plus tard par un chemin moins cher.

Coût de cette version fidèle au cours : chercher un noeud dans une liste et `heapify` sont en O(n), plus lents que l'astuce « noeud fantôme »
de l'ancienne version. C'est un choix assumé : le code ressemble exactement au pseudo-code.

### 4.5 Pourquoi tester le but à la sortie de Open

Le premier but **généré** n'est pas forcément le meilleur : un autre noeud de `f` plus petit est peut-être encore dans Open.
Quand un noeud **sort** de Open, on est sûr qu'il a le plus petit `f` de tous ; si c'est un but, `f = g` (car `h = 0` au but) et c'est
la solution de plus petit coût (si `h` est admissible). Le BFS peut tester à la génération car tous les pas coûtent 1 et il explore par profondeur.

### 4.6 Exemple minuscule : Exemple 1 avec h3

```
OOOOOO
OS B O      S = cible en (1,1) ; B = caisse en (1,3) ; R = joueur en (2,3)
O OR O
```
- Racine : `g=0`, `h3 = 4`, donc `f = 4` (h1 = 1, h2 = 2×1 + |1−1|+|3−1| = 4, joueur à 1 case de la caisse : 4 + 1 − 1 = 4).
- Successeurs de la racine : UP impossible (la caisse serait contre le mur), LEFT est un mur. Reste DOWN et RIGHT : `g=1`, `h3=5`, `f=6` chacun
  (le joueur s'éloigne de la caisse : sa distance passe de 1 à 2). Égalité de `f` → celui ajouté en premier (plus petit `numero`) sort d'abord.
- A* trouve `RIGHT, UP, LEFT, LEFT` (coût 4, le même que le BFS) en développant **5** noeuds, contre 11 pour le BFS et pour h1.

## 5. Le système d'heuristiques

### 5.1 Comment ça se branche dans le code

Une heuristique est **une simple fonction `h(etat) -> nombre`**. `AStar` la reçoit en paramètre et ne sait rien d'autre d'elle.
Changer d'heuristique = passer une autre fonction. C'est ce que font `main.py` et `gui.py` :

```python
algos = [("BFS", None), ("A* h1", h1), ("A* h2", h2), ("A* h3", h3)]   # None -> on lance BFS à la place
```

Fonctions utilitaires partagées :

- `positions(etat, symboles)` : liste des `(ligne, colonne)` des cases dont le symbole est dans `symboles`
  (ex. `"B"` = caisses hors cible ; `"S."` = cibles libres : cible vide, ou cible où se trouve le joueur).
- `distance_manhattan(a, b)` = `|xa - xb| + |ya - yb|` (équation 2 de l'énoncé).

### 5.2 `h1` : caisses mal placées

```python
def h1(etat):
    return len(positions(etat, "B"))
```

Nombre de caisses qui ne sont pas encore sur une cible. Chaque caisse demande au moins un déplacement, donc **h1 ne surestime jamais** (admissible).
Mais elle est très faible : elle ignore les distances, A* est presque un BFS (voir tableau).

### 5.3 `h2` : caisses mal placées + distance de Manhattan

```python
h2 = 2 * h1 + somme_sur_caisses( distance(caisse, cible libre la plus proche) )
```

Pour chaque caisse hors cible, on cherche (boucle) la cible libre la plus proche en Manhattan et on additionne ; on ajoute `2 × h1`
(équation 3 de l'énoncé). La distance mesure le nombre de poussées minimal, le terme `2 × h1` valorise le fait de poser une caisse.
Remarque d'honnêteté : à cause du terme `2 × h1`, h2 **peut dépasser** le vrai coût restant, donc l'optimalité n'est pas *prouvée* ;
sur les 8 niveaux, le coût trouvé est pourtant le même que celui du BFS (optimal).
Chaque caisse choisit sa cible indépendamment : deux caisses peuvent viser la même cible, ce qui est une simplification volontaire.

### 5.4 `h3` : h2 + trajet du joueur (heuristique proposée)

```python
h3 = h2 + distance(joueur, caisse hors cible la plus proche) - 1      # et 0 s'il n'y a plus de caisse hors cible
```

Raisonnement « comme un humain » :

1. h2 ne regarde que les caisses. Or ce n'est pas la caisse qui avance : c'est le joueur qui doit d'abord **marcher jusqu'à elle**.
2. Ce trajet **coûte** (chaque déplacement coûte 1) mais h2 l'ignore : deux états avec les mêmes caisses mais un joueur collé à une caisse
   dans l'un et au fond de la salle dans l'autre auraient le même `h2`.
3. Le cours fait pareil dans l'exemple du labyrinthe : `h` = distance de Manhattan entre l'agent et son but (ici : le joueur et la caisse la plus proche).
4. Le « − 1 » : pour pousser il suffit d'être **à côté** de la caisse, pas dessus.
5. Une seule idée ajoutée, facile à coder et à justifier. Pas de détection de blocage (deadlock) : non demandé.

`h3` utilise `etat.player_pos`, c'est pourquoi `SokobanPuzzle` mémorise la position du joueur.

### 5.5 Résultats mesurés (`python main.py --compare`, steps = noeuds développés)

| Niveau | BFS | A* h1 | A* h2 | A* h3 | Coût |
|---|---|---|---|---|---|
| Exemple 1 | 11 | 11 | 8 | 5 | 4 |
| Exemple 2 | 1806 | 1827 | 1400 | 979 | 35 |
| Exemple 3 | 6013 | 5984 | 3126 | 2777 | 36 |
| Exemple 4 | 6051 | 5475 | 3023 | 2577 | 30 |
| Exemple 5 | 11659 | 10190 | 2980 | 2241 | 28 |
| Maison 3 | 571 | 606 | 131 | 89 | 10 |
| Maison 4 | 11785 | 9792 | 1796 | 1349 | 20 |

Lecture : h1 ≈ BFS ; h2 divise les steps par 2 à 6 ; h3 gagne encore 10 à 30 % sur h2. Le coût de solution est identique pour les 4 algorithmes
sur les 8 niveaux. En temps, A* n'est pas toujours plus rapide que le BFS (calcul de `h` à chaque noeud), surtout avec h1.

## 6. Utilisation dans l'interface et la console

- `python main.py` : jeu Pygame ; boutons BFS / A* h1 / h2 / h3 / Comparer (touches `B`, `1`, `2`, `3`, `C`). `gui.py` appelle
  `BFS` ou `AStar` avec `successorFunction` et `isGoal` de l'état courant, affiche coût, steps et temps, puis rejoue la trajectoire
  avec `getSolution()`.
- `python main.py --compare` : tableau de comparaison en console.
- `python test_core.py` : vérifie les règles, BFS et A* (steps attendus par heuristique).

## 7. Points à retenir pour l'oral

1. Les règles du jeu vivent **uniquement** dans `successorFunction` ; BFS et A* sont génériques.
2. A* = BFS dont la file FIFO est remplacée par une file de priorité triée par `f = g + h`.
3. Test du but à la sortie de Open pour A*, à la génération pour le BFS.
4. Les trois cas d'A* (nouvel état / déjà dans Open / déjà dans Closed) gardent toujours le chemin de plus petit `f` pour chaque état.
5. Une heuristique est une fonction passée en paramètre ; h1 est admissible mais faible, h2 et h3 sont plus informées mais non prouvées admissibles.
6. Le gain d'une heuristique se mesure en **steps** (noeuds développés), pas forcément en temps.
