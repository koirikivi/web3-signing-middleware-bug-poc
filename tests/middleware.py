"""Web3 middleware utils"""

from web3.middleware.abi import STANDARD_NORMALIZERS
from web3.middleware.signing import gen_normalized_accounts
from web3.utils.rpc_abi import TRANSACTION_PARAMS_ABIS, apply_abi_formatters_to_dict
from web3.utils.toolz import (
    compose,
)
from web3.utils.transactions import (
    fill_nonce,
    fill_transaction_defaults,
)


def convert_transaction(transaction):
    return apply_abi_formatters_to_dict(STANDARD_NORMALIZERS, TRANSACTION_PARAMS_ABIS, transaction)


def construct_sign_and_send_raw_middleware(private_key_or_account):
    # Forked from web3.middleware.signing.construct_sign_and_send_raw_middleware to correctly format bytes
    # when passing to lower layers
    """Capture transactions sign and send as raw transactions


    Keyword arguments:
    private_key_or_account -- A single private key or a tuple,
    list or set of private keys. Keys can be any of the following formats:
      - An eth_account.LocalAccount object
      - An eth_keys.PrivateKey object
      - A raw private key as a hex string or byte string
    """

    accounts = gen_normalized_accounts(private_key_or_account)

    def sign_and_send_raw_middleware(make_request, w3):

        convert_and_fill_tx = compose(
            convert_transaction,
            fill_transaction_defaults(w3),
            fill_nonce(w3))

        def middleware(method, params):
            if method != "eth_sendTransaction":
                return make_request(method, params)
            else:
                transaction = convert_and_fill_tx(params[0])

            if 'from' not in transaction:
                return make_request(method, params)
            elif transaction.get('from') not in accounts:
                return make_request(method, params)

            account = accounts[transaction['from']]
            raw_tx = account.signTransaction(transaction).rawTransaction

            return make_request(
                "eth_sendRawTransaction",
                [raw_tx])

        return middleware

    return sign_and_send_raw_middleware
