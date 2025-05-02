from typing import Any, Iterable, Iterator, Set
from slugify import slugify
import re


class TagSet(Set[str]):
    """A set of tags that automatically formats strings when they are added.

    Formatting rules:
    1. Preserves forward slashes (/) in tags by default
    2. Slugifies other special characters (except unicode characters like "ü", etc.)
    3. Prefixes tags with underscore (_) if all of the tag is numeric
    4. Removes duplicates
    5. Sorts tags alphabetically
    """

    def __init__(self, iterable: Iterable[str] = None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.add(item)

    def _is_numeric(self, tag: str) -> bool:
        """Check if a tag is numeric."""
        return re.match(r"^\d+$", tag) is not None

    def _sanitize_tag(self, tag: str, allow_slashes: bool = False) -> str:
        """Sanitize a tag according to the rules."""
        if self._is_numeric(tag):
            return f"_{tag}"
        return tag

    def _slugify_tag(self, tag: str) -> str:
        """Slugify a tag while preserving Unicode characters."""
        return slugify(tag, separator="-", lowercase=True, allow_unicode=True)

    def _format_tag(self, tag: str, allow_slashes: bool = True) -> str:
        """Format a tag according to the rules."""

        if not allow_slashes:
            tag = self._slugify_tag(tag)
            return self._sanitize_tag(tag)

        # Split by forward slashes, format each part, then rejoin
        parts = tag.split("/")
        formatted_parts = []

        for part in parts:
            # Slugify the part, but preserve forward slashes
            formatted = self._slugify_tag(part)
            formatted_parts.append(formatted)

        tag = "/".join(formatted_parts)
        return self._sanitize_tag(tag)

    def add(self, element: str, allow_slashes: bool = True) -> None:
        """Add a tag to the set, automatically formatting it."""
        super().add(self._format_tag(element, allow_slashes))

    def update(self, *s: Iterable[str]) -> None:
        """Update the set with multiple tags, automatically formatting them."""
        for iterable in s:
            for element in iterable:
                self.add(element)

    def __contains__(self, element: Any) -> bool:
        """Check if a tag exists in the set, automatically formatting the input."""
        if isinstance(element, str):
            return super().__contains__(self._format_tag(element))
        return super().__contains__(element)

    def remove(self, element: str) -> None:
        """Remove a tag from the set, automatically formatting it."""
        super().remove(self._format_tag(element))

    def discard(self, element: str) -> None:
        """Discard a tag from the set, automatically formatting it."""
        super().discard(self._format_tag(element))

    def __iter__(self) -> Iterator[str]:
        """Iterate over the tags, automatically sorting them."""
        return iter(sorted(super().__iter__()))
