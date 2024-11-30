from collections import defaultdict
from pathlib import Path

from ebooklib import epub
from handlers.basehandler import BaseHandler

from genericfilenamebuilder import GenericFilenameBuilder

DEFAULT_NAMESPACE = epub.NAMESPACES['DC']
SAVED_FIELDS = ['title', 'creator']


class EPUBHandler(BaseHandler):
    """Creates filename string from epub file metadata

    Implements 'handle' method from BaseHandler for common inteface. Retrieves metadata with ebooklib package from 'DC' namespace as most common
    """

    def handle(file_path: Path) -> str:
        """Creates new filename string for given epub file based on its metadata

        Args:
            file_path (Path): Path to file

        Returns:
            str: New filename with extension
        """
        book_metadata = EPUBHandler._extract_metadata(file_path)
        book_metadata = EPUBHandler._process_metadata(book_metadata)

        # leave only one title
        book_metadata['title'] = book_metadata['title'][:1]

        new_filename = EPUBHandler._build_filename(book_metadata) + file_path.suffix
        return new_filename

    def _extract_metadata(file_path: Path) -> dict:
        book_metadata = epub.read_epub(str(file_path)).metadata[DEFAULT_NAMESPACE]
        return book_metadata

    def _process_metadata(raw_metadata: dict) -> dict:
        clean_metadata = dict(raw_metadata)
        routines = [
            EPUBHandler._flatten,
            EPUBHandler._check_integrity,
            EPUBHandler._filter,
        ]

        for routine in routines:
            clean_metadata = routine(clean_metadata)

        return clean_metadata

    def _flatten(raw_metadata: dict) -> dict:
        d = defaultdict(list)
        for key in raw_metadata:
            for data_tuple in raw_metadata[key]:
                str_field = data_tuple[0]
                if str_field is not None:
                    d[key].append(str_field.rstrip())
        return dict(d)

    def _filter(raw_metadata: dict) -> dict:
        d = defaultdict()
        for key in raw_metadata:
            if key in SAVED_FIELDS:
                d[key] = raw_metadata[key]
        return dict(d)

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
            order=SAVED_FIELDS, author_field='creator'
        )

        return s
