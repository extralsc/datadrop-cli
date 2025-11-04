# Datadrop CLI

A simple command-line tool to upload and share files via [datadrop.sh](https://datadrop.sh) - like a pastebin for files.

## Installation

### Recommended: pipx (Globally Available CLI)

```bash
# Install with pipx
pipx install datadrop-cli-extralsc

# Now use anywhere, anytime - no environment activation needed!
datadrop file.txt
datadrop -a photo1.jpg photo2.jpg
```

**Why pipx?**

- ✅ `datadrop` command available globally in any directory
- ✅ No need to activate virtual environments
- ✅ Works in `.bashrc`, `.zshrc`, scripts, anywhere
- ✅ Isolated from system Python (safe)
- ✅ Easy to manage: `pipx uninstall datadrop-cli`

**Don't have pipx?** Install it first:

```bash
# Debian/Ubuntu
sudo apt install pipx
pipx ensurepath

# macOS
brew install pipx
pipx ensurepath

# Or with pip
pip install --user pipx
pipx ensurepath
```

### Alternative: pip with --user

```bash
# Install to ~/.local/bin (globally available)
pip install --user datadrop-cli-extralsc

# Command is now available globally
datadrop file.txt
```

### From GitHub

```bash
# Install latest from GitHub (globally available with pipx)
pipx install git+https://github.com/extralsc/datadrop-cli.git
```

### From source (Development)

```bash
# Clone and install in development mode
git clone https://github.com/extralsc/datadrop-cli.git
cd datadrop-cli
pip install -e .

# Or with pipx for global access
pipx install -e .
```

## Usage

The CLI is super simple - just pass what you want to share:

### Upload a file

```bash
datadrop file.txt
datadrop screenshot.png
datadrop document.pdf
```

### Upload multiple files/folders

```bash
datadrop file1.txt file2.txt file3.txt
datadrop file.txt folder/ screenshot.png
datadrop folder1/ folder2/ folder3/
```

All uploads happen separately and you get a summary with all URLs.

### Upload files as an album

```bash
datadrop -a file1.txt file2.txt file3.txt
datadrop --album *.jpg
datadrop -a image1.png image2.png document.pdf
```

Album mode uploads all files together in one album with a file explorer UI. Perfect for sharing multiple related files!

### Upload a folder (automatically zips)

```bash
datadrop myfolder/
datadrop ./my-project/
```

The folder will be automatically zipped before uploading.

### Create a text paste

```bash
# Direct text
datadrop "Hello World"
datadrop "Quick note to share"

# From stdin (pipe)
echo "test content" | datadrop
cat myfile.txt | datadrop
pbpaste | datadrop  # macOS clipboard
xclip -o | datadrop  # Linux clipboard
```

### Custom filename

```bash
datadrop myfile.txt --name "custom-name"
datadrop myfolder/ --name "project-backup"
datadrop "content" --name "my-note.txt"
```

## Examples

```bash
# Upload a single file
datadrop screenshot.png

# Upload multiple files at once
datadrop file1.txt file2.txt file3.txt

# Upload files as an album (file explorer UI)
datadrop -a photo1.jpg photo2.jpg photo3.jpg

# Upload text notes as album
datadrop -a "First note" "Second note"

# Mix files and text in album
datadrop -a config.json "Documentation" data.zip

# Upload folders as album (auto-zipped)
datadrop -a src/ dist/

# Mix everything: files, folders, and text
datadrop -a file.txt "Notes" folder/ image.png

# Upload mix of files and folders
datadrop README.md src/ dist/

# Upload an entire project folder (zipped)
datadrop ./my-project

# Quick paste from command output
ls -la | datadrop

# Upload with custom name (single file only)
datadrop report.pdf --name "Q4-Report"

# Share clipboard content (macOS)
pbpaste | datadrop

# Share clipboard content (Linux with xclip)
xclip -o | datadrop
```

## Features

- **Album uploads**: Upload multiple files as an album with file explorer UI (`-a` or `--album`)
- **Multiple uploads**: Upload multiple files and folders in one command
- **Smart detection**: Automatically detects files, folders, or text
- **Folder zipping**: Folders are automatically zipped before upload
- **Stdin support**: Pipe any content directly to datadrop
- **Custom naming**: Optional custom names for single uploads
- **Colored output**: Beautiful terminal feedback
- **Simple syntax**: Just `datadrop <what-you-want-to-share>`

## Commands

```bash
datadrop <input> [input2...]      # Upload file(s)/folder(s) or create paste
datadrop -a <file1> <file2> ...   # Upload multiple files as an album
datadrop --album <files...>       # Upload multiple files as an album (long form)
datadrop --name "name"            # Upload with custom name (single file only)
datadrop --version                # Show version
datadrop --help                   # Show help
```

## How it works

1. **Album mode (`-a` or `--album`)** → Upload all files as one album with file explorer UI
2. **Multiple arguments** → Upload each file/folder separately and show summary
3. **File path exists as file** → Upload the file
4. **File path exists as folder** → Zip it and upload
5. **Single argument, not a path** → Create text paste
6. **No argument but stdin has data** → Create text paste from stdin

## Album Feature

Albums let you share multiple files together in one shareable link with a file explorer UI.

**What you get:**

- 📁 File tree explorer in left sidebar
- 👁️ Text file preview (auto-loads and displays)
- ⬇️ Binary file download buttons
- 📊 Album metadata (file count, total size, expiration)
- 🌙 Dark mode support

**Usage:**

```bash
# Upload multiple images as an album
datadrop -a photo1.jpg photo2.jpg photo3.jpg

# Upload text notes as an album
datadrop -a "First note" "Second note" "Third note"

# Mix files and text in album
datadrop -a config.json "Documentation for config" data.zip

# Upload folders as album (auto-zipped)
datadrop -a folder1/ folder2/

# Mix files, folders, and text in album
datadrop -a file.txt "README content" src/ "Notes about src"
```

**Album vs Regular Multiple Upload:**

- **Album** (`-a`): All items in ONE link with file explorer UI
- **Regular**: Each item gets its OWN separate link

**Requirements:**

- Minimum 2 items required for albums
- Supports files, folders (auto-zipped), AND text content
- 10MB total size limit

**Backend Integration:**
Albums send data as multipart/form-data:

- Files: `files[]=@filename.ext`
- Text: `content[]="text"` with `names[]="name"`
- Mixed: Both files and content in same request

## Requirements

- Python >= 3.8
- click >= 8.1.7
- requests >= 2.31.0

## Development

```bash
# Install dependencies
uv sync

# Run locally
python -m datadrop --help

# Test upload
.venv/bin/datadrop test.txt
```

## API

Datadrop CLI uses the datadrop.sh API:

- Endpoint: `POST https://datadrop.sh`
- No authentication required
- Data valid for 24h before deleted

## Development

### Building the Package

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

### Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI (requires PyPI account and API token)
twine upload dist/*
```

### Running Tests

```bash
# Install in development mode
pip install -e .

# Run tests (when added)
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
