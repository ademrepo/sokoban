# PLAN — Sokoban

Une étape par tour de travail. Cocher, dater et indiquer le log au fur et à mesure. Ne jamais contredire `docs/SPEC.md`.

- [x] Étape 0 — Mise en place du dépôt et du projet — 2026-10-19 — docs/logs/2026-10-19_session-01.md
- [x] Étape 1 — Niveaux (`levels.py`) — 2026-10-20 — docs/logs/2026-10-20_session-02.md
- [x] Étape 2 — État (`sokoban.py`) + tests de base — 2026-10-20 — docs/logs/2026-10-20_session-03.md
- [x] Étape 3 — Node (`node.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-04.md
- [x] Étape 4 — BFS (`search.py`) + tests — 2026-10-20 — docs/logs/2026-10-20_session-05.md
- [x] Étape 5 — Validation du cœur (BFS sur tous les niveaux, `main.py --console`) — 2026-10-20 — docs/logs/2026-10-20_session-06.md
- [x] Étape 6 — GUI : rendu statique d'un niveau — 2026-10-20 — docs/logs/2026-10-20_session-07.md
- [x] Étape 7 — GUI : jeu manuel (flèches, compteur de coups, recommencer) — 2026-10-20 — docs/logs/2026-10-20_session-11.md
- [x] Étape 8 — GUI : résolution par BFS (bouton « Résoudre (BFS) » : coût, nombre de pas, temps) — 2026-10-20 — docs/logs/2026-10-20_session-11.md
- [x] Étape 9 — GUI : simulation de la solution (trajectoire tracée + lecture automatique) — 2026-10-20 — docs/logs/2026-10-20_session-12.md
- [x] Étape 10 — GUI : fin de niveau (porte et lumière, chat qui marche jusqu'à la porte et remue la queue, pancarte « Bravo », slide vers le niveau suivant) et cibles en plaques à contour doré — 2026-10-20 — docs/logs/2026-10-20_session-10.md et docs/logs/2026-10-20_session-14.md
- [x] Étape 11 — GUI : menu de choix du niveau — 2026-10-20 — docs/logs/2026-10-20_session-15.md
- [x] Étape 12a — GUI : totems seulement s'ils tiennent des deux côtés de la porte (sinon aucun : niveaux 1, 5 et 6) — 2026-10-20 — docs/logs/2026-10-20_session-15.md
- [ ] Étape 12b — GUI : autres retouches du look niveau par niveau, après décision de l'équipe (petits niveaux un peu vides : Exemple 1, Maison 1/2/3). Les caisses de décor sur l'herbe restent (hors de la grille, le joueur ne peut pas y aller)
- [ ] Étape 13 — En plus (facultatif) : sons créés par le code, sans fichier ajouté (ambiance de prairie, bruit de pas) ; seulement s'il reste du temps
- [ ] Étape 14 — Relecture finale
- [ ] Étape 15 — Nettoyage : enlever tout ce qui est inutile (sprites, fonctions, imports, constantes et commentaires obsolètes, `voir_assets.py`, README à jour), avant les explications
- [ ] Étape 16 — Explications (`docs/EXPLICATIONS.md`)


## Prochaine étape
Étape 12b — GUI : autres retouches du look, seulement quand l'équipe aura décidé quoi changer (sinon passer à 13 ou 14). Ensuite : 13 (sons, facultatif), 14 (relecture), 15 (nettoyage), 16 (explications). Test : `python main.py`, voir `docs/COMMANDES.md` et `docs/SPEC.md`.
