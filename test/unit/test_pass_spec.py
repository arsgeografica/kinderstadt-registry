import pytest
from registry.utils import pass_spec_parser, pass_spec_builder


PASS_SPECS = {
    '':             [],
    '   ':          [],
    'a':            [],
    '111':          [111],
    '111,112':      [111, 112],
    '111, 112':     [111, 112],
    '111-113':      [111, 112, 113],
    '111 - 113':    [111, 112, 113],
    '111,113-115':  [111, 113, 114, 115],
    '113-115, 111': [111, 113, 114, 115],
    '111-113':      [111, 112, 113],
}

PASS_SPECS_REVERSE = {
    '':             [],
    '111':          [111],
    '111-112':      [111, 112],
    '111-113':      [111, 112, 113],
    '111,113-115':  [111, 113, 114, 115],
    '111,113-115':  [111, 115, 114, 113],
}


@pytest.fixture(params=PASS_SPECS.items())
def spec(request):
    return request.param


@pytest.fixture(params=PASS_SPECS_REVERSE.items())
def reverse_spec(request):
    return request.param


def test_pass_spec_parser(spec):
    spec, expected = spec

    assert pass_spec_parser(spec) == expected


def test_pass_spec_builder(reverse_spec):
    expected, spec = reverse_spec

    assert pass_spec_builder(spec) == expected
