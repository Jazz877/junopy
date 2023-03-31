from dataclasses import dataclass

import cosmpy.aerial.client


@dataclass
class NetworkConfig(cosmpy.aerial.client.NetworkConfig):
    @classmethod
    def juno_mainnet(cls) -> "NetworkConfig":
        """Get the juno mainnet configuration.

        :return: juno mainnet configuration
        """
        return NetworkConfig(
            chain_id="juno-1",
            url="grpc+https://juno-grpc.lavenderfive.com",
            fee_minimum_gas_price=0.001,
            fee_denomination="ujuno",
            staking_denomination="",
            faucet_url=None,
        )

    @classmethod
    def cosmos_directory_juno_mainnet(cls) -> "NetworkConfig":
        """Get the juno mainnet configuration from cosmos.directory.

        :return: juno mainnet configuration
        """
        return NetworkConfig(
            chain_id="juno-1",
            url="rest+https://rest.cosmos.directory/juno",
            fee_minimum_gas_price=0.001,
            fee_denomination="ujuno",
            staking_denomination="",
            faucet_url=None,
        )
