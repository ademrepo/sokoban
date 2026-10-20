# Explications du projet Sokoban

Ce document explique le code pour la soutenance : ce que fait chaque fichier, pourquoi on l'a écrit comme ça, et les questions qu'on risque de nous poser. Il suit l'ordre de l'énoncé : A (formulation), B (recherche), C (interface).

---

## 0. Vue d'ensemble

```
levels.py        les 8 niveaux (grilles de texte)
sokoban.py       SokobanPuzzle : un état du jeu + TOUTES les règles (successorFunction)
node.py          Node : un noeud de l'arbre de recherche (state, parent, action, g)
search.py        BFS : l'algorithme du cours (Figure 1.19)
main.py          point d'entrée : python main.py / --niveau N / --console
gui.py           Game : l'interface Pygame
assets_loader.py découpe des sprites + sons calculés par le code
test_core.py     tests avec de simples assert
```

Le chemin d'une partie : `main.py` crée un `Game` → `Game` charge un niveau de `levels.py` dans un `SokobanPuzzle` → chaque flèche demande à `successorFunction()` les coups possibles → le bouton « Résoudre » appelle `BFS(...)` qui construit des `Node` → `getSolution()` donne la liste des actions que l'interface rejoue.

---

## 1. Formulation du problème (énoncé A, cours §1.2.1)

Le cours définit un problème par 4 composants. Voici ce qu'ils sont chez nous :

| Composant du cours | Dans le projet |
|---|---|
| État initial | `SokobanPuzzle(niveau["grid"])`, la grille de départ du niveau |
| Fonction successeur | `SokobanPuzzle.successorFunction()` → liste de paires `(action, successeur)` |
| Test de but | `SokobanPuzzle.isGoal()` → vrai quand il n'y a plus de caisse hors cible |
| Coût du chemin | chaque déplacement coûte 1, donc coût = nombre de déplacements (`Node.g`) |

Une **solution** est une suite d'actions qui mène de l'état initial à un état but. Elle est **optimale** si son coût est le plus petit possible.

### 1.1 L'état (`SokobanPuzzle`)

- La grille est un **tuple de chaînes**, une chaîne par ligne, avec exactement les 7 symboles de l'énoncé :
  `R` joueur, `O` mur, `' '` vide, `S` cible, `B` caisse, `.` joueur sur cible, `*` caisse sur cible.
- Pourquoi un tuple de chaînes ? C'est **immuable** et **hashable**. On peut donc :
  - comparer deux états (`__eq__` compare les grilles) ;
  - les mettre dans un `set` (`__hash__` = hash de la grille), ce qui est indispensable au test « est-ce que cet état est déjà dans Open ou Closed ? » du BFS.
- `init()` de l'énoncé = `__init__` en Python. On y garde aussi la position du joueur (`player_pos`), cherchée une seule fois.
- Tout l'extérieur du labyrinthe est rempli de `O`. Le joueur ne peut donc jamais sortir de la grille, et on n'a pas besoin de tester les bords.

### 1.2 Les actions

```
UP = (-1, 0)   DOWN = (1, 0)   LEFT = (0, -1)   RIGHT = (0, 1)
```
Elles sont toujours essayées dans cet ordre, donc le BFS donne toujours la même solution d'un lancement à l'autre.

### 1.3 `successorFunction()` : les règles du jeu

**C'est le seul endroit du programme où sont écrites les règles.** L'interface ne les réécrit pas : elle demande la liste des successeurs et prend celui de la touche appuyée.

Pour chaque direction `(dr, dc)`, le joueur est en `(r, c)` :
- `n1 = (r+dr, c+dc)` est la case où il veut aller ;
- `n2 = (r+2dr, c+2dc)` est la case derrière, utile seulement s'il pousse une caisse.

| Case n1 | Ce qui se passe |
|---|---|
| `O` (mur) | coup impossible |
| `' '` ou `S` (libre) | le joueur avance (`nouvelle_grille(..., pousse=False)`) |
| `B` ou `*` (caisse) | si n2 est `' '` ou `S` : le joueur pousse la caisse (`nouvelle_grille(..., pousse=True)`) ; sinon (mur ou autre caisse) : impossible |

