import os
import unittest

from nextmv.cloud import Client


class TestClient(unittest.TestCase):
    def test_api_key(self):
        client1 = Client(api_key="foo")
        self.assertEqual(client1.api_key, "foo")

        os.environ["NEXTMV_API_KEY"] = "bar"
        client2 = Client()
        self.assertEqual(client2.api_key, "bar")
        os.environ.pop("NEXTMV_API_KEY")

        with self.assertRaises(ValueError):
            Client(api_key="")

        with self.assertRaises(ValueError):
            Client(configuration_file="")

        os.environ["NEXTMV_PROFILE"] = "i-like-turtles"
        with self.assertRaises(ValueError):
            Client()

    def test_headers(self):
        client1 = Client(api_key="foo")
        self.assertIsNotNone(client1.headers)

        os.environ["NEXTMV_API_KEY"] = "bar"
        client2 = Client()
        self.assertEqual(client2.api_key, "bar")
        self.assertIsNotNone(client2.headers)
        os.environ.pop("NEXTMV_API_KEY")
