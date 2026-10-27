# How the whole program works (to explain it to the teacher)

Written in English so you can really understand it first. Identifiers (`successorFunction`, `etat`, `bouger`...) are the real names in the code, so you can say them as they are. Every example below was produced by running the real code on **Exemple 1**.

---

## 0. The 30-second version (say this first)

> "A Sokoban position is an object called a **state** (`SokobanPuzzle`): a grid of characters plus the player's position. The rules of the game live in **one** place, `successorFunction()`, which gives all the states you can reach in one move. A **node** (`Node`) wraps a state in the search tree (parent, action, cost g, and f for A*). The **search algorithms** (BFS, and A* with three heuristics) only need three things: the initial state, `successorFunction` and `isGoal`. They return the goal node, and walking back through the parents gives the list of moves. The **Pygame interface** reads the keyboard and the mouse, and for every move it calls the same `successorFunction`, so the game and the solver can never disagree on the rules."

---

## 1. The big picture

### 1.1 The files

| File | Role | One sentence |
|---|---|---|
| `levels.py` | data | The 8 levels, written as lists of strings. |
| `sokoban.py` | **the model** | Class `SokobanPuzzle`: a state + all the rules. |
| `node.py` | the model | Class `Node`: a node of the search tree. |
| `search.py` | algorithm | `BFS` (blind search). |
| `astar.py` | algorithm | `AStar` + the heuristics `h1`, `h2`, `h3`. |
| `main.py` | entry point | Starts the game, or the console modes. |
| `gui.py` | interface | Class `Game`: Pygame window, input, drawing. |
| `assets_loader.py` | interface | Cuts the sprites out of the image pack, makes the sounds. |
| `test_core.py` | tests | Plain `assert`s. |

### 1.2 The pipeline (from the click to the answer)

```
 KEYBOARD / MOUSE
        │  pygame.event.get()
        ▼
 gui.py  handle_events()           "which key? which button?"
        │
        ├── arrow key ──► bouger(action)          one move by hand
        │                    │
        │                    └─► etat.successorFunction()   ◄── THE RULES (sokoban.py)
        │                          picks the successor whose action == the key
        │                          self.etat = that successor
        │
        └── button BFS / A* h1 / h2 / h3 (or keys B,1,2,3)
                 │
                 ▼
            resoudre(k) ─► lancer(k) ─► BFS(...)  or  AStar(..., h)    (search.py / astar.py)
                                            │  uses successorFunction + isGoal
                                            ▼
                                  goal Node  (+ steps)
                                            │
                      noeud.getSolution() = ["RIGHT","UP","LEFT","LEFT"]
                      noeud.getPath()     = the list of states (to draw the trajectory)
                                            │
                                            ▼
                 self.solution = list of actions, self.auto = True
                                            │
          every 260 ms, update() calls bouger(self.solution[i])   ← same function as the keyboard
                                            ▼
 gui.py  update()  → isGoal()? → "ouverture" → "marche" → "queue" → "bravo"
 gui.py  draw()    → reads self.etat.grid and paints sprites, 60 times per second
```

Key idea to remember: **there is only one road to change the game state, `bouger` → `successorFunction`**. A human pressing keys and the solver replaying its solution use exactly the same road.

---

## 2. The data: grids and levels (`levels.py`)

A level is a list of strings, one string per row:

```python
{"name": "Exemple 1",
 "grid": ["OOOOOO",
          "OS B O",
          "O OR O",
          "O    O",
          "O    O",
          "OOOOOO"]}
```

The 7 symbols are exactly the ones of the statement:

| Symbol | Meaning |
|---|---|
| `R` | player |
| `O` | wall |
| ` ` (space) | empty floor |
| `S` | target |
| `B` | box **not** on a target |
| `.` | player standing on a target |
| `*` | box on a target |

Reading Exemple 1: the player `R` is at (row 2, column 3); the box `B` is at (1, 3); the target `S` is at (1, 1). Positions are always `(row, column)`, counted from 0 at the top left.

The 5 first levels are copied from Figure 4 of the statement, the 3 last ("Maison 1, 2, 3") are small levels we made.

---

## 3. The state and the rules (`sokoban.py`), line by line

### 3.1 `ACTIONS`

```python
ACTIONS = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
```
The four moves of the statement, each with its `(delta row, delta column)`. `UP` = one row less, `RIGHT` = one column more.

