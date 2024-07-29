from dataclasses import dataclass


@dataclass
class File:
    path: str
    md5_checksum: str