# Deploy Datadrop CLI - Step by Step

## Important: You don't deploy TO pipx

**pipx is an installation tool**, not a deployment platform. The workflow is:

1. **You deploy to PyPI** (Python Package Index)
2. **Users install from PyPI using pipx**

```bash
# You publish once to PyPI
twine upload dist/*

# Users install with pipx (which pulls from PyPI)
pipx install datadrop-cli
```

---

## Option 1: Deploy to PyPI (Recommended)

This makes your CLI installable with `pipx install datadrop-cli`

### Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Verify your email
3. Set up 2FA (required)

### Step 2: Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `datadrop-cli`
4. Scope: "Entire account" (or create after first upload for project-specific)
5. **Copy the token** (you'll only see it once!)

### Step 3: Configure Token

Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR-TOKEN-HERE
```

Or set environment variable:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...
```

### Step 4: Build and Upload

```bash
# 1. Install build tools
pip install build twine

# 2. Build the package
python -m build

# 3. Upload to PyPI
twine upload dist/*
```

### Step 5: Test

```bash
# Wait 1-2 minutes for PyPI to process, then:
pipx install datadrop-cli

# Test it works globally
datadrop --help
datadrop "test upload"
```

**Done!** Now anyone can install with:
```bash
pipx install datadrop-cli
```

---

## Option 2: Deploy via GitHub Only (No PyPI)

If you don't want to use PyPI, users can install directly from GitHub:

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Release v0.1.0"
git push origin main
```

### Step 2: Create Release (Optional)

```bash
# Tag the release
git tag v0.1.0
git push origin v0.1.0

# Build the package
python -m build

# Go to GitHub → Releases → Create new release
# Upload files from dist/ folder
```

### Step 3: Users Install

```bash
# Install from GitHub
pipx install git+https://github.com/extralsc/datadrop-cli.git

# Or from specific tag
pipx install git+https://github.com/extralsc/datadrop-cli.git@v0.1.0
```

---

## Updating/Releasing New Versions

### For PyPI:

```bash
# 1. Update version in pyproject.toml
# version = "0.2.0"

# 2. Clean old builds
rm -rf dist/ build/ *.egg-info

# 3. Build
python -m build

# 4. Upload
twine upload dist/*

# 5. Tag in git (optional)
git tag v0.2.0
git push origin v0.2.0
```

### For GitHub only:

```bash
# Just push and tag
git tag v0.2.0
git push origin v0.2.0
```

---

## Current Status - Ready to Deploy

Your CLI is ready! Here's what users will be able to do:

### After PyPI deployment:
```bash
pipx install datadrop-cli
datadrop file.txt  # Works globally!
```

### Right now (GitHub only):
```bash
pipx install git+https://github.com/extralsc/datadrop-cli.git
datadrop file.txt  # Works globally!
```

---

## Quick Commands Cheat Sheet

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*

# Test from PyPI
pipx install datadrop-cli

# Test from GitHub
pipx install git+https://github.com/extralsc/datadrop-cli.git

# Uninstall
pipx uninstall datadrop-cli

# Upgrade
pipx upgrade datadrop-cli
```

---

## Pro Tip: Automate with GitHub Actions

You can auto-publish to PyPI on each GitHub release. Create `.github/workflows/publish.yml`:

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
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install build twine

      - name: Build
        run: python -m build

      - name: Publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI token as a GitHub secret named `PYPI_API_TOKEN`.

Then just create a GitHub release and it auto-publishes to PyPI!
