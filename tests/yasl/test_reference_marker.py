from typing import Annotated

from yasl.primitives import ReferenceMarker


def test_reference_marker_init():
    marker = ReferenceMarker("foo.bar")
    assert marker.target == "foo.bar"
    assert repr(marker) == "ref[foo.bar]"


def test_annotated_reference():
    # Verify the syntax works as expected
    MyRef = Annotated[str, ReferenceMarker("target")]
    assert MyRef.__metadata__[0].target == "target"  # type: ignore
