# CLAUDE.md — Sokoban (Problem Solving, M1 Visual Computing, USTHB)

Python 3 + Pygame project, done by a group of 3 students, **sequentially** (one person after the other, same repo: https://github.com/ademrepo/sokoban.git, branch `main`). Several people will resume the work in different sessions, so everything must be traceable in the repo.

## 1. Sources of truth (read in this order when resuming)
1. `docs/PLAN.md` — the step checklist. It says what is done and what is next.
2. `docs/logs/` — one file per work session (newest last). Read the 2 or 3 newest.
3. `docs/SPEC.md` — the full specification (statement + course extracts + technical contract). **Never contradict it.** If you think it is wrong, tell the user and wait.
4. `docs/Project 1 Part 1.pdf` and `docs/Chapter 1.pdf` — original documents. Do not modify. Read them only when a step needs the figures.

## 2. Working rules
- **One step of `docs/PLAN.md` per turn, never more.** Finish the step, verify it, tick it, log it, commit, push, then STOP and report in 5 lines max (what was done, how it was verified, next step). Wait for the user to say "continue".
- If a step is too big for one go, split it in `docs/PLAN.md` first.
- Save tokens: do not paste whole files in the chat, do not re-read what you just wrote, do not re-read the PDFs once `docs/SPEC.md` exists, keep answers short.
- Ask the user only when blocked (see `docs/SPEC.md` §5). Never invent git identity/credentials.
- Never use `git push --force`, `git reset --hard` or delete files the user did not ask to delete.

## 3. Code rules
- Code must look **student-made**: simple, readable, plain functions/classes, loops and `if`. No dataclasses, decorators, abstract classes, threading, heavy type hints, or clever one-liners.
- **Comments and docstrings in FRENCH** (the student reads them to understand and will delete them at the end). Identifiers in English: the statement's names are exact (`isGoal`, `successorFunction`, `getPath`, `getSolution`), everything else in snake_case.
- Only the standard library + `pygame`.
- Do not add what the statement does not ask for: no deadlock detection, no heuristics, no algorithm other than BFS, no extra classes beyond the ones named in `docs/SPEC.md`.
- Every rule of the game lives in **one place only**: `SokobanPuzzle.successorFunction()`. The GUI must reuse it, never re-implement the rules.
- Tests are plain `assert` scripts (`python test_core.py`), no pytest. Run the tests of the current step before ticking it.

## 4. Logging workflow (mandatory)
At the **end of every step** — and also before stopping early if a session is interrupted — create or update the session log:

- File: `docs/logs/AAAA-MM-JJ_session-NN.md` (NN = 01, 02, ... for the same day; one file per work session, written in **French**).
- Template:

```
# Session NN — AAAA-MM-JJ
- Auteur : <git config user.name>
- Étape(s) du plan : <numéros>
- Statut en fin de session : terminé | en cours (préciser où on s'est arrêté)

## Ce qui a été fait
<liste courte et concrète>

## Fichiers créés / modifiés
<liste>

## Décisions prises et pourquoi
<choix de conception, interprétation d'une règle, alternatives écartées>

## Vérifications
<commandes lancées, résultats : tests, niveaux, temps de BFS>

## Problèmes / questions ouvertes
<ce qui bloque, doutes, à demander à la prof ou au groupe>

## Prochaine étape
<étape exacte du plan à faire ensuite + tout ce qu'il faut savoir pour la reprendre>
```

- Then update `docs/PLAN.md`: tick the step (`[x]`), write the date and the log file name next to it, and update the line "Prochaine étape".
- Logs are never deleted or rewritten afterwards (add a new session instead). A correction goes in the next log.

## 5. Git workflow
- At the start of a session: `git pull --rebase origin main` (a teammate may have pushed), then `git status`.
- One commit per finished step (code + tests + `docs/PLAN.md` + log together), message in French, format `Étape N : <résumé court>`. Never commit `__pycache__/`, `.venv/`, `.vscode/`, `*.unitypackage`.
- Push to `origin main` at the end of each step. If the push is rejected, `git pull --rebase origin main`, solve conflicts carefully (keep both people's work, tell the user), then push again.
- If the user stops in the middle of a step, commit the work in progress with the message `WIP étape N : <état>` and log it as "en cours" so the next person knows exactly where to restart.

## 6. Project at a glance
```
CLAUDE.md                  this file
docs/                      PDFs, SPEC.md, PLAN.md, logs/, EXPLICATIONS.md (last step)
assets/                    itch.io pack "Pixel Art Top Down - Basic v1.2.3" (do not modify)
sokoban.py                 class SokobanPuzzle (state + rules)
node.py                    class Node (state, parent, action, g, getPath, getSolution)
search.py                  function BFS (course pseudocode, Fig. 1.19)
levels.py                  levels (list of dicts name + grid of strings)
assets_loader.py           sprite loading/cutting
gui.py                     Pygame interface (class Game)
main.py                    entry point: python main.py  (--console for text mode)
test_core.py               console tests
```
Run: `python main.py` · Test: `python test_core.py`
