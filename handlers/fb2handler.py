import re
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup
from handlers.basehandler import BaseHandler

from genericfilenamebuilder import GenericFilenameBuilder

SAVED_FIELDS = ['title', 'author']
NAME_PARTS = re.compile('-name')


class FB2Handler(BaseHandler):
    """Creates filename string from fb2 file metadata

    Implements 'handle' method from Basehandler for common interface. Retrieves metadata by parsing bookfile(which is bare xml under the hood)with BeautifulSoup library
    """

    def handle(file_path: Path) -> str:
        """Creates new filename string for given fb2 file based on its metadata

        Args:
            file_path (Path): Path to file

        Returns:
            str: New filename with extension
        """
        book_metadata = FB2Handler._extract_metadata(file_path)
        book_metadata = FB2Handler._check_integrity(book_metadata)

        new_filename = FB2Handler._build_filename(book_metadata) + file_path.suffix
        return new_filename

    def _extract_metadata(file_path: Path) -> dict:
        with file_path.open(encoding='utf-8', errors='ignore') as fb2file:
            soup = BeautifulSoup(fb2file.read(), 'lxml-xml')

        title_info = soup.find('title-info')

        book_metadata = defaultdict(list)
        # add authors
        authors = title_info.find_all('author')
        for author in authors:
            name_parts = [part.contents[0] for part in author.find_all(NAME_PARTS)]
            book_metadata['author'].append(' '.join(name_parts))

        # add title
        book_title = title_info.find('book-title')
        book_metadata['title'].append(book_title.contents[0])

        return book_metadata

    def _check_integrity(raw_metadata: dict) -> dict:
        if not raw_metadata:
            raise KeyError('Metadata is empty')
        elif not all(field in raw_metadata for field in SAVED_FIELDS):
            missing_fields = [
                field for field in SAVED_FIELDS if field not in raw_metadata
            ]
            raise KeyError(
                f'Only part of required metadata was retrieved. Missing: {missing_fields}'
            )
        elif not all(raw_metadata[field] for field in SAVED_FIELDS):
            empty_fields = [field for field in SAVED_FIELDS if not raw_metadata[field]]
            raise KeyError(f'No data in one of saved fields. Empty: {empty_fields}')

        return raw_metadata

    def _build_filename(metadata: dict):
        s = GenericFilenameBuilder(metadata=metadata).build_filename_string(
            order=SAVED_FIELDS, author_field='author'
        )
        return s
