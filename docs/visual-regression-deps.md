# Visual Regression Pipeline: Dependency Pinning

## Why librsvg is pinned (via runner image)

`rsvg-convert` (from `librsvg2-bin`) is the rendering engine for SVG visual
regression. Even a minor version change can produce pixel-level differences in
anti-aliasing, font hinting, or gradient rendering. If the librsvg version
differs between the baseline-capture run and the verify run, every image will
appear to have "drifted" — producing noisy false positives on every PR.

**Strategy**: both workflows pin `runs-on: ubuntu-22.04` (Jammy). This freezes
the apt-provided `librsvg2-bin` at **2.52.x**. The ubuntu-22.04 runner image is
a fixed point; GitHub only removes old runner images with 60+ days notice.

Using `ubuntu-latest` was rejected because GitHub silently re-points it to new
Ubuntu releases (22.04 → 24.04 etc.), changing the librsvg minor version and
invalidating all stored baselines without any code change in the repo.

## How to update librsvg

1. Decide the new runner (e.g., `ubuntu-24.04` which ships librsvg 2.56.x).
2. Update `runs-on` in **both** workflows to the new image simultaneously.
3. Manually trigger `visual-baseline-refresh.yml` on `main`:
   ```bash
   gh workflow run visual-baseline-refresh.yml --ref main
   ```
4. Wait for the workflow to commit updated baselines with `[skip ci]`.
5. Open a PR that only contains the runner bump — no SVG changes.
6. The PR's visual-regression run will pass against the freshly captured bases.

**Both workflows must always use the same runner image.** Mixing capture and
verify across different Ubuntu versions produces false positives.

## How to update Pillow / numpy

Renovate monitors `requirements-visual.txt` and opens PRs grouped as
`visual-regression-deps` on Monday mornings (before 6 AM).

Before merging a Renovate PR for these deps:
1. Check the Pillow changelog for any pixel-rendering changes in `Image.save`
   PNG output or resampling defaults.
2. Trigger `visual-baseline-refresh.yml` on the Renovate branch (or merge to
   main and let auto-refresh run).
3. Review the diff artifact (`visual-diffs/`) in the Actions summary.
4. If diffs are structural (layout changes) rather than expected, investigate
   before merging.

## Current pinned versions

| Dependency | Pinned range | Source |
|---|---|---|
| librsvg2-bin | 2.52.x (ubuntu-22.04 apt) | runner image |
| Pillow | `>=10.4.0,<11.0.0` | `requirements-visual.txt` |
| numpy | `>=2.0.0,<3.0.0` | `requirements-visual.txt` |

## Ubuntu apt package version notes

GitHub-hosted runner images are rebuilt periodically. The `ubuntu-22.04` tag
always maps to the latest 22.04 image, which may receive minor apt package
updates (security patches). If a security patch to librsvg changes rendering,
baselines must be re-captured. Monitor the
[runner-images changelog](https://github.com/actions/runner-images/releases)
for librsvg changes.
