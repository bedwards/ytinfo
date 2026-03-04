# ytinfo.py — Build & Verification Instructions

## Goal

Write a Python script called `ytinfo.py` that extracts metadata and transcript from a YouTube video and outputs flat JSON.

## Requirements

### Dependencies
- Python 3.10+
- `yt-dlp` (installed and on PATH, version 2026+)
- No pip dependencies — stdlib only (`subprocess`, `json`, `argparse`, `tempfile`, `re`, `os`, `sys`, `datetime`)

### CLI Interface

```
python ytinfo.py <youtube_url> [-o [OUTPUT_PATH]]
python ytinfo.py -h
```

| Invocation | Behavior |
|---|---|
| `python ytinfo.py <url>` | Print JSON to **stdout** |
| `python ytinfo.py <url> -o` | Save to **auto-named file** in cwd |
| `python ytinfo.py <url> -o path.json` | Save to **specific file** |
| `python ytinfo.py -h` / `--help` | Print help text with examples |

### Auto-named file format

```
YYYY-MM-DD-<channel-word1>-<channel-word2>-<title-word1>-<title-word2>.json
```

- Date is today's date
- Take the first 2 words of channel name and first 2 words of title
- Lowercase, strip non-alphanumeric chars, join with hyphens (kebab-case)
- Example: `2026-03-04-ai-news-dario-amodei.json`

### JSON Output Schema

Flat JSON object with exactly these 5 string fields:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "channel": "Channel Name",
  "title": "Video Title",
  "description": "Full video description text...",
  "transcript": "Full transcript as a single line of text with no timestamps..."
}
```

### How to Extract Data

1. **Video ID**: Run `yt-dlp --print "%(id)s" --skip-download <url>` to get the video ID.

2. **Metadata + Subtitles**: Run yt-dlp with these flags:
   ```
   yt-dlp --no-simulate --skip-download --dump-json \
     --write-auto-subs --sub-lang en --sub-format json3 \
     -o "<tmpdir>/yt-<id>" <url>
   ```
   - `--dump-json` prints full metadata JSON to stdout
   - `--no-simulate` is **required** because `--dump-json` implies `--simulate`, which prevents subtitle file creation
   - `--skip-download` skips the video file but still writes subtitle files
   - Subtitle file will be written to: `<tmpdir>/yt-<id>.en.json3`

3. **Transcript extraction** from the `.en.json3` file:
   - Parse the JSON, iterate over `.events[]`
   - For each event with a `.segs` array, concatenate all `.segs[].utf8` values
   - Strip whitespace from each resulting line
   - **Deduplicate** — auto-generated subs repeat lines; skip any line already seen
   - **Join** all unique lines with a single space into one string
   - No timestamps in the output

4. Use a `tempfile.TemporaryDirectory()` for all intermediate files — clean up automatically.

### Error Handling

- If `yt-dlp` is not installed or fails, let the subprocess error propagate naturally
- If no subtitle file exists (video has no English captions), set `transcript` to empty string `""`
- When saving to file, print `Saved to <path>` to **stderr** (not stdout, so JSON piping works)

## Verification Plan

Run these commands and check each result:

### 1. Help text
```bash
python ytinfo.py -h
```
**Expected**: Shows usage, description, arguments, and examples. Exit 0.

### 2. Stdout output (default)
```bash
python ytinfo.py "https://www.youtube.com/watch?v=pTtueIqrg0Q" | head -c 200
```
**Expected**: Valid JSON printed to stdout with all 5 fields. `transcript` field is a single long string with no timestamps or newlines inside.

### 3. Pipe to jq (verify valid JSON)
```bash
python ytinfo.py "https://www.youtube.com/watch?v=pTtueIqrg0Q" | jq 'keys'
```
**Expected**: `["channel", "description", "title", "transcript", "url"]`

### 4. Auto-named file output
```bash
python ytinfo.py "https://www.youtube.com/watch?v=pTtueIqrg0Q" -o
```
**Expected**: Creates a file like `2026-03-04-ai-news-dario-amodei.json` in cwd. Prints `Saved to <filename>` to stderr.

### 5. Specific file output
```bash
python ytinfo.py "https://www.youtube.com/watch?v=pTtueIqrg0Q" -o /tmp/test-output.json
cat /tmp/test-output.json | jq '.transcript' | head -c 200
```
**Expected**: File created at specified path. Transcript is a single long string.

### 6. Transcript quality check
```bash
python ytinfo.py "https://www.youtube.com/watch?v=pTtueIqrg0Q" | jq -r '.transcript' | wc -w
```
**Expected**: Word count should be in the thousands for a ~25min video (expect 3000-5000 words). If 0, subtitle download failed.

### 7. No temp file leakage
```bash
ls /tmp/yt-* 2>/dev/null
```
**Expected**: No leftover files. All temp files cleaned up.
