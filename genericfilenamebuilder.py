import re
from copy import deepcopy

from unidecode import unidecode

ALLOWED_CHARS_PATTERN = re.compile(r'[^ a-zA-Z0-9]+')
PARENTHESIS_PATTERN = re.compile(r'\([^)]*\)')


class GenericFilenameBuilder:
    """Builds filename string with generic template from provided metadata"""

    def __init__(self, metadata: dict[str, list[str] | str]):
        self.metadata = deepcopy(metadata)

    def build_filename_string(
        self,
        order: list[str] = None,
        field_sep: str = '_',
        metadata_sep: str = '-',
        str_case: str = 'title',
        author_field=None,
    ) -> str:
        """Builds filename concatenating all field in given order

        Args:
            order (list[str], optional): Concatenates metadata fields in that order. Defaults to None.
            field_sep (str, optional): Separator for field data e.g. names of authors. Defaults to '_'.
            metadata_sep (str, optional): Separator for different metadata fields e.g. title and author. Defaults to '-'.
            str_case (str, optional): Str class case change method(lower, upper, title...). Defaults to 'title'.
            author_field (_type_, optional): If provided, specific author field operations are apllied e.g. removing patronymic from name. Defaults to None.

        Returns:
            str: Filename string without extension
        """

        if order is None:
            order = sorted(list(self.metadata.keys))

        # remove patronymic of all authors
        if author_field is not None:
            new_names_list = []
            for name in self.metadata[author_field]:
                split_name = name.split()
                if len(split_name) >= 3:
                    new_name = ' '.join((split_name[0], split_name[-1]))
                else:
                    new_name = name
                new_names_list.append(new_name)
            self.metadata[author_field] = new_names_list

        # filter and build
        res_str = ''
        fields = []
        for field in order:

            if isinstance(self.metadata[field], list):
                item = ' '.join(self.metadata[field])
            else:
                item = self.metadata[field]

            # remove parenthesis content
            item = re.sub(PARENTHESIS_PATTERN, '', item)

            # make string latin
            item = unidecode(item)

            # remove invalid characters
            item = re.sub(ALLOWED_CHARS_PATTERN, '', item)

            # change case
            case_func = getattr(str, str_case)
            item = case_func(item)

            fields.append(field_sep.join(item.split()))
        res_str = metadata_sep.join(fields)
        return res_str
