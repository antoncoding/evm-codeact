import pytest
from src.tools.evm_tools import get_abi, get_balance, call_function

# Test contract address (USDT on Base)
TEST_CONTRACT = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"

def test_get_abi():
    """Test getting contract ABI."""
    abi = get_abi(TEST_CONTRACT)
    assert isinstance(abi, list)
    assert len(abi) > 0
    
    # Check for common ERC20 functions
    function_names = [item.get('name', '') for item in abi if item.get('type') == 'function']
    assert 'balanceOf' in function_names
    assert 'transfer' in function_names
    assert 'approve' in function_names

def test_get_balance():
    """Test getting contract balance."""
    balance = get_balance(TEST_CONTRACT)
    assert isinstance(balance, int)
    assert balance >= 0

def test_call_function():
    """Test calling contract functions."""
    # Test balanceOf function
    balance = call_function(TEST_CONTRACT, "balanceOf", TEST_CONTRACT)
    assert isinstance(balance, int)
    assert balance >= 0
    
    # Test name function
    name = call_function(TEST_CONTRACT, "name")
    assert isinstance(name, str)
    assert name == "Dai Stablecoin"

def test_invalid_address():
    """Test handling of invalid addresses."""
    invalid_address = "0xinvalid"
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        get_abi(invalid_address)
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        get_balance(invalid_address)
    
    with pytest.raises(ValueError, match="Invalid contract address"):
        call_function(invalid_address, "balanceOf", invalid_address)

def test_nonexistent_function():
    """Test calling non-existent function."""
    with pytest.raises(ValueError, match="Function nonexistent not found in contract"):
        call_function(TEST_CONTRACT, "nonexistent") 