# Explications du projet Sokoban (version pedagogique)

Ce document explique le projet comme une personne qui reprend un code deja ecrit par d'autres membres de l'equipe.
Le but est de comprendre clairement :
- ce que la prof demande dans Project 1 Part 1,
- ou chaque exigence se trouve dans le code,
- et la logique des fonctions importantes (BFS, successorFunction, isGoal).

---

## 1) Ce que la prof demande (resume simple)

La consigne Project 1 Part 1 est organisee en 3 parties.

1. A. Problem formulation
- Modeliser l'etat du jeu Sokoban.
- Modeliser le noeud de recherche.

2. B. Searching for a solution
- Resoudre avec BFS (Breadth-First Search), en suivant le pseudo-code du cours.

3. C. Game interface
- Faire une interface Pygame qui montre la simulation de la solution,
  son cout, et les informations de recherche.

Reference projet :
- docs/Project 1 Part 1.pdf
- docs/SPEC.md (copie de la specification utilisee dans le repo)

---

## 2) Ou se trouvent ces parties dans le code

### A. Modeling the state
- sokoban.py
- Classe : SokobanPuzzle
- Fonctions importantes : __init__, isGoal, successorFunction

### A. Modeling the node
- node.py
- Classe : Node
- Champs : state, parent, action, g
- Fonctions : getPath, getSolution

### B. BFS
- search.py
- Fonction : BFS(s, successorsFn, isGoal)

### C. Game interface
- gui.py
- Classe : Game
- Lancement de BFS dans la GUI : methode resoudre
- Affichage/animation dans la boucle update + draw

### Point d'entree
- main.py
- python main.py (GUI)
- python main.py --console (test BFS en console)

---

## 3) Modelisation de l'etat (A.1) - logique detaillee

Fichier : sokoban.py

### 3.1 Comment un etat est represente
Un etat Sokoban est :
- une grille de caracteres,
- plus la position du joueur.

Symboles utilises dans la grille :
- R : joueur
- O : mur
- espace : case vide
- S : cible
- B : caisse
- . : joueur sur cible
- * : caisse sur cible

### 3.2 Pourquoi le code utilise tuple(grid)
La grille est stockee en tuple de chaines :
- c'est immuable,
- c'est hashable,
- donc on peut l'utiliser dans des sets pour BFS.

C'est important pour reconnaitre rapidement un etat deja vu.

### 3.3 Egalite et hash
- __eq__ compare les grilles.
- __hash__ calcule hash(self.grid).

Donc deux etats avec la meme grille sont consideres identiques, meme s'ils sont des objets Python differents.

---

## 4) successorFunction - explication tres simple

Fichier : sokoban.py

### 4.1 Role
successorFunction repond a la question :
"Depuis cet etat, quels coups sont legalement possibles ?"

La reponse est une liste de paires :
(action, nouvel_etat)

### 4.2 Ce que la fonction fait pour chaque direction
Le code essaie toujours : UP, DOWN, LEFT, RIGHT.

Pour chaque direction :
1. regarder la case devant le joueur (n1)
2. selon le contenu de n1 :
- si mur O : coup interdit
- si vide ou cible : deplacement simple
- si caisse B ou * :
  - regarder la case derriere la caisse (n2)
  - si n2 est libre (vide ou cible), pousser autorise
  - sinon pousser interdit

### 4.3 Ce que la fonction garantit
Cette fonction applique les regles officielles Sokoban :
- pas de passage dans les murs,
- pas de tirage de caisse,
- pas de poussee de deux caisses,
- une poussee seulement si la case derriere est libre.

### 4.4 Tres important
L'etat parent n'est jamais modifie.
Le code construit une nouvelle grille pour chaque successeur.

---

## 5) isGoal - explication claire

Fichier : sokoban.py

isGoal retourne vrai si la grille ne contient plus aucun B.

Pourquoi c'est correct :
- B = caisse pas encore sur cible,
- * = caisse deja sur cible.

Donc "plus de B" veut dire "toutes les caisses sont sur cibles".

---

## 6) Modelisation du noeud (A.2)

Fichier : node.py

Un Node contient exactement ce qui est demande :
- state : etat Sokoban
- parent : noeud parent
- action : action qui a cree ce noeud
- g : cout du chemin

Ici chaque pas coute 1, donc :
- g de la racine = 0
- sinon g = parent.g + 1

Fonctions :
- getPath : reconstruit la suite d'etats depuis l'initial
- getSolution : reconstruit la suite d'actions

---

## 7) BFS (partie B) - explication pas a pas

Fichier : search.py

### 7.1 Idee intuitive
BFS explore par couches :
- d'abord distance 0,
- puis distance 1,
- puis distance 2, etc.

Avec un cout de pas constant (=1), le premier but trouve est optimal.

### 7.2 Structures
- ouvert : file FIFO (deque)
- ferme : liste des noeuds deja developpes
- ouvertSet et fermeSet : optimisation de performance

