from pathlib import Path

class BaseHandler:
    def handle(path_to_file: Path) -> str:
        raise NotImplementedError('Handler for this file extension is not implemented')

