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
- [x] Étape 11 — GUI : menu de choix du niveau — 2026-10-20 — docs/logs/2026-10-20_session-16.md
- [x] Étape 12 — GUI : retouches du look, niveau par niveau (décor, positions) — 2026-10-20 — docs/logs/2026-10-20_session-15.md (commit `c3de3e1`) et docs/logs/2026-10-20_session-17.md
- [x] Étape 13 — En plus (facultatif) : sons créés par le code, sans fichier ajouté (ambiance de prairie, bruit de pas) ; seulement s'il reste du temps — 2026-10-20 — docs/logs/2026-10-20_session-18.md
- [x] Étape 14 — Relecture finale — 2026-10-20 — docs/logs/2026-10-20_session-19.md
- [ ] Étape 15 — Nettoyage : enlever tout ce qui est inutile (sprites, fonctions, imports, constantes et commentaires obsolètes, `voir_assets.py`, README à jour), avant les explications
- [ ] Étape 16 — Explications (`docs/EXPLICATIONS.md`)

Correspondance avec les anciens numéros (avant la renumérotation du 2026-10-20, commit `4dc4589`) :

| Nouveau | Ancien | Contenu |
|---|---|---|
| 0 à 9 | 0 à 9 | inchangés |
| 10 | 7c + 7d | fin de niveau (porte, lumière, chat, Bravo, slide) et cibles en plaques |
| 11 | 7b | menu de choix du niveau |
| 12 | 6b + 6c | retouches du rendu, puis du look niveau par niveau |
| 13 | 9b | sons (facultatif) |
| 14 | 10 | relecture finale |
| 15 | 10b | nettoyage |
| 16 | 11 | explications |

Hors plan : commit `c3de3e1` (décor identique dans tous les niveaux, « Niveau N », fenêtre plus petite) = début de l'étape 12, documenté après coup dans docs/logs/2026-10-20_session-15.md.

## Prochaine étape
Étape 15 — nettoyage. Ensuite : 16 (explications). Test : `python main.py`, voir `docs/COMMANDES.md` et `docs/SPEC.md`.
