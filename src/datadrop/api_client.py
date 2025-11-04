"""API client for interacting with datadrop.sh"""
import json
import requests
from pathlib import Path


class DatadropAPIError(Exception):
    """Custom exception for API errors"""
    pass


class DatadropClient:
    """Client for interacting with datadrop.sh API"""

    def __init__(self, base_url: str = "https://datadrop.sh"):
        self.base_url = base_url.rstrip("/")
        self.api_url = self.base_url

    def upload_file(self, file_path: Path) -> dict:
        """
        Upload a single file to datadrop.sh

        Args:
            file_path: Path to the file to upload

        Returns:
            dict: Response from the API containing paste info and share URL

        Raises:
            DatadropAPIError: If the upload fails
        """
        if not file_path.exists():
            raise DatadropAPIError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise DatadropAPIError(f"Not a file: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f)}
                response = requests.post(self.api_url, files=files, timeout=30)

            response.raise_for_status()

            # Backend returns the URL as plain text
            # Parse response which might contain extra text like "URL: ... Status: ..."
            response_text = response.text.strip()

            # Check if response is HTML (error page)
            if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                # Extract error message from HTML if present
                error_msg = "Upload failed - received HTML error page"

                if '"errors"' in response_text:
                    # Try to extract error message
                    try:
                        # Find the data-page attribute content
                        start = response_text.find('data-page="') + 11
                        end = response_text.find('"', start)
                        if start > 10 and end > start:
                            page_data = response_text[start:end].replace('&quot;', '"')
                            data = json.loads(page_data)
                            if 'props' in data and 'errors' in data['props']:
                                errors = data['props']['errors']
                                # Get first error message
                                if isinstance(errors, dict):
                                    for key, msg in errors.items():
                                        error_msg = f"{key}: {msg}"
                                        break
                                else:
                                    error_msg = str(errors)
                    except Exception as e:
                        # If parsing fails, include status code
                        error_msg = f"Upload failed - server error (status {response.status_code})"

                raise DatadropAPIError(error_msg)

            # Extract just the URL if response contains "URL:" prefix
            if "URL:" in response_text:
                # Extract the URL part
                parts = response_text.split()
                for i, part in enumerate(parts):
                    if part == "URL:" and i + 1 < len(parts):
                        share_url = parts[i + 1]
                        break
                else:
                    share_url = response_text
            else:
                share_url = response_text

            return {
                'url': share_url,
                'status': response.status_code
            }

        except requests.exceptions.RequestException as e:
            raise DatadropAPIError(f"Upload failed: {str(e)}")

    def upload_text(self, content: str, filename: str = "paste.txt") -> dict:
        """
        Upload text content as a paste

        Args:
            content: Text content to upload
            filename: Optional filename for the paste

        Returns:
            dict: Response from the API containing paste info and share URL

        Raises:
            DatadropAPIError: If the upload fails
        """
        try:
            files = {'file': (filename, content.encode('utf-8'))}
            response = requests.post(self.api_url, files=files, timeout=30)

            response.raise_for_status()

            # Backend returns the URL as plain text
            # Parse response which might contain extra text like "URL: ... Status: ..."
            response_text = response.text.strip()

            # Check if response is HTML (error page)
            if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                # Extract error message from HTML if present
                error_msg = "Upload failed - received HTML error page"

                if '"errors"' in response_text:
                    # Try to extract error message
                    try:
                        # Find the data-page attribute content
                        start = response_text.find('data-page="') + 11
                        end = response_text.find('"', start)
                        if start > 10 and end > start:
                            page_data = response_text[start:end].replace('&quot;', '"')
                            data = json.loads(page_data)
                            if 'props' in data and 'errors' in data['props']:
                                errors = data['props']['errors']
                                # Get first error message
                                if isinstance(errors, dict):
                                    for key, msg in errors.items():
                                        error_msg = f"{key}: {msg}"
                                        break
                                else:
                                    error_msg = str(errors)
                    except Exception as e:
                        # If parsing fails, include status code
                        error_msg = f"Upload failed - server error (status {response.status_code})"

                raise DatadropAPIError(error_msg)

            # Extract just the URL if response contains "URL:" prefix
            if "URL:" in response_text:
                # Extract the URL part
                parts = response_text.split()
                for i, part in enumerate(parts):
                    if part == "URL:" and i + 1 < len(parts):
                        share_url = parts[i + 1]
                        break
                else:
                    share_url = response_text
            else:
                share_url = response_text

            return {
                'url': share_url,
                'status': response.status_code
            }

        except requests.exceptions.RequestException as e:
            raise DatadropAPIError(f"Upload failed: {str(e)}")

    def upload_album(self, items: list) -> dict:
        """
        Upload multiple files and/or text content as an album to datadrop.sh

        Args:
            items: List of items, each can be:
                   - Path object (for files)
                   - dict with {'content': str, 'name': str} (for text)

        Returns:
            dict: Response from the API containing album URL

        Raises:
            DatadropAPIError: If the upload fails
        """
        if not items:
            raise DatadropAPIError("No items provided for album")

        try:
            # Prepare multipart form data
            files_list = []
            data_dict = {}
            file_handles = []

            content_index = 0
            file_index = 0

            for item in items:
                if isinstance(item, Path):
                    # It's a file path
                    if not item.exists():
                        raise DatadropAPIError(f"File not found: {item}")
                    if not item.is_file():
                        raise DatadropAPIError(f"Not a file: {item}")

                    # Open and add to files list
                    fh = open(item, 'rb')
                    file_handles.append(fh)
                    files_list.append(
                        ('files[]', (item.name, fh, 'application/octet-stream'))
                    )
                    file_index += 1

                elif isinstance(item, dict) and 'content' in item:
                    # It's text content
                    content = item['content']
                    name = item.get('name', f'paste{content_index + 1}')

                    # Add to data dict (will be sent as form fields)
                    if f'content[]' not in data_dict:
                        data_dict[f'content[]'] = []
                        data_dict[f'names[]'] = []

                    data_dict[f'content[]'].append(content)
                    data_dict[f'names[]'].append(name)
                    content_index += 1

            # Send to /album endpoint
            album_url = f"{self.base_url}/album"

            # If we have data fields, we need to convert them properly for requests
            if data_dict:
                # Flatten the arrays for multipart form data
                form_data = []
                if 'content[]' in data_dict:
                    for content in data_dict['content[]']:
                        form_data.append(('content[]', content))
                if 'names[]' in data_dict:
                    for name in data_dict['names[]']:
                        form_data.append(('names[]', name))

                # Combine files and form data
                response = requests.post(album_url, files=files_list, data=form_data, timeout=60)
            else:
                # Files only
                response = requests.post(album_url, files=files_list, timeout=60)

            # Close all file handles
            for fh in file_handles:
                fh.close()

            response.raise_for_status()

            # Backend returns the URL as plain text
            response_text = response.text.strip()

            # Check if response is HTML (error page)
            if response_text.startswith('<!DOCTYPE') or response_text.startswith('<html'):
                if '"errors"' in response_text and '"file"' in response_text:
                    try:
                        start = response_text.find('data-page="') + 11
                        end = response_text.find('"', start)
                        page_data = response_text[start:end].replace('&quot;', '"')
                        data = json.loads(page_data)
                        if 'props' in data and 'errors' in data['props']:
                            error_msg = data['props']['errors'].get('file', 'Upload failed')
                            raise DatadropAPIError(error_msg)
                    except Exception:
                        pass
                raise DatadropAPIError("Upload failed - received HTML error page")

            # Extract URL from response
            if "Album URL:" in response_text or "URL:" in response_text:
                parts = response_text.split()
                for i, part in enumerate(parts):
                    if part in ["URL:", "Album"] and i + 1 < len(parts):
                        if part == "Album" and i + 1 < len(parts) and parts[i + 1] == "URL:":
                            share_url = parts[i + 2] if i + 2 < len(parts) else response_text
                        else:
                            share_url = parts[i + 1]
                        break
                else:
                    share_url = response_text
            else:
                share_url = response_text

            return {
                'url': share_url,
                'status': response.status_code,
                'type': 'album',
                'file_count': len(items)
            }

        except requests.exceptions.RequestException as e:
            raise DatadropAPIError(f"Album upload failed: {str(e)}")

    def upload_folder(self, folder_path: Path) -> list[dict]:
        """
        Upload all files in a folder to datadrop.sh

        Args:
            folder_path: Path to the folder to upload

        Returns:
            list[dict]: List of responses for each uploaded file

        Raises:
            DatadropAPIError: If the upload fails
        """
        if not folder_path.exists():
            raise DatadropAPIError(f"Folder not found: {folder_path}")

        if not folder_path.is_dir():
            raise DatadropAPIError(f"Not a folder: {folder_path}")

        results = []
        files = list(folder_path.rglob("*"))

        # Filter to only files
        files = [f for f in files if f.is_file()]

        if not files:
            raise DatadropAPIError(f"No files found in folder: {folder_path}")

        for file_path in files:
            try:
                result = self.upload_file(file_path)
                result['local_path'] = str(file_path.relative_to(folder_path))
                results.append(result)
            except DatadropAPIError as e:
                # Continue with other files even if one fails
                results.append({
                    'error': str(e),
                    'local_path': str(file_path.relative_to(folder_path))
                })

        return results
