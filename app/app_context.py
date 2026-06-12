from pathlib import Path


class AppContext:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.fpp_dir = base_dir / "fpp_scripts"