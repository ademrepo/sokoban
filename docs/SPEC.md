# SPEC — Sokoban (Problem Solving, M1 Visual Computing, USTHB)

Ce fichier est la source de vérité du projet. Copie **verbatim** des sections 1, 2 et 3 du message de cadrage. Ne jamais le contredire ; en cas de doute, demander avant de changer quoi que ce soit ici.

---

## 1. SPÉCIFICATION — TEXT OF THE PROJECT STATEMENT (verbatim, 100 % fidelity)

> Problem Solving
> Master 1, Visual Computing
> 2026/2027
>
> **Project 1 — Modeling and solving the Sokoban Puzzle**
>
> Sokoban (Pushbox) is a classic puzzle game, originating from Japan and dating back to the early 1980s. In this game, a warehouse keeper (the player) moves around a warehouse, represented by a grid of squares. These squares are of five types: PLAYER, WALL, EMPTY SPACE, BOX, TARGET SPACE (see Figure 1). The goal of the game is to place all the boxes on the target spaces.
>
> *Figure 1: Example (1) of a Sokoban board* (labels on the figure: CAISSE = box, MUR = wall, CASE CIBLE = target space, CASE VIDE = empty space, JOUEUR = player)
>
> The rules of the game are very simple:
> - The structure of the warehouse and the number of boxes vary from one level to another.
> - The warehouse in which the boxes must be placed rarely has the shape of a simple rectangle; it is more of a maze, more or less complicated. There are walls on all sides of this maze.
> - There can be one or more boxes, and there are always as many target spaces as there are boxes.
> - The game has only one player, who can move in the four cardinal directions.
> - The player is only allowed to move to an unoccupied space (one that is not a wall) or push a box and move onto the free space. They are not allowed to pull a box or move over it.
> - To push a box, the space adjacent to the box in the direction of the push must be free. The player cannot push two boxes at the same time.
> - The player wins when all the boxes are on the target spaces, in any order. There are no boxes assigned to specific target points.
>
> The objective of the project is first to model the game, then implement a solver based on various search algorithms, and finally create a GUI for this game.
>
> **A. Problem formulation:**
>
> The first step in this assignment is to propose a formulation for the Sokoban game, and implement it in Python.
>
> **1. Modeling the state:**
>
> To model a state, the following instructions must be followed:
> - The game is presented in the form of a two-dimensional grid. We need to be able to represent the following elements: walls, empty spaces, and target spaces, which are static elements, as well as the player and the boxes, which are dynamic elements. In this grid, we can have squares with the following configurations (see Figure 2):
>
> *Figure 2: Configuration of a Sokoban board*
> - Player (Robot): represented by 'R'
> - Wall (Obstacle): represented by 'O'
> - Empty space: represented by ' '
> - Target space (Storage): represented by 'S'
> - Box (Block): represented by 'B'
> - Player on a target space: '.'
> - Box on a target space: '*'
>
> - To move from one state to another, the player must move within the grid. Four movements are allowed:
>   - UP: (-1, 0)
>   - DOWN: (1, 0)
>   - LEFT: (0, -1)
>   - RIGHT: (0, 1)
> - For a move to be valid, it must follow the game's rules (see the game description). The goal state is reached when all the boxes are on the target spaces.
>
> To model a state in the Sokoban game, we define the class SokobanPuzzle with the following functions:
> - init(): This function creates a state.
> - isGoal(): This function checks if a state is a goal.
> - successorFunction(): This function generates pairs of (action, successor) representing all possible moves that can be applied on the board.
>
> **2. Modeling the node:**
>
> The Node class should include the following components:
> - state: An instance of the SokobanPuzzle class representing the state;
> - parent: A reference to the parent node;
> - action: The action applied to generate the current node from the parent node;
> - g: The path cost, where the step cost c is always equal to 1;
>
> In the Node class, you should also provide definitions for the following functions:
> - getPath(): This function returns a list or sequence of states representing the path from the initial state to the goal state of the solution;
> - getSolution(): This function returns a list or sequence of actions applied to the initial state to reach the goal state;
>
> **B. Searching for a solution:**
>
> The next step in this assignment is to solve the Sokoban puzzle using the Breadth-First Search (BFS) algorithm. Utilize the provided pseudocode from the course to create an implementation of the BFS algorithm.
>
> **C. Game interface:**
>
> Create an interface in Pygame that displays a simulation of the solution found, its cost, and the number of steps taken by the different search algorithms.
>
> This interface will provide a visual representation of the solution process, allowing users to see the simulation of how the puzzle is solved, along with other relevant information.
>
> *Figure 4: Test examples* — five boards: Exemple 1, Exemple 2, Exemple 3, Exemple 4, Exemple 5 (images on page 4 of the statement; note that the statement has no "Figure 3").

