"""
Security Utilities
Provides security functions for input validation and path sanitization
"""

from pathlib import Path
from typing import Union, Optional


def validate_safe_path(file_path: Union[str, Path], base_dir: Union[str, Path]) -> Optional[Path]:
    """
    Validate that a file path is safe and within the allowed base directory.

    Prevents path traversal attacks (e.g., ../../etc/passwd)

    Args:
        file_path: The path to validate
        base_dir: The base directory that file_path must be within

    Returns:
        Resolved safe Path object if valid, None if unsafe

    Example:
        >>> validate_safe_path("prompts/my_file.txt", "/app/data")
        Path('/app/data/prompts/my_file.txt')

        >>> validate_safe_path("../../etc/passwd", "/app/data")
        None  # Rejected - attempts to escape base_dir
    """
    try:
        # Convert to Path objects and resolve to absolute paths
        file_path = Path(file_path).resolve()
        base_dir = Path(base_dir).resolve()

        # Check if the resolved file path is within the base directory
        # This prevents path traversal attacks
        if base_dir in file_path.parents or file_path == base_dir:
            return file_path
        else:
            print(f"[SECURITY WARNING] Path traversal attempt blocked: {file_path}")
            print(f"[SECURITY WARNING] Path must be within: {base_dir}")
            return None

    except (ValueError, OSError) as e:
        print(f"[SECURITY WARNING] Invalid path rejected: {file_path} - {e}")
        return None


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to prevent security issues.

    Removes or replaces dangerous characters from filenames.

    Args:
        filename: The filename to sanitize
        max_length: Maximum allowed filename length (default 255)

    Returns:
        Sanitized filename string

    Example:
        >>> sanitize_filename("my../../file.txt")
        'my_____file.txt'

        >>> sanitize_filename("normal_file.txt")
        'normal_file.txt'
    """
    # Remove or replace dangerous characters
    dangerous_chars = ['/', '\\', '..', '\x00', '\n', '\r', '\t']

    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')

    # Remove leading/trailing dots and spaces (Windows issues)
    sanitized = sanitized.strip('. ')

    # Truncate to max length
    if len(sanitized) > max_length:
        # Preserve file extension if present
        if '.' in sanitized:
            name, ext = sanitized.rsplit('.', 1)
            sanitized = name[:max_length - len(ext) - 1] + '.' + ext
        else:
            sanitized = sanitized[:max_length]

    # If everything was stripped, use a default
    if not sanitized:
        sanitized = "unnamed_file"

    return sanitized


def validate_session_id(session_id: str) -> bool:
    """
    Validate that a session ID is safe.

    Prevents SQL injection and path traversal via session IDs.

    Args:
        session_id: The session ID to validate

    Returns:
        True if valid, False if suspicious

    Example:
        >>> validate_session_id("session_20250101_123456")
        True

        >>> validate_session_id("'; DROP TABLE sessions; --")
        False
    """
    # Session IDs should only contain alphanumeric characters, underscores, and hyphens
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

    # Check length (reasonable session ID length)
    if not (5 <= len(session_id) <= 100):
        print(f"[SECURITY WARNING] Invalid session_id length: {len(session_id)}")
        return False

    # Check for suspicious characters
    if not all(c in allowed_chars for c in session_id):
        print(f"[SECURITY WARNING] Invalid characters in session_id: {session_id}")
        return False

    return True
