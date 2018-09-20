import pytest
from eth_tester.exceptions import AccountLocked
from eth_utils import to_bytes, to_checksum_address
from web3.middleware import construct_sign_and_send_raw_middleware


@pytest.fixture
def private_key_hex():
    """Some private key we can use to create an account where we know the key."""
    return '0x5e95384d8050109aab08c1922d3c230739bc16976553c317e5d0b87b59371f2a'


@pytest.fixture
def private_key_account(web3, accounts, private_key_hex):
    address = web3.personal.importRawKey(private_key_hex, "password")
    web3.eth.sendTransaction({"from": accounts[0], "to": address, "value": 1*10**18})
    return address


@pytest.fixture
def greeter(chain):
    greeter, _ = chain.provider.get_or_deploy_contract('Greeter')
    return greeter


def test_raw_transaction_address_as_string(greeter, web3, private_key_account, private_key_hex):
    # This works: Sending a transaction using the raw transaction middleware if 'from' is a hex string
    web3.middleware_stack.add(construct_sign_and_send_raw_middleware(private_key_hex))
    greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account,
    })


@pytest.mark.xfail
def test_raw_transaction_address_as_bytes(greeter, web3, private_key_account, private_key_hex):
    # This doesn't work: Sending a transaction using the raw transaction middleware if 'from' is bytes
    # (instead, with eth_tester it raises AccountLocked)
    web3.middleware_stack.add(construct_sign_and_send_raw_middleware(private_key_hex))
    private_key_account_as_bytes = to_bytes(hexstr=private_key_account)
    greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account_as_bytes,
    })


@pytest.mark.xfail
def test_raw_transaction_address_as_bytes_inject_layer_0(greeter, web3, private_key_account, private_key_hex):
    # This doesn't work: passing from as bytes address when injecting raw transaction middleware to layer 0
    # (different error than test_raw_transaction_address_as_bytes)
    web3.middleware_stack.inject(construct_sign_and_send_raw_middleware(private_key_hex), layer=0)
    private_key_account_as_bytes = to_bytes(hexstr=private_key_account)
    greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account_as_bytes,
    })


def test_normal_transaction_contract_address_as_bytes(greeter, web3, accounts):
    # This works: specifying contract address as bytes when NOT using raw transaction middleware
    sender = accounts[0]
    greeter_address_bytes = to_bytes(hexstr=greeter.address)
    assert to_checksum_address(greeter_address_bytes) == greeter.address  # sanity check

    wrapped_greeter = web3.eth.contract(address=greeter_address_bytes, abi=greeter.abi)
    wrapped_greeter.functions.payForNothing().transact({
        'value': 100,
        'from': sender,
    })


@pytest.mark.xfail
def test_raw_transaction_contract_address_as_bytes(greeter, web3, private_key_account, private_key_hex):
    # This doesn't work: passing contract address as bytes when USING raw transaction middleware
    web3.middleware_stack.add(construct_sign_and_send_raw_middleware(private_key_hex))
    greeter_address_bytes = to_bytes(hexstr=greeter.address)
    assert to_checksum_address(greeter_address_bytes) == greeter.address  # sanity check

    wrapped_greeter = web3.eth.contract(address=greeter_address_bytes, abi=greeter.abi)
    wrapped_greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account,
    })


@pytest.mark.xfail
def test_raw_transaction_contract_address_as_bytes_inject_layer_0(greeter, web3, private_key_account, private_key_hex):
    # This doesn't work: passing contract address as bytes when injecting raw transaction middleware to layer 0
    # (different error than test_raw_transaction_contract_address_as_bytes)
    web3.middleware_stack.inject(construct_sign_and_send_raw_middleware(private_key_hex), layer=0)
    greeter_address_bytes = to_bytes(hexstr=greeter.address)
    assert to_checksum_address(greeter_address_bytes) == greeter.address  # sanity check

    wrapped_greeter = web3.eth.contract(address=greeter_address_bytes, abi=greeter.abi)
    wrapped_greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account,
    })


@pytest.mark.xfail
def test_raw_transaction_address_and_contract_address_as_bytes(greeter, web3, private_key_account, private_key_hex):
    # Obviously combining the above error cases is not fruitful either
    web3.middleware_stack.add(construct_sign_and_send_raw_middleware(private_key_hex))
    private_key_account_as_bytes = to_bytes(hexstr=private_key_account)
    greeter_address_bytes = to_bytes(hexstr=greeter.address)
    assert to_checksum_address(greeter_address_bytes) == greeter.address  # sanity check

    wrapped_greeter = web3.eth.contract(address=greeter_address_bytes, abi=greeter.abi)
    wrapped_greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account_as_bytes,
    })


@pytest.mark.xfail
def test_raw_transaction_address_and_contract_address_as_bytes_inject_layer_0(greeter, web3, private_key_account, private_key_hex):
    # ...even when injecting to layer 0
    web3.middleware_stack.inject(construct_sign_and_send_raw_middleware(private_key_hex), layer=0)
    private_key_account_as_bytes = to_bytes(hexstr=private_key_account)
    greeter_address_bytes = to_bytes(hexstr=greeter.address)
    assert to_checksum_address(greeter_address_bytes) == greeter.address  # sanity check

    wrapped_greeter = web3.eth.contract(address=greeter_address_bytes, abi=greeter.abi)
    wrapped_greeter.functions.payForNothing().transact({
        'value': 100,
        'from': private_key_account_as_bytes,
    })


# SANITY CHECKS. These can be ignored

def test_greeter(greeter):
    """A sanity check to see that the contract can be called"""
    greeting = greeter.call().greet()
    assert greeting == 'Hello'


def test_private_key_account_locked(greeter, private_key_account):
    """A sanity check to see that the account is indeed locked and can't be used without sendRawTransaction"""
    with pytest.raises(AccountLocked):
        greeter.functions.payForNothing().transact({
            'value': 100,
            'from': private_key_account,
        })