### Student's interpretation decisions (these override any ambiguity above)
- Only **BFS** is implemented (the statement only requires it in part B).
- "Number of steps taken by the search algorithm" in the interface = **`steps`, the number of nodes expanded by the BFS** (one per iteration of the loop on Open; 0 if the initial state is already a goal). It measures the work of the search (time complexity). Display "Coût" (cost g = length of the solution), "steps" and the computation time.
  *(Modifié le 2026-10-20 avec l'accord d'ademrepo, d'après les notes du cours : la prof fait renvoyer au BFS le nœud but **et** `steps`. L'ancienne interprétation, « nombre de pas = longueur de la solution », affichait deux fois le même nombre que le coût. Voir docs/logs/2026-10-20_session-30.md.)*
- Levels = the 5 test examples of Figure 4 + the boards of Figure 1 and Figure 2 if convenient + 2 or 3 extra small levels of your own.
- Method names must be exactly the ones of the statement: `isGoal`, `successorFunction`, `getPath`, `getSolution`. `init()` of the statement is implemented as Python's `__init__` (say so in a French comment).

---

## 2. SPÉCIFICATION — COURSE EXTRACTS TO FOLLOW (verbatim)

### 2.1 Problem formulation (course §1.2.1)
> A problem can be defined formally by the following four components:
> - **Initial state:** the state that the agent starts in.
> - **Successor function:** the function that changes the state of the agent. Given a particular state s, successorsFn(s) returns a set of (action, successor) ordered pairs, where each action is one of the legal actions in state s and each successor is a state that can be reached from s by applying the action.
> - **Goal test:** which determines whether a given state is a goal state. […] Sometimes the goal is specified by a property rather than a set of one or more states.
> - **Path cost:** It's the function that assigns a numeric cost to each path. […] The step cost of taking action a to go from state s1 to state s2 is denoted by c(s1, a, s2).
>
> A solution to a problem is a sequence of actions from the initial state to a goal state. Solution quality is measured by the path cost function, and an optimal solution has the lowest path cost among all solutions.

### 2.2 Node (course §1.3)
> The building block of a search tree is the node. […] a node is a data structure with five components:
> - State: the state in the state space to which the node corresponds;
> - Parent-node: the node in the search tree that generated this node;
> - Action: the action that was applied to the parent to generate the node;
> - Path-cost: the cost, usually denoted by g, of the path from the initial node;
> - Depth: the number of steps along the path from the initial state.

(The project statement keeps only `state`, `parent`, `action`, `g`. Implement exactly those four. Since every step costs 1, depth = g; add a French comment saying so.)

### 2.3 General graph search (course Figure 1.17)
```
Input: The problem to be solved
Output: A solution or failure
Function GraphSearch (problem)
Begin
  Initialize the Open list using the initial state of problem
  Initialize the Closed list to be empty
  While the Open list is not empty do
    Choose a leaf node and remove it from the Open list
    If the chosen node contains a goal state, then return the corresponding solution
    Add the chosen node to the Closed list
    Expand the chosen node
    Add the resulting nodes to the Open list only if they are not already in the Open or Closed lists
  Return failure
End
```

### 2.4 BFS (course §1.3.3.1 and Figure 1.19) — THE ALGORITHM TO IMPLEMENT
> This algorithm starts at the root node of the tree and visits all nodes at the current depth level before moving on to the nodes at the next depth level. The BFS algorithm uses a first-in-first-out (FIFO) list, known as a queue, for its Open list. This queue puts all newly generated successors at the end of the queue, ensuring that shallow nodes are expanded first.

