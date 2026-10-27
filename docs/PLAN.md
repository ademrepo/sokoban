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
- [x] Étape 15 — Nettoyage : enlever tout ce qui est inutile (sprites, fonctions, imports, constantes et commentaires obsolètes, `voir_assets.py`, README à jour), avant les explications — 2026-10-20 — docs/logs/2026-10-20_session-20.md
- [x] Étape 16 — Explications (`docs/EXPLICATIONS.md`) — 2026-10-20 — docs/logs/2026-10-20_session-21.md

Deuxième partie : UI/UX (demandée par ademrepo le 2026-10-20, sur la branche `adem`) :

- [x] Étape 17 — Fin de niveau : plus de passage automatique ; pancarte « Bravo » avec boutons « Niveau suivant », « Rejouer », « Menu » — 2026-10-20 — docs/logs/2026-10-20_session-24.md
- [x] Étape 18 — Mouvement fluide : le chat et la caisse glissent d'une case à l'autre, le chat se tourne, touche maintenue = il continue, Z = annuler le dernier coup — 2026-10-20 — docs/logs/2026-10-20_session-25.md
- [x] Étape 19 — Décor : objets du pack (arbres, statue, banc, coffre, panneau, vases, rochers) et ombres au sol — 2026-10-20 — docs/logs/2026-10-20_session-26.md
- [x] Étape 20 — Rendu dynamique : nuages qui passent, lucioles, cibles qui pulsent, étincelles quand une caisse arrive sur une cible — 2026-10-20 — docs/logs/2026-10-20_session-27.md
- [x] Étape 21 — Interface : barre d'infos et menu redessinés (aperçu de chaque niveau, boutons qui réagissent à la souris) — 2026-10-20 — docs/logs/2026-10-20_session-28.md
- [x] Étape 22 — Relecture du code et mise à jour de la doc (README, COMMANDES, EXPLICATIONS) — 2026-10-20 — docs/logs/2026-10-20_session-29.md

Correction d'après les notes du cours (demandée par ademrepo le 2026-10-20) :

- [x] Étape 23 — BFS : renvoyer aussi `steps` (nœuds développés), l'afficher dans l'interface et la console ; SPEC, tests et explications mis à jour — 2026-10-20 — docs/logs/2026-10-20_session-30.md
- [x] Étape 24 — Relecture de tout le code : enlever les doublons et les lignes en trop, garder un code simple « d'étudiant » — 2026-10-20 — docs/logs/2026-10-20_session-31.md
- [x] Étape 25 — Simplification : retirer ce qui est difficile à expliquer à l'oral (vignette, nuages, gestion manuelle de la touche maintenue, oiseaux...) — 2026-10-20 — docs/logs/2026-10-20_session-32.md
- [x] Étape 26 — Règles de programmation : position du joueur donnée aux successeurs (pas de nouvelle recherche), test le moins cher d'abord ; liste des règles respectées dans EXPLICATIONS — 2026-10-20 — docs/logs/2026-10-20_session-33.md
- [x] Étape 27 — Explications : questions probables sur SokobanPuzzle (génération des niveaux, init, isGoal, successorFunction) et Node ajoutées à `docs/EXPLICATIONS.md` — 2026-10-20 — docs/logs/2026-10-20_session-34.md

Deuxième sujet : algorithme A* (demandé le 2026-10-24, d'après `Project 1 Part 2.pdf`) :

- [x] Étape 28 — Node : `f` et `setF` ; `astar.py` (A* de la Figure 1.29 + heuristiques h1, h2, h3) ; tests — 2026-10-24 — docs/logs/2026-10-24_session-35.md
- [x] Étape 29 — Comparaison BFS / A* (`python main.py --compare`), complexité expliquée dans EXPLICATIONS — 2026-10-24 — docs/logs/2026-10-24_session-35.md
- [x] Étape 30 — Interface Pygame : choix de l'algorithme (BFS, A* h1, h2, h3), coût et steps de chacun affichés (tableau « Comparer »), simulation de la solution — 2026-10-24 — docs/logs/2026-10-24_session-36.md
- [x] Étape 31 — h3 : essai d'une version avec une cible = une caisse (trop compliquée, abandonnée) ; retour à h2 + trajet du joueur, avec le raisonnement écrit dans le code et EXPLICATIONS §13 — 2026-10-27 — docs/logs/2026-10-27_session-38.md

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
Étapes 0 à 31 faites (sujet partie 2 complet : A*, comparaison, interface). Ensuite, relire `docs/EXPLICATIONS.md` (§13 : A*) pour la soutenance. Test : `python test_core.py`, `python main.py --compare`, `python main.py`.
