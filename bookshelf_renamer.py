from pathlib import Path

from handlers.basehandler import BaseHandler
from handlers.epubhandler import EPUBHandler
from handlers.fb2handler import FB2Handler
from handlers.pdfhandler import PDFHandler


class FileRenamer:
    """Renames files in a given directory"""

    default_directory = r'C:\Users\user\Books'
    failed_to_rename = []
    handlers = {'.fb2': FB2Handler, '.epub': EPUBHandler, '.pdf': PDFHandler}

    def __init__(
        self,
        library_directory: str = default_directory,
        ignored_folders: list[str] = None,
        suggest_names: bool = False,
    ):
        """Class to rename files based on extension

        Traverses given directory and renames all files whose extension has handler. By default handlers for pdf, epub, fb2 files are implemented. If file renaming fails for any reason(no handler, handler runtime error, etc.), path to file with error text will be recorded and printed in console in the end

        Args:
            library_directory (str, optional): String path to folder with files to rename. Defaults to default_directory.
            ignored_folders (list[str], optional): List of folder names to ignore. Defaults to None.
            suggest_names (bool, optional): If set True, prints suggested filenames to console without actual file renaming. Defaults to False.
        """
        self.ignored_folders = ignored_folders if ignored_folders is not None else []
        self.library_directory = Path(library_directory)
        self.suggest_names = suggest_names

    def run(self):
        self._traverse_dir()

        # print files with error
        print('\nCAN\'T RENAME:')
        for item in self.failed_to_rename:
            print(item, sep='\n')

    def _shouldIgnore(self, dir_name: str) -> bool:
        return dir_name not in self.ignored_folders and not dir_name.startswith('.')

    def _rename_file(self, path_to_file: Path):
        file_extension = path_to_file.suffix
        handler = self.handlers.get(file_extension, BaseHandler)
        new_filename = handler.handle(path_to_file)

        if self.suggest_names:
            print(path_to_file.parent / new_filename, sep='\n')
        else:
            path_to_file.replace(path_to_file.parent / new_filename)

    def _traverse_dir(self):
        for entry in self.library_directory.iterdir():
            if entry.is_dir() and self._shouldIgnore(entry.name):
                self._traverse_dir_helper(entry)
            elif entry.is_file():
                try:
                    self._rename_file(entry)
                except Exception as e:
                    self.failed_to_rename.append(
                        (str(entry.relative_to(self.library_directory)), str(e))
                    )

    def _traverse_dir_helper(self, directory: Path):
        for entry in directory.iterdir():
            if entry.is_dir() and self._shouldIgnore(entry.name):
                self._traverse_dir_helper(entry)
            elif entry.is_file():
                try:
                    self._rename_file(entry)
                except Exception as e:
                    self.failed_to_rename.append(
                        (str(entry.relative_to(self.library_directory)), str(e))
                    )


if __name__ == '__main__':
    dir = r'C:\Users\user\Books'
    fr = FileRenamer(library_directory=dir, suggest_names=True)
    fr.run()