```
Input:
- s: The initial state
- successorsFn: The function that generates the successor pairs (action, successor) for a given state
- isGoal: The function that checks if a state is a goal or not

Output: Goal node or None

Function BFS (s, successorsFn, isGoal)
Begin
  Open: queue /* FIFO list */
  Closed: list

  init_node <- Node (s, None, None) /* A data structure with (state, parentNode, action) attributes*/
  if (isGoal(init_node.state)) then return init_node
  Open.enqueue(init_node)
  Closed <- [ ]

  while (not Open.empty()) do
    current <- Open.dequeue() /* Choose the shallowest node in Open */
    Closed.add(current)

    for each (action, successor) in successorsFn(current.state) do
      child <- Node (successor, current, action) /* Create a new node and link it to its parent */
      if (child.state not in Closed and not in Open) then
        if (isGoal(child.state)) then return child
        Open.enqueue(child)

  return None
End
```

Properties given by the course (put them in a French comment at the top of `search.py`): complete if a solution exists (shallowest goal at finite depth d); optimal if all actions have the same cost; time complexity O(b^d); space complexity O(b^d) (maximum size of the Open queue is b^d).

---

## 3. CONTRAT TECHNIQUE (decisions already taken — do not change)

### 3.1 File structure
```
CLAUDE.md                  (rules + logging workflow, already at the repo root)
docs/                      the 2 PDFs (do not modify), SPEC.md, PLAN.md, logs/, EXPLICATIONS.md (last step)
assets/                    itch.io pack "Pixel Art Top Down - Basic v1.2.3" (do not modify)
sokoban.py                 class SokobanPuzzle
node.py                    class Node
search.py                  function BFS
levels.py                  the levels (list of strings) + names
gui.py                     Pygame interface (Steps 6 to 9)
assets_loader.py           loading/cutting of sprites (Step 6)
main.py                    entry point:  python main.py
test_core.py               console tests with plain `assert` (no pytest needed)
```

### 3.2 State representation
- The grid is stored as a **tuple of strings** (one string per row), using exactly the 7 symbols of the statement: `R`, `O`, `' '`, `S`, `B`, `.`, `*`. A tuple of strings is hashable and comparable, so it can be tested with `in` and used in a `set`.
- `SokobanPuzzle.__init__(self, grid)` accepts a list/tuple of strings and stores a tuple of strings. Also store the player position (row, col) found at creation to avoid rescanning (and keep it consistent in successors).
- Implement `__eq__` (compare grids) and `__hash__` (hash of the grid) with short French comments explaining why (BFS needs "child.state not in Closed and not in Open").
- Add `__str__` returning the grid as text (useful for debugging/console).

### 3.3 Actions
```
UP    = (-1, 0)
DOWN  = ( 1, 0)
LEFT  = ( 0,-1)
RIGHT = ( 0, 1)
```
Actions are the strings `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"` with a dictionary mapping each to its delta. Successors are generated in this order: UP, DOWN, LEFT, RIGHT (so results are deterministic and reproducible).

### 3.4 Rules to implement in `successorFunction()` (translation of the statement's rules)
Let the player be at (r, c), direction delta (dr, dc), next cell n1 = (r+dr, c+dc), cell after n1 = n2 = (r+2dr, c+2dc).
- If n1 is a wall `O` → the move is illegal.
- If n1 is `' '` or `S` (free) → the player simply moves.
- If n1 is `B` or `*` (a box) → the player pushes it, only if n2 is `' '` or `S`. If n2 is a wall, a box (`B` or `*`) → illegal (cannot push two boxes, cannot push into a wall). There is no pulling.
- The player never moves onto a box without pushing it.
- Cell updates when the player leaves a cell: `R` → `' '`, `.` → `S`. When the player enters n1: `' '` → `R`, `S` → `.`; if n1 was a box: `B` → `R` and `*` → `.`. When a box lands on n2: `' '` → `B`, `S` → `*`.
- Every move (push or not) costs 1.
- `successorFunction()` returns a **list of `(action, successor)` pairs** where `successor` is a **new** `SokobanPuzzle` (never mutate the current state).
- `isGoal()`: true when there is **no `B` left in the grid** (all boxes are `*`; there are as many targets as boxes so this is equivalent to "all boxes on targets"). Explain this equivalence in a French comment. Do not assign boxes to specific targets.

