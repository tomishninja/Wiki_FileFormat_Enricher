# File Types Database

A structured database of file formats utalizing some with Local LLM-generated metadata (API's are possible but not recommended), sourced from Wikipedia's list of file formats.

## Overview

This project parses a local copy of Wikipedia's file format list (https://en.wikipedia.org/wiki/List_of_file_formats accessed April 26 2026), extracts structured information about each file type, and uses a local LLM (via [Ollama](https://ollama.com)) to annotate each entry with additional metadata — such as encoding type, human readability, and a suggested reviewer role.

The output is a JSON database and Text file that can be used to build tooling around file identification, triage, and review workflows.

## How It Works

1. **Source data** — `ListOfFileFormats_Wikipedia.md` contains a raw copy of the Wikipedia page listing file formats, organized by category (e.g. archive, audio, video, document, etc.).
2. **Parsing** — `ConvertMarkdownToFile_ForFileTypes_Wiki.py` parses the Markdown, extracts each file extension and its description, and groups them by category.
3. **LLM enrichment** — For each file entry, a prompt is sent to a local Ollama model (`gemma4`) asking it to infer:
   - **Encoding** — e.g. ASCII, Binary, UTF-8
   - **Human Readable** — `Yes`, `No`, or `Maybe`
   - **Human Generated** — `Yes`, `No`, or `Maybe`
   - **Suggested Role** — the best-suited person to review this file type (e.g. Software Engineer, System Administrator, Data Scientist)
4. **Output** — Results are written to `parsed_metadata.txt` and `FileNameInformation.json`.

## Output Schema

Each entry in the database contains the following fields:

| Field | Description |
|---|---|
| `Identifier` | The file extension or format identifier (e.g. `ZIP`, `PDF`) |
| `Description` | A short description of the format |
| `Type` | The high-level category (e.g. Archive, Audio, Document) |
| `Encoding` | The encoding type inferred by the LLM |
| `Human Readable` | Whether the file content is human-readable - Currently Broken |
| `Human Generated` | Whether the file is typically produced by a human |
| `Suggested Role` | The recommended role for reviewing this file type |

## Requirements

- Python 3.10+
- A running [Ollama](https://ollama.com) instance at `http://localhost:11434`
- The `gemma4` model pulled in Ollama (`ollama pull gemma4`)

## Usage

```bash
python ConvertMarkdownToFile_ForFileTypes_Wiki.py
```

Output files will be written to the project root:
- `parsed_metadata.txt`
- `FileNameInformation.json`

## Project Structure

```
FileTypesDatabase/
├── ConvertMarkdownToFile_ForFileTypes_Wiki.py   # Main parsing and enrichment script
├── ListOfFileFormats_Wikipedia.md               # Source data from Wikipedia
├── FileNameInformation.json                     # Enriched file format database (JSON)
├── parsed_metadata.txt                          # Enriched file format database (Text) containing error text intended for validation
└── Drafts/
    └── Playground.py                            # Scratch/experimental scripts
```
