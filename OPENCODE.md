# OpenCode Automation (Centralized)

This repository uses centralized hourly automation under a configurable Desktop root.

## Runtime

- Pull runner: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/bin/hourly-opencode-git-pull.sh`
- Cron installer: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/bin/install-system-cron.sh`
- Repo inventory: `${TWODRAGON0_HOME:-~/Desktop/.twodragon0}/repos.list`

Set `TWODRAGON0_HOME` per operator machine if the manager root differs from the default.

## Operational safety

- Fast-forward pull only.
- Dirty trees are skipped.
- File-lock based overlap prevention.
