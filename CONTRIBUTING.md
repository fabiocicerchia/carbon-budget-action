# Contributing

Thanks for taking the time to contribute to carbon-budget-action! By
participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting started

You need Python 3.10+ and `make`. The action is a composite GitHub Action
(`action.yml`) that wraps `carbon_budget.py`.

1. Fork and clone the repo.
2. `make setup` — install git hooks + pre-commit.
3. `make dev` — install dev tooling (pytest, ruff, requests).
4. Create a branch: `git checkout -b feat/short-description`.

```sh
make lint    # ruff check .
make test    # pytest -q
```

To try the action end-to-end, push a branch and let the `self-test` job in
`.github/workflows/ci.yml` run it in report mode.

## Making changes

- Keep changes focused; one logical change per PR.
- Match the existing style; add or update tests.
- Update `docs/` and `examples/` when behavior changes.
- Ensure CI (`code-quality`, `security`, `ci`) passes.

Don't edit `CHANGELOG.md` or `version.txt` by hand — release-please generates
both from commit messages.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `chore:`, etc. This keeps history readable and maps cleanly to
the version bump: `fix:` → patch, `feat:` → minor, `feat!:` or a
`BREAKING CHANGE:` footer → major.

## Releases

Releases are automated by
[release-please](.github/workflows/release.yml) — you don't tag or edit the
changelog manually.

1. Merge `feat:`/`fix:` PRs into `main` as normal — **no tag is created**.
2. release-please keeps an open **release PR** ("chore: release X.Y.Z"),
   recalculating the next version + `CHANGELOG.md` on every merge.
3. Merging that release PR creates the `vX.Y.Z` tag and GitHub Release, and the
   workflow moves the floating major tag (e.g. `v1`) so consumers can pin
   `uses: fabiocicerchia/carbon-budget-action@v1`.

## Pull requests

Fill out the PR template, link related issues, and request review. Be kind.

## License

By contributing you agree that your contributions are licensed under the
project [LICENSE](LICENSE) (Apache 2.0).
