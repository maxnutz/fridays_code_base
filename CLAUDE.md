# CLAUDE.md

Guidance for working in this repository. This file covers **structure, tooling, and
workflow only** — it deliberately contains no description of *what* each project does.
Each top-level project folder has (or will have) its own `CLAUDE.md` describing its
thematic scope; read that folder's `CLAUDE.md` when working inside it.

## Repository layout

Each top-level folder is a self-contained project (scripts and/or marimo notebooks):

```
fridays_code_base/
├── Windkraft/              # project folder
├── mail_from_list/         # project folder
├── vote_for_climate_justice/   # project folder
├── emissions_heatdays/     # project folder
├── resources/              # shared datasets for ALL projects — NOT committed
│   └── <project>/          # one subfolder per project
├── <project>/output/       # generated output per project — NOT committed
├── pixi.toml               # environment + tasks
├── ruff.toml               # formatter / linter config
└── CLAUDE.md               # this file
```

Conventions:

- **Datasets are not checked in.** They live under `resources/<project>/` and are
  gitignored. Code reads inputs from there.
- **Outputs are not checked in.** Each project writes generated files to its own
  `output/` folder, which is gitignored.
- Empty `resources/` and `output/` folders are kept in git via `.gitkeep`.
- Scripts and notebooks assume they are **run from their own project folder**, so
  data paths are relative (`../resources/<project>/...` for input, `output/...` for
  output). Keep new paths consistent with this.
- Add a new project as a new top-level folder, plus its `resources/<project>/` and
  `output/` subfolders.

## Environment (pixi, not conda)

This project uses [pixi](https://pixi.sh) for environment management.

```bash
pixi install          # create/update the environment from pixi.toml + pixi.lock
pixi run <cmd>         # run a command inside the environment
pixi shell             # drop into an activated shell
```

- Add dependencies with `pixi add <pkg>` (conda-forge). **Ask before adding a new
  runtime dependency.**
- Commit `pixi.toml` and `pixi.lock`; never commit the `.pixi/` env directory.

## Notebooks (marimo, not Jupyter)

Notebooks are [marimo](https://docs.marimo.io) notebooks stored as plain `.py` files.

```bash
pixi run marimo edit <notebook>.py    # open/edit interactively
pixi run marimo run  <notebook>.py    # run as an app
```

- Do not reintroduce `.ipynb` files. To migrate one, use
  `marimo convert nb.ipynb -o nb.py`.
- marimo cells form a dataflow graph: a variable defined in one cell must be
  returned and accepted as a parameter by cells that use it. Keep that in mind when
  editing cells.

## Formatting & linting (ruff)

ruff is the single formatter and linter (config in `ruff.toml`).

```bash
pixi run fmt      # ruff format .   (apply formatting)
pixi run lint     # ruff check .    (report lint issues)
pixi run check    # fmt + lint
```

Run `pixi run fmt` before committing.

## Working style

- State assumptions before editing; if a task is ambiguous, ask one clarifying
  question.
- Prefer the smallest change that solves the problem; touch only the files the change
  needs. Don't refactor unrelated code unless asked.
- Match the existing style of the file/folder before introducing a new pattern.
- Add type hints to public functions and return values; handle exception paths
  explicitly.
- Keep functions focused (< 50 lines where reasonable).
- Remove imports/variables/functions your own change made unused.
- Verify with the narrowest relevant check (e.g. `pixi run python -m py_compile <file>`
  or running the affected script/notebook) before finishing.
- Never commit secrets. If you spot a credential in the code, flag it.
- Be concise; call out trade-offs when several reasonable approaches exist.
