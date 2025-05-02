from typing import Any, Iterable, Set
from slugify import slugify


class TagSet(Set[str]):
    """A set of tags that automatically slugifies strings when they are added."""

    def __init__(self, iterable: Iterable[str] = None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, element: str) -> None:
        """Add a tag to the set, automatically slugifying it."""
        super().add(slugify(element))

    def update(self, *s: Iterable[str]) -> None:
        """Update the set with multiple tags, automatically slugifying them."""
        for iterable in s:
            for element in iterable:
                self.add(element)

    def __contains__(self, element: Any) -> bool:
        """Check if a tag exists in the set, automatically slugifying the input."""
        if isinstance(element, str):
            return super().__contains__(slugify(element))
        return super().__contains__(element)

    def remove(self, element: str) -> None:
        """Remove a tag from the set, automatically slugifying it."""
        super().remove(slugify(element))

    def discard(self, element: str) -> None:
        """Discard a tag from the set, automatically slugifying it."""
        super().discard(slugify(element))
