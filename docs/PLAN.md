# PLAN — Sokoban

Une étape par tour de travail. Cocher, dater et indiquer le log au fur et à mesure. Ne jamais contredire `docs/SPEC.md`.

- [x] Étape 0 — Mise en place du dépôt et du projet — 2026-10-19 — docs/logs/2026-10-19_session-01.md
- [x] Étape 1 — Niveaux (`levels.py`) — 2026-10-20 — docs/logs/2026-10-20_session-02.md
- [x] Étape 2 — État (`sokoban.py`) + tests de base — 2026-10-20 — docs/logs/2026-10-20_session-03.md
- [x] Étape 3 — Node (`node.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-04.md
- [x] Étape 4 — BFS (`search.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-05.md
- [x] Étape 5 — Validation du cœur (BFS sur tous les niveaux, `main.py --console`) — 2026-10-20 — docs/logs/2026-10-20_session-06.md
- [x] Étape 6 — GUI : rendu statique — 2026-10-20 — docs/logs/2026-10-20_session-07.md
- [ ] Étape 6b — GUI : ajuster en détail l'apparence de chaque niveau (décor, assets, positions) ; le rendu de l'étape 6 est une première version, pas finie (ajout demandé par l'équipe)
- [ ] Étape 7 — GUI : jeu manuel
- [ ] Étape 7b — GUI : menu de choix du niveau (ajout demandé par l'équipe)
- [ ] Étape 7c — GUI : écran « Bravo » (panneau en bois qui glisse, décor de plantes) puis passage au niveau suivant (ajout demandé par l'équipe)
- [ ] Étape 8 — GUI : résolution par BFS
- [ ] Étape 9 — GUI : simulation de la solution
- [ ] Étape 10 — Relecture finale
- [ ] Étape 11 — Explications (`docs/EXPLICATIONS.md`)

## Prochaine étape
Étape 6b — GUI : ajuster en détail l'apparence de chaque niveau (niveau par niveau, avec les retours de l'équipe : décor, assets, positions). Pour choisir les assets : `python voir_assets.py` (outil perso, non versionné) ; commande de test : `python main.py --niveau N`.
Ensuite : étape 7 (jeu manuel, flèches du clavier via `successorFunction`, compteur de coups, touche pour recommencer, victoire détectée avec `isGoal`). Voir `docs/SPEC.md`.
