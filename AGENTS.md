# AGENTS.md

Teapot, a RenderMan render project for the Utah teapot, rendered with
[gman](https://github.com/jac18281828/gman). The RIB files under `assets/` are the masters;
everything generated goes to `build/` or `renders/`. POSIX only: macOS and Linux. `README.md` holds
the layout, the conventions and how to render.

## Project facts

- **Repository:** `git@github.com:jac18281828/teapot.git` (public, MIT), checked out at
  `~/src/3d/teapot`.
- **Docs root:** `TEAPOT_ROOT="${HOME}/OneDrive/Documents/projects/teapot"`. Prompts live in
  `${TEAPOT_ROOT}/prompts/`, executor reports in `${TEAPOT_ROOT}/reports/<topic>/<RUN_TS>/`, each
  review round's `REVIEW-<N>.md` beside the report it reviews. No arcs.
- **Agenda:** `~/OneDrive/Documents/org/teapot.org`. The orchestrator owns it; an executor edits no
  agenda.
- **Machine:** the owner's workstation, where gman and a CPU for path-traced renders live.
- **gman:** `gman` on `PATH`, release 1.3.1 or later from the GitHub release archive, installed to
  `/usr/local`; `GMAN=<path>` overrides it. `tools/render.sh` refuses an older gman.
- **Python:** `python3` with `numpy`, always run with `-I`; no other dependency.

## Workflow

1. Summarize current behaviour before proposing edits.
2. **Ask each time:** new dependencies, file deletions.
3. **Always ask:** any change under `assets/`, landing on `main`, tags, force operations on any
   branch but your own `agent/`.

Branches are `agent/<topic>`, rebased onto `main`; `main` only fast-forwards. Every commit is
signed (`--gpg-sign`) and carries no attribution: no `Co-Authored-By`, no `Claude-Session`, no
"Generated with". Conventional Commits, lower-case `type: subject`; bodies are flowing paragraphs
wrapped at 100 columns.

## Python

- No code comments.
- Tests use the standard library's `unittest`, never pytest. They live in `tests/test_*.py` and
  read only files in the tree, or files they wrote to a temporary directory.

## Completion gates

Run from the repository root; every gate passes before work is complete:

```sh
python3 -I -m unittest discover -s tests -v
make all
git status --porcelain -- assets
```

The last prints nothing: no build or render writes a master. A change to geometry, a shot or the
render path also renders every shot it affects with `make shot=<name>`; a render that writes no
image, or an all-black frame, fails the gate. If a gate stays red after a genuine fix attempt,
stop and report the error.
