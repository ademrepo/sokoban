# PLAN — Sokoban

Une étape par tour de travail. Cocher, dater et indiquer le log au fur et à mesure. Ne jamais contredire `docs/SPEC.md`.

- [x] Étape 0 — Mise en place du dépôt et du projet — 2026-10-19 — docs/logs/2026-10-19_session-01.md
- [x] Étape 1 — Niveaux (`levels.py`) — 2026-10-20 — docs/logs/2026-10-20_session-02.md
- [x] Étape 2 — État (`sokoban.py`) + tests de base — 2026-10-20 — docs/logs/2026-10-20_session-03.md
- [ ] Étape 3 — Node (`node.py`) + tests
- [ ] Étape 4 — BFS (`search.py`) + tests
- [ ] Étape 5 — Validation du cœur (BFS sur tous les niveaux, `main.py --console`)
- [ ] Étape 6 — GUI : rendu statique
- [ ] Étape 7 — GUI : jeu manuel
- [ ] Étape 8 — GUI : résolution par BFS
- [ ] Étape 9 — GUI : simulation de la solution
- [ ] Étape 10 — Relecture finale
- [ ] Étape 11 — Explications (`docs/EXPLICATIONS.md`)

## Prochaine étape
Étape 3 — `Node` (`node.py`) selon la section 3.5 de `docs/SPEC.md` (state, parent, action, g), plus `getPath()`/`getSolution()`, et asserts dans `test_core.py` sur une chaîne de 3 noeuds construite à la main.

Remarque : `pygame-ce` est installé dans l'environnement (compatible Python 3.14, importé comme `pygame`), donc rien à installer avant l'étape 6.
