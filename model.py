import os
from dataclasses import dataclass

OBSIDIAN_BASE_PATH = "/mnt/c/Users/rishabh.bhatnagar/OneDrive - Xebia/Documents/obsidian-value"

directory_map = {
    "": "1jypqabHFF-KOW6YPk4yXEhyqEBkNphw5",
    ".": "1jypqabHFF-KOW6YPk4yXEhyqEBkNphw5",
    "Blogs": "1RhoqFzUCWqQPOcxXco4Ck_IqdmgDmVZA",
    ".obsidian": "1YZ9_0UiTdqIXci6KapC8zAE5WYvdEAGQ",
}


@dataclass
class File:
    path: str
    md5_checksum: str

    @property
    def gdrive_path(self) -> str:
        rel_path = os.path.relpath(self.path, OBSIDIAN_BASE_PATH).strip('\\').strip('/')
        dir_name = os.path.dirname(rel_path)
        if dir_name not in directory_map:
            raise ValueError(f"Invalid relative path: {dir_name} not found in the gdrive")
        return directory_map[dir_name]
