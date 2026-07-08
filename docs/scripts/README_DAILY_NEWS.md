# Daily Tech News Collection System (Removed)

> **Removed 2026-07-08** — `.github/workflows/daily-news.yml` has been deleted.
> Its `schedule` trigger had been deprecated (commented out) since before this
> removal, and manual `workflow_dispatch` runs had gone unused for 30+ days
> (last run 2026-03-02). All scheduled news collection and auto-publish are
> now handled exclusively by `.github/workflows/ai-blogwatcher.yml`, whose
> `workflow_dispatch` inputs (`hours`, `max_news`, `mode`, `dry_run`,
> `force_publish`) are a superset of the removed workflow's manual inputs.
>
> See `docs/pipeline/workflows.md` for the current workflow list and
> `docs/pdca/content.md` for the content pipeline PDCA.
