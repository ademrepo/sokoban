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

## Prérequis

- Python 3
- `pygame-ce` (compatible avec `pygame`, y compris sur les versions récentes de Python) :
  `pip install pygame-ce`

## Lancer le jeu

```
python main.py
```

Le jeu s'ouvre sur le menu de choix du niveau. Toutes les touches sont dans `docs/COMMANDES.md`.
Ouvrir directement un niveau : `python main.py --niveau 3`.

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
- `gui.py` — interface Pygame (classe `Game`)
- `assets_loader.py` — découpe des sprites et sons créés par le code
- `main.py` — point d'entrée (`python main.py`, `--niveau N`, `--console`)
- `test_core.py` — tests (`assert`, pas de pytest)
- `assets/` — pack d'images « Pixel Art Top Down - Basic » (Cainos, itch.io)
- `docs/` — spécification (`SPEC.md`), suivi (`PLAN.md`), journal de sessions (`logs/`),
  commandes (`COMMANDES.md`), explications (`EXPLICATIONS.md`)
