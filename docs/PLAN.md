# PLAN — Sokoban

Une étape par tour de travail. Cocher, dater et indiquer le log au fur et à mesure. Ne jamais contredire `docs/SPEC.md`.

- [x] Étape 0 — Mise en place du dépôt et du projet — 2026-10-19 — docs/logs/2026-10-19_session-01.md
- [ ] Étape 1 — Niveaux (`levels.py`)
- [ ] Étape 2 — État (`sokoban.py`) + tests de base
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
Étape 1 — Niveaux. Lire les figures du PDF (page 1 = Figure 1, page 2 = Figure 2, page 4 = Exemples 1 à 5), transcrire les plateaux dans `levels.py` selon la section 3.7 de `docs/SPEC.md`, ajouter 2-3 niveaux maison, puis afficher l'ASCII de chaque niveau dans le chat et attendre la confirmation visuelle avant de cocher l'étape.

Remarque bloquante : `pygame` n'est pas installé dans l'environnement Python actuel (Python 3.14.2). Il faudra l'installer avant l'étape 6 (`pip install pygame`), pas avant.
