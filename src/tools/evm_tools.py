from typing import Any, Dict, List, Optional, Union
from web3 import Web3
from langchain_core.tools import tool
import os
import requests
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

# Initialize Web3 client
RPC_URL = os.getenv("RPC_URL")
if not RPC_URL:
    raise ValueError("RPC_URL environment variable not set")

web3_client = Web3(Web3.HTTPProvider(RPC_URL))

def get_abi(contract_address: str) -> Dict[str, Any]:
    """Get the ABI of a contract from Basescan."""
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        raise ValueError("ETHERSCAN_API_KEY environment variable not set")
    
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Call Basescan API
    url = "https://api.basescan.org/api"
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": api_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ABI: {response.text}")
    
    data = response.json()

    if data["status"] != "1":
        raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
    
    # Parse the ABI string into a Python object
    try:
        abi = json.loads(data["result"])
        return abi
    except Exception as e:
        raise Exception(f"Failed to parse ABI: {str(e)}")

def call_function(contract_address: str, function_name: str, *args, is_read: bool = True) -> Union[Any, str]:
    """
    Call a contract function with given arguments.
    
    Args:
        contract_address: The address of the contract
        function_name: Name of the function to call
        *args: Arguments to pass to the function
        is_read: If True, performs a read operation (call). If False, performs a write operation (transact)
    
    Returns:
        For read operations: The function's return value (converted to string if it's a large number)
        For write operations: The transaction hash
    """
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Get contract ABI
    abi = get_abi(contract_address)
    
    # Create contract instance
    contract = web3_client.eth.contract(address=contract_address, abi=abi)
    
    # Get the function
    if not hasattr(contract.functions, function_name):
        raise ValueError(f"Function {function_name} not found in contract")
    
    function = getattr(contract.functions, function_name)
    
    try:
        if is_read:
            # Read operation (call)
            result = function(*args).call()
            # Convert large numbers to string
            if isinstance(result, (int, float)) and result > 2**63 - 1:
                return str(result)
            return result
        else:
            # Write operation (transact)
            # Note: For write operations, you'll need to handle private key and gas settings
            # This is a basic implementation
            tx_hash = function(*args).transact()
            return web3_client.to_hex(tx_hash)
    except Exception as e:
        raise Exception(f"Failed to call function {function_name}: {str(e)}")


def get_events(contract_address: str, event_name: str, from_block: Optional[int] = None, to_block: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get events emitted by a contract.
    
    Args:
        contract_address: The address of the contract
        event_name: Name of the event to search for
        from_block: Starting block number (optional)
        to_block: Ending block number (optional)
    
    Returns:
        List of event logs
    """

    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Get contract ABI
    abi = get_abi(contract_address)
    
    # Create contract instance
    contract = web3_client.eth.contract(address=contract_address, abi=abi)
    
    # Get the event
    if not hasattr(contract.events, event_name):
        raise ValueError(f"Event {event_name} not found in contract")
    
    event = getattr(contract.events, event_name)
    
    try:
        # Get events
        events = event.get_logs(from_block=from_block, to_block=to_block)
        return [dict(event) for event in events]
    except Exception as e:
        raise Exception(f"Failed to get events: {str(e)}")

def get_transaction_receipt(tx_hash: str) -> Dict[str, Any]:
    """
    Get the receipt of a transaction.
    
    Args:
        tx_hash: The transaction hash
    
    Returns:
        Transaction receipt as a dictionary
    """
    try:
        # Convert hex string to bytes if needed
        if isinstance(tx_hash, str):
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            tx_hash = web3_client.to_bytes(hexstr=tx_hash)
        
        receipt = web3_client.eth.get_transaction_receipt(tx_hash)
        return dict(receipt)
    except Exception as e:
        raise Exception(f"Failed to get transaction receipt: {str(e)}")

# Tool wrappers
@tool
def get_contract_abi_tool(contract_address: str) -> Dict[str, Any]:
    """Tool wrapper for getting contract ABI."""
    return get_abi(contract_address)

@tool
def call_contract_function_tool(contract_address: str, function_name: str, *args, is_read: bool = True) -> Union[Any, str]:
    """Tool wrapper for calling contract functions."""
    return call_function(contract_address, function_name, *args, is_read=is_read)

@tool
def get_contract_events_tool(contract_address: str, event_name: str, from_block: Optional[int] = None, to_block: Optional[int] = None) -> List[Dict[str, Any]]:
    """Tool wrapper for getting contract events."""
    return get_events(contract_address, event_name, from_block, to_block)

@tool
def get_transaction_receipt_tool(tx_hash: str) -> Dict[str, Any]:
    """Tool wrapper for getting transaction receipt."""
    return get_transaction_receipt(tx_hash) 