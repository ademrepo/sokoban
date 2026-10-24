# Sokoban — Problem Solving (M1 Visual Computing, USTHB)

Modélisation et résolution du jeu Sokoban (recherche BFS) avec une interface Pygame.
Projet réalisé à plusieurs, en séquentiel (une personne après l'autre, voir `CLAUDE.md`).

## Reprendre le projet (nouveau contributeur)

Avant de coder quoi que ce soit, lire dans cet ordre :

1. `CLAUDE.md` (racine) — règles du projet, workflow git/logs, style de code attendu.
2. `docs/PLAN.md` — la case à cocher qui dit où on en est et quelle est la prochaine étape.
3. `docs/logs/` — les 2-3 fichiers les plus récents (journal de chaque session de travail).
4. `docs/SPEC.md` — la spécification complète (ne jamais la contredire).

`git pull --rebase origin main` avant de commencer, `git status` pour vérifier l'état local.

## État d'avancement

Voir `docs/PLAN.md` pour la liste à jour. En résumé à ce stade :

- Le jeu est complet : niveaux, état et règles (`SokobanPuzzle`), `Node`, `BFS`, mode console, et
  l'interface Pygame (menu, jeu à la main, bouton « Résoudre (BFS) », simulation de la solution,
  fin de niveau animée, sons).
- Les explications du code pour la soutenance sont dans `docs/EXPLICATIONS.md`.

## Installation (une seule fois)

1. Python 3 (testé avec Python 3.14). Vérifier dans un terminal : `python --version`
   (sous Windows, si `python` n'est pas reconnu, essayer `py`).
2. Récupérer le projet (branche `main`) :
   ```
   git clone https://github.com/ademrepo/sokoban.git
   cd sokoban
   ```
3. Installer Pygame (version `pygame-ce`, compatible avec `import pygame`, y compris sur les
   Python récents) :
   ```
   pip install pygame-ce
   ```
   Si `pygame` (l'ancien) est déjà installé, le désinstaller d'abord : `pip uninstall pygame`.

## Lancer le jeu

```
python main.py
```

Le jeu s'ouvre sur le **menu** : cliquer sur un niveau, taper son numéro (1 à 8), ou choisir avec
les flèches puis Entrée.

| Touche / bouton | Effet |
|---|---|
| Flèches | bouger le chat et pousser les caisses (garder appuyé pour avancer en continu) |
| Z, Retour arrière ou « Annuler » | annuler le dernier coup |
| B ou « BFS » (1, 2, 3 ou « A* h1/h2/h3 » pour A* ; C ou « Comparer » : tableau des 4 algorithmes) | résout depuis la position actuelle : affiche le coût de la solution, les steps (nœuds développés par le BFS) et le temps, trace la trajectoire, puis joue la solution |
| R ou « Recommencer » | recommencer le niveau |
| M ou « Menu » | retour au menu |
| S | couper / remettre le son |
| Échap | quitter |

Quand toutes les caisses sont sur les cibles, la porte s'ouvre, le chat y va, puis la pancarte
« Bravo » propose « Rejouer » (R), « Niveau suivant » (Entrée ou N) ou « Menu » (M).

Autres façons de lancer :

```
python main.py --niveau 3      # ouvre directement le niveau 3 (1 à 8), sans menu
python main.py --console       # sans fenêtre : BFS sur les 8 niveaux (solution, coût, steps, temps)
```

Le jeu peut être lancé depuis n'importe quel dossier (`python chemin/vers/main.py`).

## Lancer les tests

```
python test_core.py
```

Doit afficher `Tous les tests sont passes.` (quelques secondes : le BFS est lancé sur les 8 niveaux).
Les tests vérifient les règles, `Node`, le BFS, la forme des niveaux et les coûts optimaux.

## Organisation du projet

- `sokoban.py` — règles du jeu et état (`SokobanPuzzle`)
- `node.py` — noeud de l'arbre de recherche (`Node`)
- `search.py` — algorithme `BFS`
- `astar.py` — algorithme `AStar` et heuristiques `h1`, `h2`, `h3`
- `levels.py` — les niveaux
- `gui.py` — interface Pygame (classe `Game`)
- `assets_loader.py` — découpe des sprites et sons créés par le code
- `main.py` — point d'entrée (`python main.py`, `--niveau N`, `--console`)
- `test_core.py` — tests (`assert`, pas de pytest)
- `assets/` — pack d'images « Pixel Art Top Down - Basic » (Cainos, itch.io)
- `docs/` — spécification (`SPEC.md`), suivi (`PLAN.md`), journal de sessions (`logs/`),
  commandes (`COMMANDES.md`), explications (`EXPLICATIONS.md`)
