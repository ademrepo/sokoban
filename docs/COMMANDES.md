# Commandes du projet Sokoban

Toutes les commandes se lancent dans un terminal, à la racine du projet (le dossier qui contient `main.py`).

## Installer ce qu'il faut (une seule fois)
```
pip install pygame-ce
```

## Lancer le jeu
```
python main.py
```
Ouvre la fenêtre sur le menu : cliquer sur un niveau (ou taper son numéro, 1 à 8).

## Lancer directement un niveau (sans passer par le menu)
```
python main.py --niveau 5
```
Remplacer 5 par le numéro du niveau :

| N | Niveau |
|---|---|
| 1 | Exemple 1 |
| 2 | Exemple 2 |
| 3 | Exemple 3 |
| 4 | Exemple 4 |
| 5 | Exemple 5 |
| 6 | Maison 1 |
| 7 | Maison 2 |
| 8 | Maison 3 |

## Touches et boutons du jeu
| Touche / bouton | Effet |
|---|---|
| Flèches | Bouger le chat (et pousser les caisses) |
| R ou bouton « Recommencer » | Recommencer le niveau |
| B ou bouton « Résoudre (BFS) » | Lancer le BFS : trace la trajectoire et joue la solution tout seul |
| Une flèche pendant la lecture | Arrête la lecture automatique |
| M ou bouton « Menu » | Retour au menu de choix du niveau |
| Dans le menu : clic ou touche 1 à 8 | Ouvre ce niveau |
| Échap | Quitter |

Quand toutes les caisses sont sur les cibles : la porte s'ouvre avec de la lumière, la pancarte « Bravo » descend, puis on passe au niveau suivant.

## Mode console (sans fenêtre)
```
python main.py --console
```
Résout les 8 niveaux avec le BFS et affiche la solution, le coût et le temps.

## Tests
```
python test_core.py
```
Doit afficher « Tous les tests sont passes. »

## Voir les assets (images du pack) et choisir ceux qu'on veut
Outil temporaire : `voir_assets.py` (à la racine du projet, après un `git pull`). Il sert seulement à choisir des images du pack et **sera supprimé à l'étape 15** (nettoyage). Les choix sont enregistrés dans `choix_assets.txt`, qui reste sur l'ordinateur (il n'est pas poussé) : l'envoyer à la personne qui modifie `assets_loader.py`.
```
python voir_assets.py
```
| Touche / souris | Effet |
|---|---|
| Clic sur un objet | Le sélectionne (son rectangle s'affiche en bas) |
| Entrée | Enregistre l'objet choisi dans `choix_assets.txt` |
| N / P | Feuille suivante / précédente |
| Molette ou flèches | Faire défiler (Maj + molette : sur le côté) |
| Z | Zoom x1 / x2 |
| C | Catalogue des sprites déjà utilisés par le jeu |
| Échap | Quitter |

Les feuilles sont dans `assets/Pixel Art Top Down - Basic v1.2.3/Texture/`. Les rectangles de découpe sont dans `assets_loader.py`.

## Git (rappel)
```
git pull --rebase origin main     # récupérer le travail des autres
git status                        # voir ce qui a changé
git add <fichiers>
git commit -m "Étape N : résumé"
git push origin <sa branche>
```
