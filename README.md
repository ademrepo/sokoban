# Sokoban — Problem Solving (M1 Visual Computing, USTHB)

Modélisation et résolution du jeu Sokoban (recherche BFS) avec une interface Pygame.

## Prérequis

- Python 3
- `pygame-ce` (compatible avec `pygame`) : `pip install pygame-ce`

## Lancer le jeu

```
python main.py
```

Mode console (sans interface graphique) :

```
python main.py --console
```

## Lancer les tests

```
python test_core.py
```

## Organisation du projet

Voir `CLAUDE.md` (racine) pour les règles du projet et `docs/PLAN.md` pour l'avancement.

- `sokoban.py` — règles du jeu et état (`SokobanPuzzle`)
- `node.py` — noeud de l'arbre de recherche (`Node`)
- `search.py` — algorithme `BFS`
- `levels.py` — les niveaux
- `gui.py`, `assets_loader.py`, `main.py` — interface Pygame
- `test_core.py` — tests (`assert`, pas de pytest)
- `docs/` — spécification complète (`SPEC.md`), suivi (`PLAN.md`), journal de sessions (`logs/`)
