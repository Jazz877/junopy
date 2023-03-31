from abc import ABC, abstractmethod

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


class FeeShare(ABC):
    """FeeShare abstract class."""

    @abstractmethod
    def FeeShares(self, request: QueryFeeSharesRequest) -> QueryFeeSharesResponse:
        """
        FeeShares retrieves all registered FeeShares

        :return: a QueryFeeSharesResponse instance
        """

    @abstractmethod
    def FeeShare(self, request: QueryFeeShareRequest) -> QueryFeeShareResponse:
        """
        FeeShare retrieves a registered FeeShare for a given contract address

        :return: a QueryFeeShareResponse instance
        """

    @abstractmethod
    def Params(self, request: QueryParamsRequest) -> QueryParamsResponse:
        """
        Params retrieves the FeeShare module params

        :return: a QueryParamsResponse instance
        """

    @abstractmethod
    def DeployerFeeShares(
        self, request: QueryDeployerFeeSharesRequest
    ) -> QueryDeployerFeeSharesResponse:
        """
        DeployerFeeShares retrieves all registered FeeShares for a given deployer

        :return: a QueryDeployerFeeSharesResponse instance
        """

    @abstractmethod
    def WithdrawerFeeShares(
        self, request: QueryWithdrawerFeeSharesRequest
    ) -> QueryWithdrawerFeeSharesResponse:
        """
        WithdrawerFeeShares retrieves all registered FeeShares for a given withdrawer

        :return: a QueryWithdrawerFeeSharesResponse instance
        """
