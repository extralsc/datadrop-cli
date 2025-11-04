"""Datadrop CLI - Upload and share files via datadrop.sh"""
from pathlib import Path
import sys
import tempfile
import zipfile
import click
from .api_client import DatadropClient, DatadropAPIError


@click.command()
@click.argument("inputs", nargs=-1, required=False)
@click.option("--name", "-n", help="Custom name for the uploaded file (only works with single file)")
@click.option("--album", "-a", is_flag=True, help="Upload multiple files as an album")
@click.version_option(version="0.1.0")
def cli(inputs: tuple, name: str, album: bool):
    """
    Datadrop CLI - Upload and share files via datadrop.sh

    A simple command-line tool to upload files and folders to datadrop.sh,
    similar to a pastebin for files.

    Examples:
        datadrop file.txt              # Upload a file
        datadrop file1.txt file2.txt   # Upload multiple files
        datadrop -a file1.txt file2.txt file3.txt  # Upload as album
        datadrop --album *.jpg         # Upload all images as album
        datadrop folder/               # Zip and upload a folder
        datadrop file.txt folder/      # Upload file and folder
        datadrop "Hello World"         # Create a text paste
        echo "test" | datadrop         # Pipe content to create paste
    """
    client = DatadropClient()

    try:
        # Check if reading from stdin
        if not inputs or len(inputs) == 0:
            if album:
                click.echo(click.style("Error: --album flag requires file arguments", fg="red"))
                sys.exit(1)

            if not sys.stdin.isatty():
                # Reading from pipe/stdin
                text = sys.stdin.read()
                if not text.strip():
                    click.echo(click.style("Error: Content is empty", fg="red"))
                    sys.exit(1)

                click.echo("Creating paste from stdin...")
                filename = name if name else "paste.txt"
                result = client.upload_text(text, filename)

                click.echo(click.style("Paste created successfully!", fg="green", bold=True))
                _display_result(result)
            else:
                # No input provided
                click.echo(click.style("Error: No input provided", fg="red"))
                click.echo("\nUsage:")
                click.echo("  datadrop file.txt")
                click.echo("  datadrop file1.txt file2.txt")
                click.echo("  datadrop -a file1.txt file2.txt")
                click.echo("  datadrop folder/")
                click.echo('  datadrop "text content"')
                click.echo("  echo 'text' | datadrop")
                sys.exit(1)
            return

        # Handle album upload
        if album:
            # Collect all items for album (files, folders, text)
            album_items = []
            temp_zips = []  # Track temp zips for cleanup
            item_display_names = []

            for idx, input_item in enumerate(inputs):
                path = Path(input_item)

                if path.exists():
                    if path.is_dir():
                        # Zip the folder and add to album
                        click.echo(f"Zipping folder: {path.name}...")
                        zip_path = _zip_folder(path, None)
                        album_items.append(zip_path)
                        temp_zips.append(zip_path)
                        item_display_names.append(f"{zip_path.name} (folder)")
                    elif path.is_file():
                        album_items.append(path)
                        item_display_names.append(path.name)
                else:
                    # Treat as text content
                    text_content = input_item
                    text_name = f"note{idx + 1}"
                    album_items.append({
                        'content': text_content,
                        'name': text_name
                    })
                    preview = text_content[:30] + "..." if len(text_content) > 30 else text_content
                    item_display_names.append(f"{text_name}.txt ({preview})")

            if len(album_items) < 2:
                click.echo(click.style("Error: Album requires at least 2 items (files, folders, or text)", fg="red"))
                sys.exit(1)

            # Upload as album
            click.echo(f"\nCreating album with {len(album_items)} items...")
            for display_name in item_display_names:
                click.echo(f"  + {display_name}")

            try:
                result = client.upload_album(album_items)
                click.echo(click.style(f"\n📦 Album created successfully with {result.get('file_count', len(album_items))} items!", fg="green", bold=True))
                _display_result(result)
            finally:
                # Clean up temp zip files
                for zip_path in temp_zips:
                    if zip_path.exists():
                        zip_path.unlink()
            return

        # Handle multiple inputs (non-album)
        results = []
        for input_item in inputs:
            path = Path(input_item)

            if path.exists():
                if path.is_file():
                    # Upload file
                    click.echo(f"Uploading file: {path.name}...")
                    result = client.upload_file(path)
                    result['input'] = str(path)
                    results.append(result)

                elif path.is_dir():
                    # Zip and upload folder
                    click.echo(f"Zipping folder: {path.name}...")
                    custom_name = name if name and len(inputs) == 1 else None
                    zip_path = _zip_folder(path, custom_name)

                    try:
                        click.echo(f"Uploading {zip_path.name}...")
                        result = client.upload_file(zip_path)
                        result['input'] = str(path)
                        results.append(result)
                    finally:
                        # Clean up temp zip file
                        if zip_path.exists():
                            zip_path.unlink()
            else:
                # Treat as text content
                click.echo(f"Creating paste: {input_item[:30]}..." if len(input_item) > 30 else f"Creating paste: {input_item}")
                filename = name if name and len(inputs) == 1 else "paste.txt"
                result = client.upload_text(input_item, filename)
                result['input'] = input_item[:50] + "..." if len(input_item) > 50 else input_item
                results.append(result)

        # Display results
        if len(results) == 1:
            # Single upload - show detailed result
            if 'error' in results[0]:
                click.echo(click.style(f"Error: {results[0]['error']}", fg="red"))
                sys.exit(1)
            else:
                click.echo(click.style("Upload successful!", fg="green", bold=True))
                _display_result(results[0])
        else:
            # Multiple uploads - show summary
            success_count = sum(1 for r in results if 'error' not in r)
            error_count = len(results) - success_count

            click.echo(click.style(f"\nUploaded {success_count}/{len(results)} items", fg="green", bold=True))

            if error_count > 0:
                click.echo(click.style(f"Failed: {error_count} items", fg="red"))

            click.echo("\nResults:")
            for result in results:
                if 'error' in result:
                    click.echo(click.style(f"  ✗ {result['input']}: {result['error']}", fg="red"))
                else:
                    click.echo(click.style(f"  ✓ {result['input']}", fg="green"))
                    if 'url' in result:
                        click.echo(f"    → {click.style(result['url'], fg='cyan')}")

    except DatadropAPIError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        sys.exit(1)


def _zip_folder(folder_path: Path, custom_name: str = None) -> Path:
    """
    Create a zip file from a folder

    Args:
        folder_path: Path to the folder to zip
        custom_name: Optional custom name for the zip file

    Returns:
        Path to the created zip file
    """
    # Use custom name or folder name
    zip_name = custom_name if custom_name else f"{folder_path.name}.zip"
    if not zip_name.endswith('.zip'):
        zip_name += '.zip'

    # Create temp file
    temp_dir = Path(tempfile.gettempdir())
    zip_path = temp_dir / zip_name

    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files in the folder
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                # Add file to zip with relative path
                arcname = file_path.relative_to(folder_path)
                zipf.write(file_path, arcname)

    return zip_path


def _display_result(result: dict):
    """Helper function to display upload result"""
    if 'url' in result:
        click.echo(f"\nShare URL: {click.style(result['url'], fg='cyan', bold=True)}")

    if 'id' in result:
        click.echo(f"Paste ID: {result['id']}")

    if 'expires_at' in result:
        click.echo(f"Expires: {result['expires_at']}")


if __name__ == "__main__":
    cli()
