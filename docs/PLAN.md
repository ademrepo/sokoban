# PLAN — Sokoban

Une étape par tour de travail. Cocher, dater et indiquer le log au fur et à mesure. Ne jamais contredire `docs/SPEC.md`.

- [x] Étape 0 — Mise en place du dépôt et du projet — 2026-10-19 — docs/logs/2026-10-19_session-01.md
- [x] Étape 1 — Niveaux (`levels.py`) — 2026-10-20 — docs/logs/2026-10-20_session-02.md
- [x] Étape 2 — État (`sokoban.py`) + tests de base — 2026-10-20 — docs/logs/2026-10-20_session-03.md
- [x] Étape 3 — Node (`node.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-04.md
- [x] Étape 4 — BFS (`search.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-05.md
- [x] Étape 5 — Validation du cœur (BFS sur tous les niveaux, `main.py --console`) — 2026-10-20 — docs/logs/2026-10-20_session-06.md
- [x] Étape 6 — GUI : rendu statique — 2026-10-20 — docs/logs/2026-10-20_session-07.md
- [ ] Étape 6b — GUI : refaire le rendu de zéro avec les assets choisis par l'équipe (personnage, porte/portail, lumière, décor, murs, sol), portail fermé visible dans chaque niveau (ajout demandé par l'équipe)
- [ ] Étape 6c — GUI : ajuster le look de chaque niveau, niveau par niveau (décor, positions)
- [ ] Étape 7 — GUI : jeu manuel
- [ ] Étape 7b — GUI : menu de choix du niveau (ajout demandé par l'équipe)
- [ ] Étape 7c — GUI : fin de niveau : le portail s'ouvre avec une lumière quand toutes les caisses sont sur les cibles (`isGoal`), pancarte « Bravo » en bois qui glisse, puis slide vers le niveau suivant (ajout demandé par l'équipe)
- [ ] Étape 8 — GUI : résolution par BFS
- [ ] Étape 9 — GUI : simulation de la solution
- [ ] Étape 10 — Relecture finale
- [ ] Étape 11 — Explications (`docs/EXPLICATIONS.md`)

## Prochaine étape
Étape 6b — d'abord l'équipe choisit les assets avec l'outil perso `python voir_assets.py` (non versionné : détecte et numérote tous les objets des feuilles du pack, ENTRÉE enregistre le choix dans `choix_assets.txt`, aussi non versionné), puis on refait le rendu de zéro avec ces choix. Test : `python main.py --niveau N`.
Ensuite : 6c (ajustement par niveau), 7 (jeu manuel), 7b (menu), 7c (fin de niveau avec portail). Voir `docs/SPEC.md`.
