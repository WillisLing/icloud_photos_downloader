"""Path functions"""
import os
from pathlib import Path
from typing import Callable
from pathvalidate.argparse import sanitize_filename
from pyicloud.services.photos import PhotoAsset


def clean_filename(filename):
    """Replaces invalid chars in filenames with '_'
	[willis-patch]: Do nothing here, see `patchPhotoAsset` below
	"""
    return filename


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
    """Returns the path with modified stem, e.g.
    1. ("IMG1234.jpg", lambda x: f"{x}-small")  =>  "IMG1234-small.jpg"
    2. ("/path/to/IMG1234.jpg", lambda x: f"{x}-small")  =>  "/path/to/IMG1234-small.jpg"
    3. ("relative/to/IMG1234.jpg", lambda x: f"{x}-small")  =>  "relative/to/IMG1234-small.jpg"
    """
    obj = Path(path)
    new_stem = func(obj.stem)
    obj = obj.with_name(new_stem + obj.suffix)
    return str(obj)

def path_by_replace_stem(path: str, new_stem: str) -> str:
    """Returns the path with replaced stem"""
    return path_by_modify_stem(path, lambda _: new_stem)

# pylint: disable=invalid-name
def patchPhotoAsset():
    """Patch `PhotoAsset.filename` to ensure filename is valid"""
    # pylint: disable=protected-access
    PhotoAsset._ORIGfilename = PhotoAsset.filename
    def _sanitized_filename(self: PhotoAsset) -> str:
        return sanitize_filename(self._ORIGfilename, "_")
    # pylint: enable=protected-access
    PhotoAsset.filename = property(_sanitized_filename)
# pylint: enable=invalid-name
