# OpenCode Automation (Centralized)

This repository uses centralized hourly automation under Desktop root.

## Runtime

- Pull runner: `/Users/namyongkim/Desktop/.twodragon0/bin/hourly-opencode-git-pull.sh`
- Cron installer: `/Users/namyongkim/Desktop/.twodragon0/bin/install-system-cron.sh`
- Repo inventory: `/Users/namyongkim/Desktop/.twodragon0/repos.list`

## Operational safety

- Fast-forward pull only.
- Dirty trees are skipped.
- File-lock based overlap prevention.
