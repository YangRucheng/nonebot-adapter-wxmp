from typing import overload, Literal, cast, Optional
from pathlib import Path


class File():
    file_type: Literal["image", "voice", "video", "thumb"]
    file_name: str
    data: bytes

    @overload
    def __init__(self, obj: "File"):
        ...

    @overload
    def __init__(self, file: bytes, file_type: str, file_name: str):
        ...

    @overload
    def __init__(self, file_path: Path, file_type: Optional[str] = None, file_name: Optional[str] = None):
        ...

    def __init__(self, **args):
        if obj := args.get("obj", None):
            obj = cast(File, obj)
            self.file_type = obj.file_type
            self.file_name = obj.file_name
            self.data = obj.data

        elif file_path := args.get("file_path", None):
            file_path = cast(Path, file_path)
            self.file_name = file_path.name

            if file_type := args.get("file_type", None):
                self.file_type = file_type
            else:
                suffix = file_path.suffix[1:]
                if suffix in ["jpg", "jpeg", "png", "bmp", "gif"]:
                    self.file_type = "image"
                elif suffix in ["mp3", "wma", "wav", "amr"]:
                    self.file_type = "voice"
                elif suffix in ["mp4"]:
                    self.file_type = "video"
                else:
                    raise ValueError(f"Unknown file type: {suffix}")

            self.data = file_path.read_bytes()

        else:
            self.file_type = args["file_type"]
            self.file_name = args["file_name"]
            self.data = args["data"]
