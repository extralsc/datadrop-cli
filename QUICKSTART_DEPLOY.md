# Quick Start: Deploy Datadrop CLI

## Step 1: Build the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# - dist/datadrop_cli-0.1.0-py3-none-any.whl
# - dist/datadrop-cli-0.1.0.tar.gz
```

## Step 2: Test Locally

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install the built package
pip install dist/datadrop_cli-0.1.0-py3-none-any.whl

# Test it
datadrop --help
datadrop "test content"

# Clean up
deactivate
rm -rf test-env
```

## Step 3: Publish to PyPI

### First Time Setup

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create API token**: https://pypi.org/manage/account/token/
3. **Save token** in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
```

### Publish

```bash
# Upload to PyPI
twine upload dist/*

# Enter your credentials or use token from ~/.pypirc
```

### Test Installation

```bash
# Wait a minute for PyPI to process, then:
pipx install datadrop-cli

# Test - command is globally available now!
datadrop --help
datadrop "test"

# Works anywhere without activating environments
cd ~
datadrop file.txt
```

Done! Users can now install with `pipx install datadrop-cli` and use the `datadrop` command anywhere in their shell!

---

## Alternative: GitHub Only (No PyPI)

If you don't want to publish to PyPI:

1. **Push to GitHub**:
```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

2. **Create GitHub Release**:
- Go to GitHub → Releases → Create new release
- Tag: `v0.1.0`
- Upload files from `dist/` folder

3. **Users install**:
```bash
pipx install git+https://github.com/extralsc/datadrop-cli.git
```

---

## Updating for New Versions

1. **Update version** in `pyproject.toml`:
```toml
version = "0.2.0"
```

2. **Clean and rebuild**:
```bash
rm -rf dist/ build/ *.egg-info
python -m build
```

3. **Upload**:
```bash
twine upload dist/*
```

4. **Tag release** (optional):
```bash
git tag v0.2.0
git push origin v0.2.0
```

---

## Common Issues

### "Package already exists"
You can't upload the same version twice. Increment the version number.

### "Invalid distribution"
Make sure `pyproject.toml` is properly formatted and all required fields are filled.

### "Import error"
Make sure the package structure is correct:
```
datadrop-cli/
├── datadrop/
│   ├── __init__.py
│   └── api_client.py
├── pyproject.toml
└── README.md
```

---

## Quick Commands Reference

```bash
# Build
python -m build

# Test install locally
pip install dist/*.whl

# Upload to PyPI
twine upload dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ datadrop-cli
```
