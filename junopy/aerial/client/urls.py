from urllib.parse import urlparse

from cosmpy.aerial.urls import ParsedUrl, Protocol


def parse_url(url: str) -> ParsedUrl:
    """An updated version that handle cosmos.directory urls.

    :param url: url
    :raises RuntimeError: If url scheme is unsupported
    :return: Parsed URL
    """
    result = urlparse(url)
    if result.scheme == "grpc+https":
        protocol = Protocol.GRPC
        secure = True
        default_port = 443
    elif result.scheme == "grpc+http":
        protocol = Protocol.GRPC
        secure = False
        default_port = 80
    elif result.scheme == "rest+https":
        protocol = Protocol.REST
        secure = True
        default_port = 443
    elif result.scheme == "rest+http":
        protocol = Protocol.REST
        secure = False
        default_port = 80
    else:
        raise RuntimeError(f"Unsupported url scheme: {result.scheme}")

    hostname = str(result.hostname)
    if hostname.endswith(".cosmos.directory"):
        hostname = hostname + result.path
    port = default_port if result.port is None else int(result.port)

    return ParsedUrl(protocol=protocol, secure=secure, hostname=hostname, port=port)
