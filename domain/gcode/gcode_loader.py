


class GCodeLoader:
    def load(self, path: str) -> list[str]:
        with open(path, "r") as f:
            return f.readlines()





