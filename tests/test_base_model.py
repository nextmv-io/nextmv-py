import unittest
from typing import Optional

from nextmv.base_model import BaseModel


class Foo(BaseModel):
    bar: str
    baz: Optional[int] = None


class Roh(BaseModel):
    foo: Foo
    qux: Optional[list[str]] = None
    lorem: Optional[str] = None


class TestBaseModel(unittest.TestCase):
    valid_dict = {
        "foo": {
            "bar": "bar",
            "baz": 1,
        },
        "qux": ["qux"],
        "lorem": "lorem",
    }

    def test_from_dict(self):
        roh = Roh.from_dict(self.valid_dict)
        self.assertTrue(isinstance(roh, Roh))
        self.assertTrue(isinstance(roh.foo, Foo))

    def test_change_attributes(self):
        roh = Roh.from_dict(self.valid_dict)
        self.assertEqual(roh.foo.bar, "bar")

        different_str = "different_str"
        roh.foo.bar = different_str
        self.assertEqual(roh.foo.bar, different_str)

    def test_invalid_dict(self):
        invalid = {
            "foo": {
                "bar": "bar",
                "baz": "1",
            },
            "qux": "qux",
            "lorem": "lorem",
        }
        with self.assertRaises(ValueError):
            Roh.from_dict(invalid)

    def test_to_dict(self):
        some_none = {
            "foo": {
                "bar": "bar",
            },
            "lorem": "lorem",
        }
        roh = Roh.from_dict(some_none)
        parsed = roh.to_dict()
        self.assertEqual(parsed, some_none)