### 3.2 `__init__(self, grid, player_pos=None)` (the statement's `init()`)

```python
self.grid = tuple(grid)
if player_pos is None:
    player_pos = self.trouver_joueur()
self.player_pos = player_pos
```
- `tuple(grid)`: we turn the list of strings into a **tuple**. A tuple cannot be modified, and that matters: a state must never change after it is created (otherwise a successor could corrupt its parent). A tuple of strings is also **hashable**, which BFS needs (see `__hash__`).
- `player_pos`: for the first state we do not know where the player is, so `trouver_joueur()` scans the grid once. For a successor we already know (we just moved the player), so it is passed in and **no scan is needed** — that is a speed rule we applied.

### 3.3 `trouver_joueur()`

Two nested loops over rows `r` and columns `c`; returns `(r, c)` for the first cell that is `"R"` or `"."` (the player, standing on floor or on a target).

### 3.4 `__eq__` and `__hash__`

- `__eq__`: two states are equal if their grids are identical. (The player's position is already inside the grid, so no need to compare it.)
- `__hash__`: `hash(self.grid)`. It lets us put states in a Python `set`. **Why it matters:** BFS and A* must ask "have I already seen this state?" thousands of times; with a set the answer is instant.

### 3.5 `isGoal()`

```python
for ligne in self.grid:
    if "B" in ligne:
        return False
return True
```
Goal = no `B` left. Reason: there are always as many targets as boxes, and a box that is on a target is written `*`, not `B`. So "no `B`" means "every box is on a target". (Any box on any target — the statement says the order does not matter.)

### 3.6 `successorFunction()` — THE RULES

It returns a list of `(action, successor_state)` pairs, trying `UP, DOWN, LEFT, RIGHT` in this fixed order (so results are always the same).

For each direction:
1. `n1` = the cell the player wants to enter = player position + delta.
2. Look at the character in `n1`:
   - **`" "` or `"S"`** (free floor or empty target): the player just walks. We build the new grid with `nouvelle_grille(..., pousse=False)` and add the pair.
   - **`"B"` or `"*"`** (a box): the player pushes. This is allowed **only if** the cell behind the box (`n2` = player + 2×delta) is `" "` or `"S"`. Not a wall, **not another box** (so two boxes can never be pushed together). If allowed → `nouvelle_grille(..., pousse=True)`.
   - **Anything else (`"O"`, a wall)**: nothing is added. The move simply does not exist.

So "a legal move" is *by definition* "a pair returned by this function". No other file contains a rule.

### 3.7 `nouvelle_grille(r, c, dr, dc, pousse)`

Builds the next grid **without touching the current one** (it works on a copy `lignes`, a list of lists of characters):
1. The cell the player leaves: becomes `" "`, or `"S"` if the player was standing on a target (`"."`).
2. The cell the player enters: becomes `"."` if it is a target (`"S"` or a `"*"` whose box was just pushed away), otherwise `"R"`.
3. If a box is pushed, the cell behind receives it: `"*"` if that cell is a target, otherwise `"B"`.
4. Re-join each row into a string.

### 3.8 Worked example (real output)

Exemple 1, player at `(2, 3)`:

```
OOOOOO
OS B O
O OR O      <- R at (2,3)
O    O
O    O
OOOOOO
```
`successorFunction()` returns **2** pairs:
- `UP`? The cell above is the box `B` at (1,3). Behind it is (0,3) = wall `O` → push forbidden → **no pair**.
- `DOWN` → (3,3) is free → pair `("DOWN", state)` with player at (3,3).
- `LEFT` → (2,2) is the wall `O` → **no pair**.
- `RIGHT` → (2,4) is free → pair `("RIGHT", state)` with player at (2,4).

---

## 4. The node (`node.py`)

```python
class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        if parent is None: self.g = 0
        else:              self.g = parent.g + 1
        self.f = 0
```
- `state`: the `SokobanPuzzle`. `parent`: the node it came from. `action`: the move that led here.
- `g`: cost of the path from the start. Every move costs 1, so `g = parent.g + 1` and the root has `g = 0`.
- `f`: the A* evaluation, filled by `setF`. BFS ignores it.

**`setF(h)`**: `self.f = self.g + h(self.state)`. *f = what I already paid + what I think is left.*

**`getPath()`**: starts at the node, follows `parent` up to the root while appending states, then `reverse()` so the order is start → goal.

**`getSolution()`**: same walk, but collects `action` (the root has none, so we stop when `parent is None`), then reverse.

**State vs node** (a classic question): the state is the picture of the game (the grid). The node is a point of the search tree: it wraps a state and remembers *how we got there*. Two different nodes can hold the same state (reached by two different paths).

---

## 5. BFS (`search.py`), line by line

BFS = Breadth-First Search, Figure 1.19 of the course. It explores all states at depth 1, then all at depth 2, and so on, so the first goal it finds has the fewest moves.

```python
def BFS(s, successorsFn, isGoal):
```
It receives the **initial state**, the **function that gives successors** and the **goal test**. It does not know anything about Sokoban: that is why the same code could solve another problem.

```python
racine = Node(s, None, None)
if isGoal(racine.state):
    return racine, 0
```
Create the root. If we already start on a goal, done (0 nodes developed).

```python
ouvert = deque(); ouvert.append(racine)     # Open  : FIFO queue
ferme = []                                  # Closed: nodes already developed
ouvertSet = set(); fermeSet = set()         # same states, only to test membership fast
```
- **Open** = nodes discovered but not yet developed. A `deque` used as a queue: we remove on the left, add on the right (first in, first out). This FIFO order *is* what makes the search "breadth first".
- **Closed** = already developed nodes.
- The two **sets** hold the same states as Open/Closed. Testing `x in set` is instant, `x in list` is slow. It is a speed trick only; the algorithm is the one of the course.

```python
steps = 0
while len(ouvert) > 0:
    steps = steps + 1
    courant = ouvert.popleft()          # the shallowest node
    ouvertSet.remove(courant.state); ferme.append(courant); fermeSet.add(courant.state)
```
Each turn of the loop = **one node developed** = one "step". `steps` is what we use to measure the work (time complexity).

```python
    for action, successeur in successorsFn(courant.state):
        enfant = Node(successeur, courant, action)
        if enfant.state not in fermeSet and enfant.state not in ouvertSet:
            if isGoal(enfant.state):
                return enfant, steps
            ouvert.append(enfant); ouvertSet.add(enfant.state)
return None, steps
```
For each successor: build the child node (parent = `courant`). If its state was never seen, test the goal **now** (BFS tests at generation, as in the course) and return it; otherwise put it at the end of Open. If Open becomes empty, there is no solution → `None`.

### Worked example: Exemple 1

- Start: player (2,3). Root expanded (step 1) → two children: `DOWN` and `RIGHT`.
- Then each of those is expanded, etc. The goal appears at depth 4, after **11 steps**.
- The solution found: **`RIGHT, UP, LEFT, LEFT`**, cost 4. The states along the path:

```
start          RIGHT          UP             LEFT           LEFT  (goal)
OOOOOO         OOOOOO         OOOOOO         OOOOOO         OOOOOO
OS B O         OS B O         OS BRO         OSBR O         O*R  O
O OR O         O O RO         O O  O         O O  O         O O  O
O    O         O    O         O    O         O    O         O    O
```
The player goes round the box (RIGHT, UP), then pushes it twice to the left (LEFT, LEFT). The box ends on the target and is shown `*`.

### Properties (from the course)
- **Complete**: finds a solution if one exists.
- **Optimal** here: all moves cost 1, so the shallowest goal is the cheapest.
- **Time and space O(b^d)** with `b` = branching factor (here at most 4) and `d` = depth of the solution. It becomes huge when `d` grows — that is why A* exists.

---

## 6. A* (`astar.py`), line by line

A* = BFS with a **brain**. Instead of "the shallowest node first", it takes "the node with the smallest **f = g + h**": what it already cost (`g`) plus an estimate of what remains (`h`, the heuristic).

### 6.1 Helpers
- `positions(etat, symboles)`: returns the list of `(row, col)` of all cells whose character is in `symboles`. Example: `positions(etat, "B")` = where the boxes are.
- `distance_manhattan(a, b)` = `|ra − rb| + |ca − cb|` (equation 2 of the statement).

### 6.2 The three heuristics

A heuristic answers: *"looking at this state, roughly how many more moves until the goal?"*

| | Formula | Idea |
|---|---|---|
| **h1** | number of boxes not on a target (`B`) | each remaining box needs at least one push |
| **h2** | `2 × h1 + Σ (Manhattan distance from each box to its nearest free target)` | also counts **how far** each box is |
| **h3** (ours) | `h2 + (distance player → nearest box) − 1` | also counts **the player's walk** |

"Free target" = `S` or `.` (a target without a box on it).

**Why h3** (the reasoning to give):
1. h2 only looks at the boxes. But the player is the one who pushes, and he has to walk to a box first.
2. Every move costs 1, pushing or not, so that walk is a real part of the cost. h2 forgets it: it gives the same value whether the player is next to a box or at the other end of the room.
3. The course does the same in its maze example (Figure 1.41): `h` = Manhattan distance from the **agent** to the goal. Here the agent is the player and his first goal is the nearest box.
4. "−1" because he must stand **next to** the box to push it, not on it.
5. One simple idea, easy to compute, no deadlock detection (not asked).

**Numbers on Exemple 1 root** (player (2,3), box (1,3), target (1,1)): `h1 = 1`; `h2 = 2×1 + 2 = 4`; `h3 = 4 + (1 − 1) = 4`. After `DOWN` (player (3,3)) the player is 2 away from the box, so `h3 = 4 + (2−1) = 5` and `f = g + h3 = 1 + 5 = 6`.

### 6.3 `AStar(s, successorsFn, isGoal, h)` (Figure 1.29)

```python
racine = Node(s, None, None); racine.setF(h)
ouvert = []                      # a heap (heapq): smallest f comes out first
heapq.heappush(ouvert, (racine.f, numero, racine))
ouvertDict = {racine.state: racine}    # which node of each state is currently in Open
ferme = {}                             # Closed: state -> node
```
- **Open is a priority queue** (`heapq`). Each element is `(f, numero, node)`; the `numero` only breaks ties (first in, first out) and avoids comparing two nodes.
- `ouvertDict` and `ferme` are dictionaries so "is this state in Open/Closed, and with which f?" is instant.

```python
while len(ouvert) > 0:
    f, n, courant = heapq.heappop(ouvert)         # smallest f
    if ouvertDict.get(courant.state) is not courant: continue    # an old, replaced node: ignore
    del ouvertDict[courant.state]
    if isGoal(courant.state): return courant, steps              # goal tested when it COMES OUT of Open
    steps = steps + 1
    ferme[courant.state] = courant
```
Difference with BFS: the goal is tested **when the node is removed** from Open (Figure 1.29), because only then are we sure it has the best f.

```python
    for action, successeur in successorsFn(courant.state):
        enfant = Node(successeur, courant, action); enfant.setF(h)
        if state in neither Open nor Closed:           → insert in Open
        elif state in Open  and enfant.f is smaller:   → replace the Open node by the child
        else (state in Closed) and enfant.f smaller:   → remove it from Closed, insert the child in Open
```
These three cases are exactly the three `if / else if / else if` of the course pseudocode: *never seen → add; seen but we found a cheaper way → replace; otherwise ignore.*

(Implementation detail you may be asked: a heap cannot delete an element in the middle, so a replaced node stays in the heap but is no longer in `ouvertDict`; when it comes out we recognise it and skip it. Same result as "replace".)

### 6.4 Results we measured (steps = nodes developed, same optimal cost everywhere)

| Level | BFS | A* h1 | A* h2 | A* h3 |
|---|---|---|---|---|
| Exemple 2 | 1806 | 1827 | 1400 | 979 |
| Exemple 3 | 6013 | 5984 | 3126 | 2777 |
| Exemple 4 | 6051 | 5475 | 3023 | 2577 |
| Exemple 5 | 11659 | 10190 | 2980 | 2241 |

How to read it: h1 is too weak (≈ BFS); h2 divides the work by 2 to 4; h3 saves another 10–25 %. **Complexity**: in the worst case A* is still O(b^d) like BFS, but a good heuristic lowers the *effective* branching factor, so the real work is much smaller. A* costs more per node (computing h, the heap), so on tiny levels BFS can be as fast. A* is guaranteed optimal only if h is admissible (never overestimates); h1 is, h2 and h3 are not guaranteed, but they found the optimal cost on all our levels.

---

## 7. `main.py`

- `python main.py` → `Game(numero, menu).run()` → the window opens on the level menu.
- `python main.py --niveau 3` → opens directly level 3 (checks the number is valid).
- `python main.py --console` → for each level: builds `SokobanPuzzle(grid)`, runs `BFS`, prints solution, cost, steps, time.
- `python main.py --compare` → table BFS / A* h1 / h2 / h3 for every level (cost, steps, time).

`main()` just reads `sys.argv` and dispatches; the helper functions only time the algorithms with `time.time()`.

---

## 8. The interface (`gui.py`), from the keyboard to the screen

### 8.1 Start-up: `Game.__init__`
1. `pygame.init()`, window size computed from the biggest level (+ a margin for the scenery + the info bar at the bottom).
2. `load_sprites(TAILLE)` cuts the images (cat, box, walls, trees...) out of the pack; `load_sounds()` generates the sounds with code.
3. Creates the rectangles of all buttons (`boutons_algos` ×4, `bouton_comparer`, `bouton_annuler`, `bouton_recommencer`, `bouton_menu`).
4. `charger_niveau(numero)` then maybe `ouvrir_menu()`.

### 8.2 `charger_niveau(numero)`
```python
self.etat = SokobanPuzzle(self.niveau["grid"])     # the current state = a SokobanPuzzle
self.coups = 0; self.historique = []                # move counter, undo stack
self.phase = "jeu"
```
`self.etat` is **the** current state. Everything on screen is drawn from it.

### 8.3 The main loop `run()`
```python
while self.en_cours:
    self.handle_events()     # 1. read the keyboard / mouse
    self.update()            # 2. advance the logic and the animations
    self.draw()              # 3. paint the frame
    self.horloge.tick(60)    # 60 frames per second
```
This is the heart of every game: read → update → draw, 60 times per second.

### 8.4 `handle_events()` — collecting the information
`pygame.event.get()` returns everything that happened since the last frame (key pressed, mouse clicked, window closed).
- Arrow key → `TOUCHES[key]` maps `pygame.K_RIGHT` to `"RIGHT"` → `bouger("RIGHT")` (or stored in `action_en_attente` if the cat is still sliding).
- `B`, `1`, `2`, `3`, or a click on a button of `boutons_algos` → `resoudre(k)`.
- `C` or the "Comparer" button → `comparer()`.
- `Z` / "Annuler" → `annuler_coup()`; `R` → reload the level; `M` → menu; `S` → sound; `Esc` → quit.
- Mouse: `bouton.collidepoint(evenement.pos)` tells if the click was inside a button's rectangle.

### 8.5 `bouger(action)` — where the interface meets the rules

```python
dr, dc = ACTIONS[action]
ancien = self.etat
for nom, suivant in ancien.successorFunction():
    if nom == action:
        self.historique.append(ancien)     # for undo
        self.etat = suivant                # THE state changes here
        self.coups = self.coups + 1
        ... (animation info, dust particles, sound)
        return
# no pair matched: the move is illegal -> the cat does a small "bump", the state does not change
```
Nothing about walls or boxes is re-implemented: we ask `successorFunction`, and if it has no pair for this key the move is refused.

**Example: you press → in Exemple 1.** `handle_events` sees `K_RIGHT` → `bouger("RIGHT")` → `successorFunction()` returns the `DOWN` and `RIGHT` pairs → the `RIGHT` pair matches → `self.etat` becomes the state with the player at (2,4), `coups = 1`. Pressing `LEFT` instead: no `LEFT` pair (wall) → the cat bumps, `coups` stays 0.

### 8.6 `resoudre(k)` / `lancer(k)` — calling the solver

```python
ALGOS = [("BFS", None), ("A* h1", h1), ("A* h2", h2), ("A* h3", h3)]
```
`lancer(k)`: takes the name and heuristic `ALGOS[k]`; starts a timer; calls `BFS(self.etat, lambda s: s.successorFunction(), lambda s: s.isGoal())` or `AStar(..., h)`; returns `(node, steps, duration)`. **The search starts from the current position** (`self.etat`), not always from the beginning, so you can move a few steps and then ask for the solution.

`resoudre(k)` then:
```python
self.solution   = noeud.getSolution()                          # ["RIGHT","UP","LEFT","LEFT"]
self.trajectoire = [e.player_pos for e in noeud.getPath()]     # cells to draw the blue path
self.auto = True
self.resultat = "A* h3 : cout 4 | 5 steps | 0.000 s"           # text shown in the bar
```
`comparer()` does the same for the 4 algorithms in a loop and builds one text line per algorithm for the table panel.

### 8.7 `update()` — playing the solution and detecting victory
- If `self.auto` is true and `DELAI_PAS` (260 ms) passed: `bouger(self.solution[self.pas_auto])`, then `pas_auto += 1`. **The solution is replayed through the same `bouger`** as the keyboard.
- If the cat is not moving and `self.etat.isGoal()`: victory → phases `ouverture` (door opens) → `marche` (cat walks to the door) → `queue` → `bravo` (sign with the buttons Rejouer / Niveau suivant / Menu).
- Victory is decided **only by `isGoal()`**, never by the interface.

### 8.8 `draw()` — from the state to pixels
`dessiner_niveau()` loops over `self.etat.grid`: for each `S . *` it draws a target plate, for each `B *` a box sprite (a green outline if it is `*`), then the cat at `player_pos`, then the door and the effects. The ground, walls and scenery are pre-drawn once in `preparer_fond()` for speed. `dessiner_barre()` draws the bottom bar: level, moves, `self.resultat`, the buttons.

### 8.9 Complete example, step by step

You open level 1, press **3** (A* h3):
1. `handle_events`: `K_3` → `resoudre(3)`.
2. `lancer(3)` → `AStar(self.etat, successorFunction, isGoal, h3)`.
3. Inside, for each node: `successorFunction()` gives children, `setF(h3)` gives f, the heap orders them.
4. It returns the goal node after 5 steps; `getSolution()` = `RIGHT, UP, LEFT, LEFT`.
5. The bar shows `A* h3 : cout 4 | 5 steps | 0.000 s`; the blue path is drawn.
6. `update()` plays one action every 260 ms through `bouger`; the cat and the box slide.
7. After the 4th action `isGoal()` is true → the door opens → "BRAVO".

---

## 9. The tests (`test_core.py`)
Simple `assert` functions, run with `python test_core.py`:
- rules: a wall blocks, a box cannot be pushed into a wall or another box, a box on a target becomes `*`, leaving a target restores `S`;
- all levels are well formed; `isGoal` is false at the start and true on a solved board;
- the parent state is never modified by `successorFunction`;
- `Node`: root `g = 0`, `getPath`/`getSolution`;
- BFS: already-goal start, one push, no-solution level, all 8 levels (optimal costs and exact steps);
- A*: `setF`, heuristic values, all 8 levels with the 3 heuristics (same costs as BFS, exact steps, solution replayed to a goal).

---

## 10. Questions the teacher may ask (and short answers)

- **Where are the rules?** Only in `SokobanPuzzle.successorFunction()`. GUI, BFS and A* all call it.
- **Why a tuple of strings for the grid?** Immutable and hashable → a state cannot be corrupted, and it can go into a `set`/`dict`.
- **Why `__eq__` / `__hash__`?** To recognise an already-seen state (Open/Closed membership).
- **What is a step?** One node developed (one turn of the main loop).
- **Why is BFS optimal here?** All moves cost 1, so the shallowest solution is the cheapest.
- **BFS vs A*?** BFS uses a FIFO queue (shallowest first), A* a priority queue by f = g + h. A* tests the goal when the node leaves Open; BFS when it is generated.
- **What does a heuristic do?** Estimates the remaining cost to guide the search; a good one means fewer nodes developed.
- **What is admissible?** h never overestimates the real remaining cost; then A* is optimal. h1 is admissible; h2 and h3 are not guaranteed.
- **Why is h3 better than h2?** It also counts the player's walk to the first box, which h2 ignores although each move costs 1.
- **Are there deadlock checks?** No: the statement does not ask for it.
- **Why do you need `Closed`?** To avoid re-developing a state already developed (the game has loops: you can go left then right).
- **How does the interface show the solution?** It replays the list of actions with the same `bouger` the keyboard uses, one every 260 ms.
- **Where do the sprites come from?** An itch.io pack, cut by `assets_loader.py`; the sounds are generated by code.

## 11. Mini glossary
- **state**: one position of the game (grid + player).
- **successor**: a state reachable in one legal move.
- **node**: state + parent + action + g (+ f).
- **Open / Closed**: nodes waiting to be developed / already developed.
- **g, h, f**: cost so far / estimated cost to go / g + h.
- **branching factor b**: number of successors per state (≤ 4 here). **depth d**: moves in the solution.