### 7.3 Deroulement concret
1. creer la racine Node(etat_initial)
2. si racine est deja but -> retour immediat
3. mettre racine dans Open
4. tant que Open non vide :
- sortir le premier noeud
- le mettre dans Closed
- generer ses successeurs
- pour chaque successeur non deja vu :
  - si but : retour
  - sinon ajouter dans Open
5. si Open vide sans but : pas de solution

### 7.4 Difference entre cout et steps
Dans ce code, BFS renvoie : (noeud_but_ou_None, steps)

- cout g : longueur de la solution finale
- steps : nombre de noeuds developpes par BFS

steps mesure le travail de recherche, pas la longueur de la solution.

---

## 8) Interface de jeu (partie C)

Fichier : gui.py

### 8.1 Ce que fait l'interface
- menu de niveaux
- jeu manuel (fleches)
- bouton Resoudre (BFS)
- affichage du resultat BFS
- lecture automatique de la solution
- animations de victoire

### 8.2 Point architecture important
La GUI ne recode pas les regles de Sokoban.
Elle appelle successorFunction et applique seulement les coups legalement proposes.

Donc les regles restent centralisees dans sokoban.py.

### 8.3 Cycle principal
La classe Game tourne avec :
- handle_events
- update
- draw

Cette separation rend le code plus lisible :
- entree utilisateur,
- logique etat,
- affichage.

---

## 9) Verification de conformite a la consigne

Base de comparaison : docs/Project 1 Part 1.pdf (et docs/SPEC.md du repo).

### A. Modeling state
Exigences : symboles, mouvements, init/isGoal/successorFunction.
Etat : conforme.

### A. Modeling node
Exigences : state, parent, action, g, getPath, getSolution.
Etat : conforme.

### B. BFS
Exigences : BFS selon pseudo-code du cours.
Etat : conforme (avec optimisation sets qui ne change pas la logique).

### C. Interface Pygame
Exigences : simuler la solution et afficher les infos de recherche.
Etat : conforme.

Conclusion :
Le code respecte les points centraux demandes par la prof pour A, B, C.

---

## 10) Lecture conseillee si tu presentes a l'oral

