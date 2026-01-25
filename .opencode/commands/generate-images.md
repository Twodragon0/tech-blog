# /generate-images - Image Generation Command

## Description
Generate missing post images with English-only filenames.

## Usage
```
/generate-images [--all] [--post=filename]
```

## Arguments
- `--all`: Generate images for all posts (default: false)
- `--post`: Generate image for specific post file

## Requirements
- **Filenames**: English only (no Korean characters
- **Format**: SVG preferred, PNG fallback
- **Naming**: `YYYY-MM-DD-English_Title.svg`
- **Content**: SVG text must be English only

## Workflow
1. Identify posts missing images
2. Generate SVG image for each post
3. Validate filename is English only
4. Validate SVG content has no Korean
5. Save to `assets/images/`
6. Update post front matter with image path

## Completion Promise
Output `<promise>IMAGES_GENERATED</promise>` when complete.

## Error Handling
- If generation fails, use placeholder
- Flag for manual review
- Log errors for debugging

## Security
- Validate generated content
- No sensitive data in images
- Sanitize file paths
