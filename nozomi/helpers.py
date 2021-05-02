"""Helper functions for creating paths and input normalization.

Primarily used by the nozomi API functions for generating the appropriate paths to files, and
ensuring that queries are made in a particular format used by the website.

If this package grows more complex, the functionality can be divided in a more manner. Due to
the simplicity of the current API, there isn't really a point right now.

TODO: Use logging and add logging support.

"""

import re
import logging

from nozomi.exceptions import InvalidTagFormat


_LOGGER = logging.getLogger(__name__)


def sanitize_tag(tag: str) -> str:
    """Remove and replace any invalid characters in the tag.

    Args:
        tag: The search tag.

    Raises:
        InvalidTagFormat: If the tag was not sanitized properly.

    Returns:
        A tag in a valid format.

    """
    _LOGGER.info("Sanitizing tag '%s'", tag)
    try:
        sanitized_tag = tag.lower().strip()
        sanitized_tag = re.sub('[/#%]', '', sanitized_tag)
        _validate_tag_sanitized(sanitized_tag)
    except InvalidTagFormat:
        raise
    except Exception as ex:
        _LOGGER.exception(ex)
    return sanitized_tag


def create_tag_filepath(sanitized_tag: str) -> str:
    """Build the path to a .nozomi file for a particular tag.

    Every search tag/term has an associated .nozomi file stored in the database. Each file contains
    references to data that is related to the tag. This function builds the path to that file.

    Args:
        sanitized_tag: The sanitized search tag.

    Raises:
        InvalidTagFormat: If the tag was not sanitized before creating a tag filepath.

    Returns:
        The URL of the search tag's associated .nozomi file.

    """
    _LOGGER.info("Creating tag filepath for sanitized tag '%s'", sanitized_tag)
    try:
        _validate_tag_sanitized(sanitized_tag)
        encoded_tag = _encode_tag(sanitized_tag)
    except InvalidTagFormat:
        raise InvalidTagFormat('Tag must be sanitized before creating a filepath.')
    except Exception as ex:
        _LOGGER.exception(ex)
    return f"https://j.nozomi.la/nozomi/{encoded_tag}.nozomi"


def create_post_filepath(post_id: int) -> str:
    """Build the path to a post's JSON file.

    The rules for creating the filepath can be found in the site's javascript file. They appear to
    be arbitrary decisions. The JSON file for the post contains a variety of useful data including
    image data, popularity, tags, etc.

    Args:
        post_id: The ID of a post on the website.

    Returns:
        The URL of the post's associated JSON file.

    """
    _LOGGER.info("Creating tag filepath for post ID %d", post_id)
    post_id = str(post_id)
    if len(post_id) < 3:
        path = post_id
    else:
        path = re.sub('^.*(..)(.)$', r'\g<2>/\g<1>/' + post_id, post_id)
    return f'https://j.nozomi.la/post/{path}.json'


def _validate_tag_sanitized(tag: str) -> None:
    """Validate a search tag is sanitized properly.

    Args:
        tag: The search tag.

    Raises:
        InvalidTagFormat: If the tag is an empty string or begins with an invalid character.

    """
    _LOGGER.debug("Validating that the tag '%s' is sanitized", tag)
    if not tag:
        raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot be empty.")
    if tag[0] == '-':
        raise InvalidTagFormat(f"The tag '{tag}' is invalid. Cannot begin with character '-'")


def _encode_tag(sanitized_tag: str) -> str:
    """Encode a sanitized tag using Nozomi's custom urlencoder.

    Args:
        sanitized_tag: The sanitized search tag.

    Returns:
        The encoded sanitized search tag.

    """
    _LOGGER.debug("Encoding sanitized tag '%s'", sanitized_tag)
    convert_char_to_hex = lambda c: f"%{format(ord(c.group(0)), 'x')}"
    encoded_tag = re.sub('[;/?:@=&]', convert_char_to_hex, sanitized_tag)
    return encoded_tag
