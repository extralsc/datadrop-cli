# Deployment Guide for Datadrop CLI

## Option 1: Publish to PyPI (Recommended)

### Prerequisites
```bash
pip install build twine
```

### Steps

1. **Update version** in `pyproject.toml`:
```toml
[project]
name = "datadrop-cli"
version = "0.2.0"  # Update this for each release
```

2. **Build the package**:
```bash
python -m build
```
This creates:
- `dist/datadrop_cli-0.2.0-py3-none-any.whl` (wheel)
- `dist/datadrop-cli-0.2.0.tar.gz` (source distribution)

3. **Test on TestPyPI first** (optional but recommended):
```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ datadrop-cli
```

4. **Upload to PyPI**:
```bash
# You'll need a PyPI account: https://pypi.org/account/register/
twine upload dist/*
```

5. **Users can now install**:
```bash
pip install datadrop-cli
# or with pipx (recommended for CLI tools)
pipx install datadrop-cli
```

### Updating

For new versions:
1. Update version in `pyproject.toml`
2. Delete old `dist/` folder: `rm -rf dist/`
3. Build again: `python -m build`
4. Upload: `twine upload dist/*`

---

## Option 2: Install from GitHub

Users can install directly from your Git repository:

```bash
# Install from main branch
pip install git+https://github.com/yourusername/datadrop-cli.git

# Or with pipx
pipx install git+https://github.com/yourusername/datadrop-cli.git

# Install specific version/tag
pip install git+https://github.com/yourusername/datadrop-cli.git@v0.2.0
```

---

## Option 3: GitHub Releases + Downloadable Wheels

1. **Create a GitHub release**:
```bash
git tag v0.2.0
git push origin v0.2.0
```

2. **Build the package**:
```bash
python -m build
```

3. **Upload to GitHub Releases**:
- Go to GitHub → Releases → Create new release
- Upload files from `dist/` folder
- Users download `.whl` file

4. **Users install**:
```bash
pip install datadrop_cli-0.2.0-py3-none-any.whl
```

---

## Option 4: Create Standalone Binary (Advanced)

For users without Python, create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create binary
pyinstaller --onefile --name datadrop datadrop/__init__.py

# Binary is in dist/datadrop
./dist/datadrop --help
```

Users just download and run the binary - no Python needed!

---

## Option 5: Distribution Packages

### Debian/Ubuntu (.deb)
Use `dh-virtualenv` or `stdeb`:
```bash
pip install stdeb
python setup.py --command-packages=stdeb.command bdist_deb
```

### Arch Linux (AUR)
Create a PKGBUILD file for the Arch User Repository.

### Homebrew (macOS/Linux)
Create a Homebrew formula.

---

## Recommended Approach

**For most users:**
1. Publish to PyPI (easiest for Python users)
2. Create GitHub releases with built wheels as backup
3. Document both installation methods in README

**Quick start for users:**
```bash
# With pipx (recommended - isolated environment)
pipx install datadrop-cli

# Or with pip
pip install datadrop-cli
```

---

## CI/CD Automation (GitHub Actions)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

This automatically publishes to PyPI when you create a GitHub release!

---

## Testing Before Publishing

Always test your package before publishing:

```bash
# Build
python -m build

# Install locally in a fresh virtual environment
python -m venv test-env
source test-env/bin/activate
pip install dist/*.whl

# Test it
datadrop --help
datadrop "test content"

# Clean up
deactivate
rm -rf test-env
```
