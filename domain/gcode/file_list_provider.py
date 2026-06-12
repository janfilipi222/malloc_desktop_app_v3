from pathlib import Path

class FileListProvider:
    @staticmethod
    def list_files(path: Path) -> list[str]:
        return [
            f.name
            for f in path.iterdir()
            if f.is_file()
        ]