### 3.5 Node
```
Node(state, parent=None, action=None)
  state, parent, action
  g = 0 if parent is None else parent.g + 1       (step cost = 1)
  getPath()     -> list of states from the initial state to this node (walk parent links, then reverse)
  getSolution() -> list of actions from the initial state to this node (same, skipping the root's None action)
```
Keep it as simple as possible (loop with `while node is not None`).

### 3.6 BFS signature
`BFS(s, successorsFn, isGoal)` — exactly the course signature and structure (Open = `collections.deque`, Closed = list). Return **two values: `(goal node or None, steps)`**, where `steps` is incremented at each iteration of the loop on Open (as in the course notes; modifié le 2026-10-20, voir §1).
Called as: `BFS(initialPuzzle, lambda st: st.successorFunction(), lambda st: st.isGoal())` — or with small named helper functions instead of lambdas if that reads more simply.
Membership tests `child.state not in Closed and not in Open` are O(n) on lists/deques and will be slow on bigger levels. Keep the course structure (Open queue + Closed list) AND add two **sets of states** (`openSet`, `closedSet`) used only for the membership tests, with a French comment explaining that it is only a speed optimization and does not change the algorithm. Keep both sets in sync with the queue/list.

### 3.7 Levels (`levels.py`)
- Format: `LEVELS = [ {"name": "Exemple 1", "grid": [ "OOOOOO", "O S BO", ... ]}, ... ]` — plain list of dicts, rows are strings, every row padded with spaces to the same width, symbols exactly the 7 of the statement.
- **Transcribe the boards from the PDF yourself**: look at the figures with Read (statement page 1 = Figure 1, page 2 = Figure 2, page 4 = Examples 1 to 5). Pay attention to walls in irregular shapes (outside the maze, fill with `O` or a space — choose one convention, say `' '` outside is NOT allowed because the BFS/GUI treat it as free: use `O` for everything outside/around the maze so that the player can never leave the grid).
- After transcribing, **print each level as ASCII in the chat** and ask me to confirm visually against the figures before continuing. Also verify with an assertion that every level has exactly one player (`R` or `.`) and that the number of boxes (`B` + `*`) equals the number of targets (`S` + `*` + `.`-under-player + ...) — precisely: count of boxes = count of cells that are targets (`S`, `*`, `.`).
- Add 2 or 3 extra small, easy-to-medium levels designed by you, each verified solvable with the BFS (record the optimal number of moves in a French comment).

### 3.8 Python style recap
Simple functions/classes, camelCase for the statement's method names (`isGoal`, `successorFunction`, `getPath`, `getSolution`), snake_case for everything else, French comments, no type hints, no f-string gymnastics.

## 7. Partie 2 : A* (ajouté le 2026-10-24, demandé par l'utilisateur d'après `Project 1 Part 2.pdf`)
Le sujet de la partie 2 ajoute à l'énoncé de la partie 1 (les §1 à 6 ci-dessus restent vrais, sauf l'interdiction d'autre algorithme que BFS et d'heuristique, levée pour cette partie) :
- `Node` : attribut `f` et méthode `setF(h)` (f = g + h(état)). Le BFS n'utilise pas f.
- `astar.py` : `AStar(s, successorsFn, isGoal, h)` selon la Figure 1.29 du cours (Open = file de priorité ordonnée par f via `heapq`, Closed = dictionnaire ; remplacement dans Open / retrait de Closed quand un meilleur f est trouvé ; test du but à la sortie de Open). Retourne `(noeud but ou None, steps)`, `steps` = noeuds développés, comme le BFS.
- Heuristiques (dans `astar.py`) : `h1` = nombre de caisses hors cible ; `h2` = 2*h1 + somme des distances de Manhattan caisse → cible libre la plus proche ; `h3` (proposée) = h2 + distance de Manhattan joueur → caisse hors cible la plus proche − 1 (le joueur doit aller jusqu'à la caisse, et chaque déplacement coûte 1 ; même idée que « distance de l'agent au but » dans l'exemple du labyrinthe du cours). Sans détection de deadlock.
- Test : comparer BFS, A* h1, h2, h3 sur les niveaux (`python main.py --compare`).
- Interface (étape 30, faite) : boutons BFS / A* h1 / h2 / h3 (touches B, 1, 2, 3) qui lancent l'algorithme et jouent la solution ; bouton « Comparer » (touche C) qui affiche coût, steps et temps des 4 algorithmes.