Ordre simple :
1. main.py (point d'entree)
2. sokoban.py (regles)
3. node.py (structure de noeud)
4. search.py (BFS)
5. gui.py (integration visuelle)
6. test_core.py (preuves de bon fonctionnement)

Si tu bloques pendant l'oral, tu peux dire :
- "Les regles du jeu sont centralisees dans successorFunction." 
- "BFS travaille avec Open/Closed, evite les etats deja vus, et reconstruit la solution via parent."
- "isGoal est vrai quand il ne reste plus de B."

---

## 11) Commandes utiles

- Lancer le jeu :
  - python main.py

- Lancer BFS console :
  - python main.py --console

- Lancer les tests :
  - python test_core.py

---

## 12) Questions probables (ajoutées par adem, étape 27)

**Où sont les règles du jeu ?**
Uniquement dans `successorFunction()`. L'interface, la lecture automatique et le BFS l'utilisent tous les trois.

### Questions sur la classe `SokobanPuzzle`

**Comment les niveaux sont-ils générés ?**
Ils ne sont pas générés au hasard : ils sont écrits à la main dans `levels.py`, sous forme de grilles de texte (les 5 premiers sont recopiés de la Figure 4 de l'énoncé). `SokobanPuzzle(grille)` transforme une grille en état. Ce qui est « généré » par le programme, ce sont les états suivants : `successorFunction()` fabrique les enfants d'un état, et le BFS les assemble en arbre.

**À quoi sert `__init__` ?**
À créer un état : il range la grille dans `self.grid` (en tuple, donc non modifiable et hashable) et la position du joueur dans `self.player_pos`. Pour le niveau de départ, il cherche le joueur dans la grille (`trouver_joueur`). Pour un successeur, la position est donnée directement (on vient de déplacer le joueur, donc on la connaît : pas besoin de re-chercher).

**À quoi sert `isGoal()` ?**
À dire si l'état est un but : vrai quand il ne reste aucune caisse `B` hors cible. Le BFS l'appelle sur chaque nouvel enfant.

**Que renvoie `successorFunction()` ?**
Une liste de paires `(action, successeur)`, une par coup légal parmi UP, DOWN, LEFT, RIGHT. Un coup est légal si la case visée est libre, ou si elle contient une caisse et que la case derrière est libre. Chaque successeur est un nouveau `SokobanPuzzle` : l'état de départ n'est jamais modifié.

**Pourquoi `__eq__` et `__hash__` ?**
Le BFS doit savoir si un état a déjà été vu. Deux états sont les mêmes si leurs grilles sont identiques, et `__hash__` permet de les mettre dans un `set`.

### Questions sur la classe `Node`

**Que contient un nœud ?**
Exactement ce que demande l'énoncé : `state` (un `SokobanPuzzle`), `parent` (le nœud d'où l'on vient), `action` (le coup qui a mené ici) et `g` (le coût du chemin).

**Comment est calculé `g` ?**
`g = g du père + 1`, car chaque coup coûte 1. La racine a `g = 0`.

**Comment marchent `getPath()` et `getSolution()` ?**
Les deux remontent de nœud en nœud avec `parent` jusqu'à la racine, puis inversent la liste. `getPath()` collecte les états, `getSolution()` collecte les actions (la racine n'en a pas).

**Différence entre état et nœud ?**
L'état est la photo du jeu (la grille). Le nœud est un point de l'arbre de recherche : il enveloppe un état et se souvient de son père, de l'action et du coût. Deux nœuds différents peuvent contenir le même état.

**Rôle de chaque fichier ?**
`sokoban.py` = l'état et les règles. `node.py` = le nœud. `search.py` = le BFS. `levels.py` = les grilles. `gui.py` = l'interface Pygame, qui réutilise `successorFunction()`. `main.py` = le point d'entrée.

---

## 13) A* et comparaison avec le BFS (sujet partie 2)

**Ce qui a été ajouté.** `Node` a maintenant `f` et `setF(h)` (f = g + h). Le fichier `astar.py` contient `AStar` (pseudo-code du cours, Figure 1.29) et les trois heuristiques. `python main.py --compare` affiche le tableau BFS / A* h1 / h2 / h3.

**Différence avec le BFS.** Le BFS prend dans Open le noeud le moins profond (file FIFO). A* prend celui qui a le plus petit f = g + h (file de priorité, `heapq`). Il teste le but quand le noeud sort de Open (pas à la génération), et si un état déjà vu est retrouvé avec un meilleur f, il remplace l'ancien noeud.

**Heuristiques.**
- h1 = nombre de caisses pas encore sur une cible.
- h2 = 2 × h1 + somme, pour chaque caisse hors cible, de la distance de Manhattan à la cible libre la plus proche.
- h3 (proposée) = h2 + distance du joueur à la caisse hors cible la plus proche − 1.

**Pourquoi h3 (le raisonnement à dire à l'oral).**
1. *Ce qui manque à h2.* h2 ne regarde que les caisses : combien il en reste et à quelle distance de leur cible. Or ce n'est pas la caisse qui se déplace toute seule : c'est le joueur qui la pousse, et il doit d'abord marcher jusqu'à elle.
2. *Ce trajet coûte.* Dans notre modèle chaque déplacement coûte 1, qu'on pousse ou non. Donc le trajet du joueur fait partie du coût réel jusqu'au but, et h2 l'oublie : il donne la même valeur à deux états dont l'un a le joueur collé à une caisse et l'autre tout au fond de la salle, alors que le premier est clairement plus proche de la solution.
3. *Le cours dit la même chose.* Dans l'exemple du labyrinthe (A*, Figure 1.41), h est la distance de Manhattan entre l'agent et le but. Ici l'agent est le joueur, et son « but » immédiat est la caisse la plus proche.
4. *Pourquoi « − 1 ».* Pour pousser, le joueur se met à côté de la caisse, pas sur elle : s'il en est à 3 cases, il n'a que 2 pas à faire.
5. *Pourquoi on s'arrête là.* On ajoute une seule idée à h2, facile à calculer (une boucle sur les caisses) et facile à justifier. On n'a pas cherché les blocages (caisse dans un coin) : ce serait plus compliqué et pas demandé.
6. *Résultat.* Moins de steps que h2 sur tous les niveaux (voir le tableau), avec le même coût de solution.

**Complexité.** Dans le pire cas, A* comme le BFS est en O(b^d) en temps et en espace : on ne peut pas faire mieux sans connaître h. Mais la complexité réelle dépend de la qualité de h : plus h est proche du vrai coût restant, moins A* développe de noeuds (le facteur de branchement effectif diminue). Mesure (steps = noeuds développés) :

| Niveau | BFS | A* h1 | A* h2 | A* h3 |
|---|---|---|---|---|
| Exemple 2 | 1806 | 1827 | 1400 | 979 |
| Exemple 3 | 6013 | 5984 | 3126 | 2777 |
| Exemple 4 | 6051 | 5475 | 3023 | 2577 |
| Exemple 5 | 11659 | 10190 | 2980 | 2241 |

Lecture : h1 est trop faible (presque comme ne pas avoir d'heuristique : A* ≈ BFS, parfois même un peu pire à cause des égalités de f). h2 divise les steps par 2 à 4, h3 gagne encore 10 à 25 %. Les quatre algorithmes trouvent le même coût optimal sur les 8 niveaux. Le temps par noeud est plus grand pour A* (calcul de h, tas), donc sur les petits niveaux le BFS peut finir plus vite. L'optimalité de A* est garantie seulement si h est admissible (ne surestime jamais) ; h1 l'est, h2 et h3 pas forcément, mais ici les coûts sont optimaux.
