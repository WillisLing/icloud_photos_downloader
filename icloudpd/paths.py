"""Path functions"""
import os
from pathlib import Path
from typing import Callable


def local_download_path(filename: str, size: str, download_dir: str) -> str:
    """Returns the full download path, including size"""
    filename = filename_with_size(filename, size)
    download_path = os.path.join(download_dir, filename)
    return download_path


def filename_with_size(filename: str, size: str) -> str:
    """Returns the filename with size, e.g. IMG1234.jpg, IMG1234-small.jpg"""
    if size == 'original':
        return filename
    return path_by_modify_stem(filename, lambda x: f"{x}-{size}")


def path_by_modify_stem(path: str, func: Callable[[str], str]) -> str:
    """Returns the filename with modified stem, e.g.
    1. ("IMG1234.jpg", lambda x: f"{x}-small")  =>  "IMG1234-small.jpg"
    2. ("/path/to/IMG1234.jpg", lambda x: f"{x}-small")  =>  "/path/to/IMG1234-small.jpg"
    3. ("relative/to/IMG1234.jpg", lambda x: f"{x}-small")  =>  "relative/to/IMG1234-small.jpg"
    """
    obj = Path(path)
    new_stem = func(obj.stem)
    obj = obj.with_stem(new_stem)
    return str(obj)
