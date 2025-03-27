import pytest
from src.tools.evm_tools import get_abi, call_function, get_events, get_transaction_receipt

# Test contract on Baes: USDT
TEST_CONTRACT = "0x50c5725949a6f0c72e6c4a641f24049a917db0cb"
TEST_CHAIN_ID = 8453
TEST_ACC = "0x20b2630f501BEE7d69e401D3ABA40636d1BD1B09"

# Test contract address on mainnet: UniswawpV4 Router
TEST_CONTRACT_MAINNET = "0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af"

# Test transaction hash (a known transaction on Base)
TEST_TX_HASH = "0x9af335f5bfe18ba83a45dddf8f0e0b2924c0d1cb907f07a2da263b08a31badba"

TEST_TX_MAINNET = "0x52c99a26848578dd9214c4249b7d365fd67b2500e22a6a37a6c5adb44600410b"

def test_get_abi():
    """Test getting contract ABI."""
    abi = get_abi(TEST_CONTRACT, TEST_CHAIN_ID)
    assert isinstance(abi, list)
    assert len(abi) > 0
    
    # Check for common ERC20 functions
    function_names = [item.get('name', '') for item in abi if item.get('type') == 'function']
    assert 'balanceOf' in function_names
    assert 'transfer' in function_names
    assert 'approve' in function_names

    abi_mainnet = get_abi(TEST_CONTRACT_MAINNET, 1)
    assert isinstance(abi_mainnet, list)
    assert len(abi_mainnet) > 0

def test_call_function():
    """Test calling contract functions."""
    # Test balanceOf function
    balance = call_function(TEST_CONTRACT, "balanceOf", TEST_ACC, chain_id=TEST_CHAIN_ID)
    assert isinstance(balance, (int, str))  # Can be int or string for large numbers
    assert int(balance) >= 0
    
    # Test name function
    name = call_function(TEST_CONTRACT, "name", chain_id=TEST_CHAIN_ID)
    assert isinstance(name, str)
    assert name == "Dai Stablecoin"

def test_get_events():
    """Test getting contract events."""
    # Test getting Transfer events
    events = get_events(TEST_CONTRACT, "Transfer", from_block=1000000, to_block=1000100)
    assert isinstance(events, list)
    
    # If events are found, verify their structure
    if events:
        event = events[0]
        assert isinstance(event, dict)
        assert 'args' in event
        assert 'blockNumber' in event
        assert 'transactionHash' in event

def test_get_transaction_receipt():
    """Test getting transaction receipt."""
    receipt = get_transaction_receipt(TEST_TX_HASH, TEST_CHAIN_ID)
    assert isinstance(receipt, dict)
    assert 'blockNumber' in receipt
    assert 'transactionHash' in receipt
    assert 'status' in receipt
    assert 'gasUsed' in receipt

    receipt_mainnet = get_transaction_receipt(TEST_TX_MAINNET, 1)
    assert isinstance(receipt_mainnet, dict)

def test_invalid_address():
    """Test handling of invalid addresses."""
    invalid_address = "0xinvalid"
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        get_abi(invalid_address, TEST_CHAIN_ID)
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        call_function(invalid_address, "balanceOf", invalid_address, chain_id=TEST_CHAIN_ID)
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        get_events(invalid_address, "Transfer", chain_id=TEST_CHAIN_ID)

def test_nonexistent_function():
    """Test calling non-existent function."""
    with pytest.raises(ValueError, match="Function nonexistent not found in contract"):
        call_function(TEST_CONTRACT, "nonexistent", chain_id=TEST_CHAIN_ID)

def test_nonexistent_event():
    """Test getting non-existent event."""
    with pytest.raises(ValueError, match="Event Nonexistent not found in contract"):
        get_events(TEST_CONTRACT, "Nonexistent", chain_id=TEST_CHAIN_ID)

def test_invalid_transaction_hash():
    """Test getting receipt for invalid transaction hash."""
    invalid_hash = "0xinvalid"
    with pytest.raises(Exception):
        get_transaction_receipt(invalid_hash, chain_id=TEST_CHAIN_ID) 