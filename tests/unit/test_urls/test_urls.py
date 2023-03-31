from unittest import TestCase

from cosmpy.aerial.urls import Protocol

from pyuno.aerial.client.urls import parse_url


class TestUrls(TestCase):
    def test_parse_url(self):
        url = "grpc+https://rpc.cosmos.directory/juno"
        parsed_url = parse_url(url)

        self.assertEqual(parsed_url.protocol, Protocol.GRPC)
        self.assertEqual(parsed_url.secure, True)
        self.assertEqual(parsed_url.hostname, "rpc.cosmos.directory/juno")
        self.assertEqual(parsed_url.port, 443)
        self.assertEqual(parsed_url.host_and_port, "rpc.cosmos.directory/juno:443")
