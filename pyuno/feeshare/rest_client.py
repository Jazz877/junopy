from google.protobuf.json_format import Parse

from cosmpy.common.rest_client import RestClient
from pyuno.feeshare.interface import FeeShare
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


class FeeShareRestClient(FeeShare):
    """FeeShare REST client."""

    API_URL = "/juno/feeshare/v1"

    def __init__(self, rest_api: RestClient) -> None:
        """
        Initialize.

        :param rest_api: RestClient api
        """
        self._rest_api = rest_api

    def FeeShares(self, request: QueryFeeSharesRequest) -> QueryFeeSharesResponse:
        json_response = self._rest_api.get(
            f"{self.API_URL}/fee_shares",
            request,
        )
        return Parse(json_response, QueryFeeSharesResponse())

    def FeeShare(self, request: QueryFeeShareRequest) -> QueryFeeShareResponse:
        json_response = self._rest_api.get(
            f"{self.API_URL}/fee_shares/{request.contract_address}",
            request,
        )
        return Parse(json_response, QueryFeeShareResponse())

    def Params(self, request: QueryParamsRequest) -> QueryParamsResponse:
        json_response = self._rest_api.get(f"{self.API_URL}/params")
        return Parse(json_response, QueryParamsResponse())

    def DeployerFeeShares(
        self, request: QueryDeployerFeeSharesRequest
    ) -> QueryDeployerFeeSharesResponse:
        json_response = self._rest_api.get(
            f"{self.API_URL}/fee_shares/{request.deployer_address}",
            request,
        )
        return Parse(json_response, QueryDeployerFeeSharesResponse())

    def WithdrawerFeeShares(
        self, request: QueryWithdrawerFeeSharesRequest
    ) -> QueryWithdrawerFeeSharesResponse:
        json_response = self._rest_api.get(
            f"{self.API_URL}/fee_shares/{request.withdrawer_address}",
            request,
        )
        return Parse(json_response, QueryWithdrawerFeeSharesResponse())
