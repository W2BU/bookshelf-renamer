import logging
import re
from collections import defaultdict
from pathlib import Path

from handlers.basehandler import BaseHandler
from pypdf import PdfReader

from genericfilenamebuilder import GenericFilenameBuilder

SAVED_FIELDS = ['/Title', '/Author']
NAME_DELIMITERS = re.compile(r'[,&;]|and')
AUTHOR_FIELD = '/Author'

# silence pypdf terminal output
logging.getLogger('pypdf').setLevel(logging.ERROR)


class PDFHandler(BaseHandler):
    """Creates filename string from pdf file metadata

    Implements 'handle' method from BaseHandler for common inteface. Retrieves metadata with pypdf package
    """

    def handle(file_path: Path) -> str:
        """Creates new filename string for given pdf file based on its metadata

        Args:
            file_path (Path): Path to file

        Returns:
            str: New filename with extension
        """
        book_metadata = PDFHandler._extract_metadata(file_path)
        book_metadata = PDFHandler._process_metadata(book_metadata)

        new_filename = PDFHandler._build_filename(book_metadata) + file_path.suffix
        return new_filename

    def _extract_metadata(file_path: Path) -> dict:
        book_metadata = PdfReader(file_path).metadata
        return book_metadata

    def _process_metadata(raw_metadata: dict) -> dict:
        clean_metadata = dict(raw_metadata)
        routines = [
            PDFHandler._filter,
            PDFHandler._check_integrity,
            PDFHandler._authors_str_to_list,
        ]

        for routine in routines:
            clean_metadata = routine(clean_metadata)

        return clean_metadata

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

    def _authors_str_to_list(raw_metadata: dict) -> dict:
        authors = re.split(NAME_DELIMITERS, raw_metadata[AUTHOR_FIELD])
        raw_metadata[AUTHOR_FIELD] = authors
        return raw_metadata

    def _build_filename(metadata: dict):
        s = GenericFilenameBuilder(metadata=metadata).build_filename_string(
            order=SAVED_FIELDS, author_field='/Author'
        )
        return s
