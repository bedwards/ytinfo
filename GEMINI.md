# Gemini Agent Instructions

This project provides `ytinfo`, a CLI tool for extracting YouTube video metadata and transcripts into flat JSON.

## Project Structure

```
ytinfo.py   # Main script (also linked as `ytinfo` on PATH)
SKILL.md    # AI agent skill definition
SPEC.md     # Original build & verification spec
```

## Skill Registration

To make this skill available to Gemini/Antigravity:

```bash
mkdir -p "$HOME/.gemini/antigravity/skills/ytinfo"
ln -s "$(pwd)/SKILL.md" "$HOME/.gemini/antigravity/skills/ytinfo/SKILL.md"
```

## Key Facts

- **No pip dependencies** — uses only Python stdlib + `yt-dlp` on PATH.
- **Output is flat JSON** with 5 string fields: `url`, `channel`, `title`, `description`, `transcript`.
- **Transcript** is deduplicated auto-generated English subtitles joined into one line, no timestamps.
- **`-o` flag** saves to file (auto-named or explicit path); without it, JSON goes to stdout.
- **Temp files** are cleaned up automatically via `tempfile.TemporaryDirectory`.

## Common Agent Tasks

### Extract video info
```bash
ytinfo "https://youtube.com/watch?v=VIDEO_ID" -o /tmp/video.json
```

### Read the output
```bash
cat /tmp/video.json | jq '.title'
```

### Feed into NotebookLM
```bash
ytinfo "https://youtube.com/watch?v=VIDEO_ID" -o /tmp/vid.json
nlm source add <notebook-id> \
  --text "$(jq -r '.transcript' /tmp/vid.json)" \
  --title "$(jq -r '.title' /tmp/vid.json)"
```

## ArtCraft (what Brian means by it)

"ArtCraft" means **storytold's Craft Apps**: free, open-source (Apache-2.0), clean-room, pure-Rust replacements for Adobe and Microsoft Office, built for Claude to drive headless through CLI and MCP. They are vectorcraft (Illustrator), designcraft (InDesign), photocraft (Photoshop), lightcraft (Lightroom), effectcraft (After Effects), filmcraft (Premiere), AniCraft (2D animation), soundcraft (Pro Tools), deckcraft (PowerPoint), wordcraft (Word), gridcraft (Excel), pdfcraft (Acrobat), figcraft (Figma), cadcraft (AutoCAD) and craft-launcher, all at github.com/storytold/<app>. Example: `vectorcraft-cli mcp`, `vectorcraft-cli run --in x.vectorcraft --export out.pdf`. Alpha quality with frequent releases, so pin versions and check every export.

**We do NOT use ArtCraft for AI image generation.** `storytold/artcraft` (the AI image/video app, getartcraft.com) and the PyPI package `artcraft` are not what we mean.
