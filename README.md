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

- Fait : niveaux (`levels.py`), état du jeu et règles (`sokoban.py`, testé dans `test_core.py`).
- Pas encore fait : `Node` (`node.py`), `BFS` (`search.py`), et toute l'interface Pygame
  (`gui.py`, `assets_loader.py`, `main.py` ne sont que des stubs vides pour l'instant).
  `python main.py` ne fait donc rien d'utile tant que ces étapes ne sont pas faites.

## Prérequis

- Python 3
- `pygame-ce` (compatible avec `pygame`, y compris sur les versions récentes de Python) :
  `pip install pygame-ce`

## Lancer le jeu (une fois les étapes GUI faites)

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

- `sokoban.py` — règles du jeu et état (`SokobanPuzzle`)
- `node.py` — noeud de l'arbre de recherche (`Node`)
- `search.py` — algorithme `BFS`
- `levels.py` — les niveaux
- `gui.py`, `assets_loader.py`, `main.py` — interface Pygame
- `test_core.py` — tests (`assert`, pas de pytest)
- `docs/` — spécification complète (`SPEC.md`), suivi (`PLAN.md`), journal de sessions (`logs/`)
