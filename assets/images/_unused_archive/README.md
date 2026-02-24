# Unused Images Archive

This folder contains image files that are **not referenced** in any post, layout, or config.

- **Created by**: `python3 scripts/verify_images_unified.py --unused --move-unused-to-archive`
- **Manifest**: `manifest.txt` lists all moved files.
- **Deploy**: Excluded from Jekyll build via `_config.yml` (not served on tech.2twodragon.com).
- **Restore**: Move files back to `assets/images/` (or the subpath in the manifest) if needed.

Do not reference images from this path in new content; use files under `assets/images/` only.