Mise à jour des cases (on construit une **nouvelle** grille, on ne modifie jamais l'état actuel) :
- case quittée : `R` → `' '` et `.` → `S` (on « découvre » la cible) ;
- case d'arrivée du joueur : `' '` → `R`, `S` → `.`, `B` → `R`, `*` → `.` ;
- case d'arrivée de la caisse : `' '` → `B`, `S` → `*`.

Ce que ça garantit (les règles de l'énoncé) : pas de passage à travers un mur, pas de tirage de caisse, pas deux caisses poussées d'un coup, pas de marche sur une caisse sans la pousser.

Exemple sur l'Exemple 1 (le joueur `R` est en ligne 2, colonne 3) :
```
OOOOOO
OS B O     UP    : n1 = (1,3) = 'B', n2 = (0,3) = 'O'  → caisse contre un mur : impossible
O OR O     LEFT  : n1 = (2,2) = 'O'                    → mur : impossible
O    O     DOWN  : n1 = (3,3) = ' '                    → le joueur descend
O    O     RIGHT : n1 = (2,4) = ' '                    → le joueur va à droite
OOOOOO
```
`successorFunction()` renvoie donc 2 paires : `("DOWN", ...)` et `("RIGHT", ...)`.

### 1.4 `isGoal()`

Le but est atteint quand **il ne reste aucun `B`** dans la grille. Il y a autant de cibles que de caisses : s'il n'y a plus de `B`, toutes les caisses sont des `*`, donc chacune est sur une cible. On n'attribue pas une cible précise à chaque caisse, comme le dit l'énoncé (« in any order »).

---

## 2. Le noeud (`Node`, énoncé A.2, cours §1.3)

```
Node(state, parent=None, action=None)
  g = 0 pour la racine, sinon parent.g + 1
```
- Le cours donne 5 champs (state, parent, action, g, profondeur). L'énoncé n'en garde que 4. Comme chaque pas coûte 1, **g = profondeur**.
- `getPath()` remonte les liens `parent` jusqu'à la racine, puis inverse la liste : on obtient les états du début à la fin.
- `getSolution()` fait pareil avec les actions, sans la racine (son action est `None`).

L'interface utilise les deux : `getSolution()` pour rejouer les coups, `getPath()` pour tracer la trajectoire du chat (position du joueur dans chaque état).

---

## 3. La recherche : BFS (énoncé B, cours §1.3.3.1, Figure 1.19)

`search.py` suit le pseudo-code du cours ligne par ligne :

| Pseudo-code du cours | Code |
|---|---|
| `init_node <- Node(s, None, None)` | `racine = Node(s, None, None)` |
| `if isGoal(init_node.state) return init_node` | `return racine, 0` |
| `Open: queue (FIFO)` | `ouvert = deque()` |
| `Closed: list` | `ferme = []` |
| `while (not Open.empty())` | `while len(ouvert) > 0:` puis `steps = steps + 1` |
| `current <- Open.dequeue()` | `courant = ouvert.popleft()` (le moins profond) |
| `Closed.add(current)` | `ferme.append(courant)` |
| `for each (action, successor) in successorsFn(...)` | idem |
| `child <- Node(successor, current, action)` | `enfant = Node(successeur, courant, action)` |
| `if child.state not in Closed and not in Open` | test sur `fermeSet` / `ouvertSet` |
| `if isGoal(child.state) return child` | `return enfant, steps` (test au moment de la génération) |
| `Open.enqueue(child)` | `ouvert.append(enfant)` |
| `return None` | `return None, steps` |

**`steps`, demandé en cours :** le BFS renvoie deux valeurs, le nœud but (ou `None`) **et** `steps`. C'est un compteur qui augmente à chaque tour de la boucle sur Open, donc le nombre de nœuds **développés**. Il mesure le travail fait par la recherche (sa complexité en temps). Il vaut 0 si l'état initial est déjà un but. À ne pas confondre avec le **coût** `g`, qui est la longueur de la solution trouvée.

**Différence avec le pseudo-code : deux ensembles en plus (`ouvertSet`, `fermeSet`).** Chercher un état dans une liste prend un temps proportionnel à sa longueur ; dans un `set`, c'est presque immédiat. Ces ensembles contiennent exactement les mêmes états que `ouvert` et `ferme` et sont mis à jour en même temps. L'algorithme ne change pas, il va juste beaucoup plus vite. Sans eux, l'Exemple 5 prendrait des minutes.

Appel : `noeud, steps = BFS(etat, lambda s: s.successorFunction(), lambda s: s.isGoal())`. On passe les fonctions en paramètre, comme dans la signature du cours.

**On manipule des nœuds, pas directement des états :** Open et Closed contiennent des `Node`. Grâce au lien `parent` de chaque nœud, on reconstruit la solution (`getSolution`) une fois le but trouvé. En revanche, pour savoir si un état a « déjà été vu », on compare les **états par leur contenu** (`__eq__` et `__hash__` comparent les grilles), pas les objets Python. Deux plateaux identiques créés séparément sont deux objets différents, mais c'est le même état.

### Propriétés (données par le cours)
- **Complet** : si une solution existe, BFS la trouve (le but le moins profond est à une profondeur finie d).
- **Optimal** quand toutes les actions ont le même coût. C'est notre cas (coût 1) : la solution trouvée a **le plus petit nombre de déplacements possible**. Ce sont les déplacements qui comptent, pas seulement les poussées.
- **Temps et mémoire** : O(b^d), avec b ≤ 4 (le nombre de directions) et d la longueur de la solution. Tous les états d'une profondeur sont gardés en mémoire avant de passer à la suivante, d'où le temps plus long sur les grands niveaux.

### Résultats (`python main.py --console`)

| Niveau | Coût (longueur de la solution) | Steps (nœuds développés) | Temps BFS |
|---|---|---|---|
| Exemple 1 | 4 | 11 | 0,000 s |
| Exemple 2 | 35 | 1 806 | 0,06 s |
| Exemple 3 | 36 | 6 013 | 0,13 s |
| Exemple 4 | 30 | 6 051 | 0,14 s |
| Exemple 5 | 28 | 11 659 | 0,24 s |
| Maison 1 | 2 | 3 | 0,000 s |
| Maison 2 | 5 | 12 | 0,000 s |
| Maison 3 | 10 | 571 | 0,01 s |

(Temps mesurés sur le PC de développement ; ils changent d'un ordinateur à l'autre. Les coûts et les steps, eux, sont toujours les mêmes, et les tests les vérifient. Les coûts ont été confirmés par un solveur indépendant, voir session 13.)

Ce tableau montre bien la différence : une solution de 28 coups (Exemple 5) a demandé de développer 11 659 nœuds. Les steps grandissent beaucoup plus vite que le coût, c'est le O(b^d) du cours.

---

## 4. L'interface (énoncé C) : `gui.py`

### 4.1 Organisation
Une seule classe `Game`, avec la boucle classique de Pygame (60 images par seconde) :
```
while en_cours:
    handle_events()   # clavier / souris
    update()          # avance les animations et la lecture automatique
    draw()            # dessine tout
```
Le jeu est piloté par une variable `phase` :
```
menu → jeu → ouverture → marche → queue → bravo ─(bouton « Niveau suivant »)→ glisse → jeu
```
- `menu` : choix du niveau (cartes avec un aperçu ; clic, touches 1 à 8, ou flèches + Entrée).
- `jeu` : on joue. **La victoire est décidée uniquement par `isGoal()`.**
- `ouverture` : la porte s'ouvre et s'illumine.
- `marche` : le chat va jusqu'à la porte.
- `queue` : il remue la queue.
- `bravo` : la pancarte descend et **attend** : « Rejouer », « Niveau suivant » ou « Menu ».
- `glisse` : l'ancien niveau sort à gauche, le nouveau entre à droite.

### 4.2 Jouer à la main
`bouger(action)` parcourt `successorFunction()` et prend le successeur qui porte le nom de la touche. Si l'action n'est pas dans la liste (mur, caisse bloquée), l'état ne change pas. **Aucune règle n'est réécrite dans l'interface.**

Le reste de `bouger` ne sert qu'à l'animation :
- on retient la case de départ et d'arrivée du chat. Si la case d'arrivée contenait une caisse dans l'ancien état, c'est qu'elle a été poussée : on retient aussi son déplacement ;
- pendant 140 ms, le chat et la caisse **glissent** d'une case à l'autre. `avancement()` donne un nombre entre 0 et 1 qui ralentit à la fin (`1 - (1 - t)²`), ce qui rend le mouvement plus doux. Le chat fait un petit saut et se tourne vers la gauche ou la droite ;
- si le coup est refusé, le chat fait un petit « choc » vers l'obstacle : on voit que la touche a été prise en compte ;
- confort : une flèche appuyée pendant un pas est jouée juste après, et une flèche gardée appuyée fait avancer le chat en continu ;
- **Annuler** (Z) : chaque état précédent est gardé dans `historique` (les états ne sont jamais modifiés, donc on peut les garder tels quels) ; annuler, c'est reprendre le dernier.

### 4.3 Bouton « Résoudre (BFS) » : la simulation de la solution
1. On lance `BFS` depuis la position **actuelle** : on peut donc jouer quelques coups puis demander la solution.
2. On mesure le temps avec `time.time()` avant et après.
3. On affiche « BFS : coût X | Y steps | Z s » : le coût de la solution, le nombre de nœuds développés et le temps.
4. `getPath()` donne la trajectoire, dessinée en bleu sur le sol ; elle raccourcit à mesure que le chat avance.
5. La lecture automatique rejoue `getSolution()` : un coup toutes les 260 ms, avec la même fonction `bouger`.

### 4.4 La fin de niveau
La victoire n'est déclarée qu'une fois le dernier pas fini, pour qu'on voie la caisse arriver. L'animation de fin ne compte ni dans les coups ni dans le coût. Pour amener le chat devant la porte, `chemin_vers_porte` fait un petit parcours en largeur sur les cases (même idée que le BFS : une file et les cases déjà vues). Ce n'est pas un coup du jeu, juste un chemin pour l'animation. La porte est un simple dessin : la case reste un mur.

### 4.5 Les dessins
- Herbe, sol, murs, caisses, décor (arbres, statues, banc, vases, tonneaux, lanternes...) et porte viennent du pack « Pixel Art Top Down - Basic » (Cainos, itch.io), découpés dans `assets_loader.py`.
- Le chat, les plaques cibles, la pancarte, les boutons et les cartes du menu sont dessinés avec `pygame.draw`.
- **Décor** : il est posé par des règles fixes (pas de hasard), et `poser` vérifie toutes les cases que l'image recouvre. Un objet qui toucherait le niveau ou un autre objet n'est pas posé, donc le même décor s'adapte aux petits et aux grands niveaux.
- **Fond pré-dessiné** : ce qui ne bouge jamais (herbe, haie, décor, murs, sol) est dessiné une seule fois par niveau (`preparer_fond`), puis recopié à chaque image. On ne redessine que ce qui bouge.
- **Effets** (`dessiner_effets`) : ombres de nuages qui passent, lucioles qui clignotent, poussière quand on pousse une caisse et étincelles quand elle arrive sur une cible ; les cibles « respirent », un halo doré entoure une caisse bien placée, les bords de l'image sont un peu assombris (vignette). Le chat respire et remue la queue quand il attend. Tout est fait avec des cercles et des ellipses transparents (`creer_halo`), sans image en plus. Ces effets ne touchent jamais à l'état du jeu.

### 4.6 Les sons
Il n'y a aucun fichier audio : les sons sont **calculés** dans `assets_loader.py`. Un son n'est qu'une suite de nombres entre -1 et 1 (22 050 par seconde) :
- le vent : un bruit aléatoire « adouci » (on garde une moyenne qui suit lentement le bruit), dont le volume monte et descend ;
- les oiseaux : une sinusoïde dont la fréquence monte vite ;
- le pas : un bruit très court qui s'éteint vite.

La touche S coupe le son. Si l'ordinateur n'a pas de son, le jeu marche quand même.

---

## 5. Les tests (`python test_core.py`)
16 tests, avec de simples `assert` :
- **règles** : un mur bloque ; pousser une caisse dans un mur, ou deux caisses, est interdit ; une caisse poussée sur une cible devient `*` ; une caisse poussée hors d'une cible redevient `B` ; marcher sur une cible puis la quitter ; un successeur ne modifie pas l'état parent ;
- **niveaux** : bien formés (un seul joueur, autant de caisses que de cibles, bord en murs), pas déjà résolus au départ ;
- **`isGoal`** et **`Node`** : la racine, une chaîne de trois noeuds ;
- **BFS** : un état déjà but (0 step), une seule poussée (1 step), un niveau sans solution (2 steps), et tous les niveaux sont résolus avec leur **coût optimal** (4, 35, 36, 30, 28, 2, 5, 10) et leur nombre de **steps** attendu ; la solution de chaque niveau, rejouée avec `successorFunction`, arrive bien au but.

---

## 6. Questions probables à l'oral

**Pourquoi BFS trouve la solution la plus courte ?**
Il explore niveau par niveau : tous les états à 1 coup, puis tous ceux à 2 coups, etc. Le premier but trouvé est donc à la profondeur minimale. Comme chaque coup coûte 1, c'est aussi le coût minimal.

**C'est quoi la fonction successeur ?**
La fonction qui répond à « depuis cet état, où peut-on aller ? ». Elle renvoie la liste des paires (action, état enfant), une par coup légal. Un enfant est une copie du père avec une seule modification (le déplacement), et le père n'est jamais modifié. C'est `successorFunction()`, le seul endroit où sont écrites les règles.

**Pourquoi le BFS manipule des nœuds et pas directement des états ?**
Un état ne sait pas d'où il vient. Un nœud garde son père et l'action qui y mène : une fois le but trouvé, on remonte les pères pour obtenir la solution. Mais pour le test « déjà vu ? », on compare les états par leur contenu (la grille), jamais les objets Python eux-mêmes.

**Que représente `steps` ?**
Le nombre de tours de la boucle sur Open, donc de nœuds développés : c'est le travail fait par la recherche. Le coût, lui, est la longueur de la solution. Exemple 5 : coût 28, mais 11 659 steps.

**Pourquoi tester `isGoal` à la génération et pas à la sortie de la file ?**
C'est ce que fait le pseudo-code du cours (Fig. 1.19). Avec des coûts tous égaux à 1, ça ne change pas l'optimalité, et ça évite de développer un niveau de plus.

**À quoi servent Open et Closed ?**
Open contient les noeuds générés mais pas encore développés (la « frontière »). Closed contient les noeuds déjà développés. Ne pas remettre un état déjà vu évite de tourner en rond (aller-retour gauche-droite à l'infini) et d'explorer deux fois la même chose.

**Pourquoi des `set` en plus ?**
Uniquement pour la vitesse du test « déjà vu ? ». Ce sont les mêmes états que dans les listes, donc l'algorithme est inchangé.

**Pourquoi l'état est un tuple et pas une liste ?**
Une liste n'est pas hashable, on ne pourrait pas la mettre dans un `set`. Un tuple ne change pas : un successeur est toujours une nouvelle grille, et l'état parent reste intact (c'est testé).

**Pourquoi `isGoal` = « plus de `B` » ?**
Il y a autant de caisses que de cibles. Plus de `B` veut dire que toutes les caisses sont sur une cible (`*`), dans n'importe quel ordre.

**Qu'est-ce qui est lent et pourquoi ?**
Le BFS sur les grands niveaux (Exemple 5 : 11 659 nœuds développés, entre 0,2 et 1,3 s selon l'ordinateur), car le nombre d'états grandit très vite avec la profondeur (O(b^d)). Pendant ce calcul, la fenêtre attend : on n'utilise pas de thread, pour garder le code simple.

**Pourquoi pas de détection de blocage (caisse coincée dans un coin) ?**
L'énoncé ne le demande pas. Le BFS finit quand même : il explore ces états puis les abandonne quand ils n'ont plus de successeurs nouveaux.

**Où sont les règles du jeu ?**
Uniquement dans `successorFunction()`. L'interface, la lecture automatique et le BFS l'utilisent tous les trois.
