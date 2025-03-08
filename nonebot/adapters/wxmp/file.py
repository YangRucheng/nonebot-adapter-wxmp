from pathlib import Path
from typing import Literal, Optional, Union, TypeAlias, overload

FileType: TypeAlias = Literal["image", "voice", "video", "thumb"]


class File:
    file_type: FileType
    file_name: str
    data: bytes

    @overload
    def __init__(self, file_or_path: "File"): ...
    @overload
    def __init__(self, file_or_path: bytes, file_type: FileType, file_name: str): ...
    @overload
    def __init__(
        self,
        file_or_path: Path,
        file_type: Optional[FileType] = None,
        file_name: Optional[str] = None,
    ): ...
    def __init__(
        self,
        file_or_path: Union["File", bytes, Path],
        file_type: Optional[FileType] = None,
        file_name: Optional[str] = None,
    ):
        if isinstance(file_or_path, File):
            self.file_type = file_or_path.file_type
            self.file_name = file_or_path.file_name
            self.data = file_or_path.data
        elif isinstance(file_or_path, Path):
            self.file_name = file_or_path.name
            if file_type is None:
                suffix = file_or_path.suffix[1:]
                if suffix in ["jpg", "jpeg", "png", "bmp", "gif"]:
                    self.file_type = "image"
                elif suffix in ["mp3", "wma", "wav", "amr"]:
                    self.file_type = "voice"
                elif suffix in ["mp4"]:
                    self.file_type = "video"
                else:
                    raise ValueError(f"Unknown file type: {suffix}")
            else:
                self.file_type = file_type
            self.data = file_or_path.read_bytes()
        else:
            if file_type is None or file_name is None:
                raise ValueError("file_type and file_name must be provided")
            self.file_type = file_type
            self.file_name = file_name
            self.data = file_or_path
