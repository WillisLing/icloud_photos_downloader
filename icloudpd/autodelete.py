"""
Delete any files found in "Recently Deleted"
"""
import os
from pathlib import Path
from tzlocal import get_localzone
from icloudpd.logger import setup_logger
from icloudpd.paths import local_download_path, path_by_replace_stem


def autodelete_photos(icloud, folder_structure, directory):
    """
    Scans the "Recently Deleted" folder and deletes any matching files
    from the download directory.
    (I.e. If you delete a photo on your phone, it's also deleted on your computer.)
    """
    logger = setup_logger()
    logger.info("Deleting any files found in 'Recently Deleted'...")

    recently_deleted = icloud.photos.albums["Recently Deleted"]

    for media in recently_deleted:
        created_date = media.created.astimezone(get_localzone())
        date_path = folder_structure.format(created_date)
        download_dir = os.path.join(directory, date_path)

        for size in ["original", "medium", "thumb"]:
            # Image (include Live Photo image part)
            path = os.path.normpath(
                local_download_path(
                    media.filename, size, download_dir))
            if os.path.exists(path):
                logger.info("Deleting %s!", path)
                os.remove(path)
            # Live Photo video part
            lp_size = size + "Video"
            if lp_size in media.versions:
                version = media.versions[lp_size]
                lp_fname = version["filename"]
                filename = path_by_replace_stem(lp_fname, Path(
                    media.filename).stem)
                for enum_fn in [filename, lp_fname]:
                    lp_path = os.path.normpath(
                        local_download_path(
                            enum_fn, size, download_dir))
                    if os.path.exists(lp_path):
                        logger.info("Deleting %s !", lp_path)
                        os.remove(lp_path)
