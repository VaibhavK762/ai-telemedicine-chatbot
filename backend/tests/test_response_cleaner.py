import pytest
from backend.services.response_cleaner import clean_response

def test_clean_response_boilerplate():
    raw = "Hello dear, you should drink water. Thanks for writing in. Regards, Chat Doctor"
    expected = "you should drink water."
    assert clean_response(raw) == expected

def test_clean_response_duplicate_punctuation():
    raw = "Is this urgent?? Yes, absolutely!! Please check.."
    expected = "Is this urgent? Yes, absolutely! Please check."
    assert clean_response(raw) == expected

def test_clean_response_multiple_newlines():
    raw = "Line 1\n\n\n\nLine 2\n\nHope this helps."
    expected = "Line 1\n\nLine 2"
    assert clean_response(raw) == expected

def test_clean_response_empty():
    assert clean_response("") == ""
