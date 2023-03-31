from unittest import TestCase

from google.protobuf.json_format import ParseDict

from cosmpy.common.utils import json_encode
from pyuno.feeshare.rest_client import FeeShareRestClient
from pyuno.protos.juno.feeshare.v1.query_pb2 import (
    QueryDeployerFeeSharesRequest,
    QueryDeployerFeeSharesResponse,
    QueryFeeShareRequest,
    QueryFeeShareResponse,
    QueryFeeSharesRequest,
    QueryFeeSharesResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryWithdrawerFeeSharesRequest,
    QueryWithdrawerFeeSharesResponse,
)
from tests.unit.helpers import MockRestClient


class FeeShareRestClientTestCase(TestCase):
    """Test case for FeeShareRestClient class."""

    @staticmethod
    def test_FeeShares():
        """Test FeeShares method."""
        content = {"pagination": {"next_key": "", "total": "1"}}
        mock_client = MockRestClient(json_encode(content).encode("utf8"))

        expected_response = ParseDict(content, QueryFeeSharesResponse())

        fee_share = FeeShareRestClient(mock_client)

        assert fee_share.FeeShares(QueryFeeSharesRequest()) == expected_response
        assert mock_client.last_base_url == "/juno/feeshare/v1/fee_shares"

    @staticmethod
    def test_FeeShare():
        """Test FeeShare method."""
        content = {}
        mock_client = MockRestClient(json_encode(content).encode("utf8"))

        expected_response = ParseDict(content, QueryFeeShareResponse())

        fee_share = FeeShareRestClient(mock_client)

        assert (
            fee_share.FeeShare(
                QueryFeeShareRequest(contract_address="contract_address")
            )
            == expected_response
        )
        assert (
            mock_client.last_base_url == "/juno/feeshare/v1/fee_shares/contract_address"
        )

    @staticmethod
    def test_Params():
        """Test Params method."""
        content = {}
        mock_client = MockRestClient(json_encode(content).encode("utf8"))

        expected_response = ParseDict(content, QueryParamsResponse())

        fee_share = FeeShareRestClient(mock_client)

        assert fee_share.Params(QueryParamsRequest()) == expected_response
        assert mock_client.last_base_url == "/juno/feeshare/v1/params"

    @staticmethod
    def test_DeployerFeeShares():
        """Test DeployerFeeShares method."""
        content = {"pagination": {"next_key": "", "total": "1"}}
        mock_client = MockRestClient(json_encode(content).encode("utf8"))

        expected_response = ParseDict(content, QueryDeployerFeeSharesResponse())

        fee_share = FeeShareRestClient(mock_client)

        assert (
            fee_share.DeployerFeeShares(
                QueryDeployerFeeSharesRequest(deployer_address="deployer_address")
            )
            == expected_response
        )
        assert (
            mock_client.last_base_url == "/juno/feeshare/v1/fee_shares/deployer_address"
        )

    @staticmethod
    def test_WithdrawerFeeShares():
        """Test WithdrawerFeeShares method."""
        content = {"pagination": {"next_key": "", "total": "1"}}
        mock_client = MockRestClient(json_encode(content).encode("utf8"))

        expected_response = ParseDict(content, QueryWithdrawerFeeSharesResponse())

        fee_share = FeeShareRestClient(mock_client)

        assert (
            fee_share.WithdrawerFeeShares(
                QueryWithdrawerFeeSharesRequest(withdrawer_address="withdrawer_address")
            )
            == expected_response
        )
        assert (
            mock_client.last_base_url
            == "/juno/feeshare/v1/fee_shares/withdrawer_address"
        )
