# Contributing to Lampcat

Thanks for your interest! Bug reports, ideas, docs, translations and code are all welcome.

## Development setup

```bash
git clone https://github.com/tranvanhuy-hichan/lampcat-for-linux.git && cd lampcat-for-linux
./setup.sh                      # downloads Tomcat + phpMyAdmin (see README, Option B)
python3 panel/lampcat-panel.py
```

## Workflow

1. Open an [issue](https://github.com/tranvanhuy-hichan/lampcat-for-linux/issues) first for larger changes. Look for `good first issue` / `help wanted` labels if you are new.
2. Fork, then branch from `main` (`feat/...`, `fix/...`, `docs/...`).
3. Keep changes focused and update the README when behaviour changes.
4. Before opening a PR, run:
   ```bash
   # test setup.sh and the panel on a clean Ubuntu/Debian VM if you changed them
   shellcheck lampcat.sh setup.sh   # optional
   ```
5. Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`) and describe *what* and *why* in the PR.

## License

By contributing you agree that your contributions are licensed under the project's [MIT License](LICENSE).

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). For vulnerabilities see [SECURITY.md](SECURITY.md).
