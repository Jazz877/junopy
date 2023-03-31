from cosmpy.crypto.address import Address
from pyuno.protos.juno.feeshare.v1.tx_pb2 import (
    MsgRegisterFeeShare,
    MsgUpdateFeeShare,
    MsgCancelFeeShare,
)


def create_register_feeshare_msg(
    deployer_address: Address, contract_address: Address, withdrawer_address: Address
) -> MsgRegisterFeeShare:
    """Create a MsgRegisterFeeShare message.

    :param deployer_address: deployer address
    :param contract_address: contract address
    :param withdrawer_address: withdrawer address
    :return: MsgRegisterFeeShare message
    """
    msg = MsgRegisterFeeShare(
        contract_address=str(contract_address),
        deployer_address=str(deployer_address),
        withdrawer_address=str(withdrawer_address),
    )

    return msg


def create_update_feeshare_msg(
    deployer_address: Address, contract_address: Address, withdrawer_address: Address
) -> MsgUpdateFeeShare:
    """Create a MsgUpdateFeeShare message.

    :param deployer_address: deployer address
    :param contract_address: contract address
    :param withdrawer_address: withdrawer address
    :return: MsgUpdateFeeShare message
    """
    msg = MsgUpdateFeeShare(
        contract_address=str(contract_address),
        deployer_address=str(deployer_address),
        withdrawer_address=str(withdrawer_address),
    )

    return msg


def create_cancel_feeshare_msg(
    deployer_address: Address, contract_address: Address
) -> MsgCancelFeeShare:
    """Create a MsgCancelFeeShare message.

    :param deployer_address: deployer address
    :param contract_address: contract address
    :return: MsgCancelFeeShare message
    """
    msg = MsgCancelFeeShare(
        contract_address=str(contract_address),
        deployer_address=str(deployer_address),
    )

    return msg
