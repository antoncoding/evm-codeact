from typing import Any, Dict, List, Optional, Union
from web3 import Web3
from langchain_core.tools import tool
import os
import requests
from dotenv import load_dotenv
import json
from eth_utils.toolz import assoc
from eth_utils import to_dict
import time
# Load environment variables
load_dotenv()

# Alchemy API configurations
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
if not ALCHEMY_API_KEY:
    raise ValueError("ALCHEMY_API_KEY environment variable not set")

CHAIN_RPC_URLS = {
    1: f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}",  # Mainnet
    8453: f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"  # Base
}

def _get_web3_client(chain_id: int) -> Web3:
    """Get a Web3 client for the specified chain.
    
    Args:
        chain_id: The chain ID of the network
    
    Returns:
        Web3 client instance
    """
    if chain_id not in CHAIN_RPC_URLS:
        raise ValueError(f"Unsupported chain ID: {chain_id}. Supported chains: {list(CHAIN_RPC_URLS.keys())}")
    
    return Web3(Web3.HTTPProvider(CHAIN_RPC_URLS[chain_id]))

def _make_infura_request(chain_id: int,params: Dict[str, str]) -> Dict[str, Any]:
    """Helper function to make requests to Etherscan API.
    
    Args:
        chain_id: The chain ID of the network
        params: Dictionary of parameters to send to the API
    
    Returns:
        API response data as dictionary
    """
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        raise ValueError("ETHERSCAN_API_KEY environment variable not set")
    
    url = f"https://api.etherscan.io/v2/api"
    params["apikey"] = api_key
    params["chainid"] = chain_id
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                raise Exception("Rate limit exceeded. Please try again later.")
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.text}")
            
            data = response.json()
            if data["status"] != "1":
                raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")

def get_abi(contract_address: str, chain_id: int) -> Dict[str, Any]:
    """Get the ABI of a contract from Basescan."""
    web3_client = _get_web3_client(chain_id)
    
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Call Basescan API
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
    }
    
    data = _make_infura_request(chain_id, params)
    
    # Parse the ABI string into a Python object
    try:
        abi = json.loads(data["result"])
        return abi
    except Exception as e:
        raise Exception(f"Failed to parse ABI: {str(e)}")

def get_source_code(contract_address: str, chain_id: int) -> Dict[str, Any]:
    """Get the Source code of a contract from Basescan. Only used when you need to understand the logic"""
    web3_client = _get_web3_client(chain_id)
    
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Call Basescan API
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
    }
    
    data = _make_infura_request(chain_id, params)
    
    # The result is now a list with a single item containing the contract details
    if not data["result"] or not isinstance(data["result"], list):
        raise Exception("No source code found for this contract")
    
    return data["result"][0]

def call_function(contract_address: str, function_name: str, *args, chain_id, is_read: bool = True) -> Union[Any, str]:
    """
    Call a contract function with given arguments.
    
    Args:
        contract_address: The address of the contract
        function_name: Name of the function to call
        *args: Arguments to pass to the function
        chain_id: The chain ID of the network
        is_read: If True, performs a read operation (call). If False, performs a write operation (transact)
    
    Returns:
        For read operations: The function's return value (converted to string if it's a large number)
        For write operations: The transaction hash
    """
    web3_client = _get_web3_client(chain_id)
    
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Get contract ABI
    abi = get_abi(contract_address, chain_id)
    
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

def _convert_to_serializable(obj: Any) -> Any:
    """Convert an object to a serializable format.
    
    Args:
        obj: The object to convert
        
    Returns:
        A serializable version of the object
    """
    # Handle web3's AttributeDict
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'AttributeDict':
        return dict(obj)
    # Handle HexBytes
    elif hasattr(obj, 'hex'):
        return obj.hex()
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_serializable(item) for item in obj]
    return obj

def get_events(contract_address: str, event_name: str, from_block: Optional[int] = None, to_block: Optional[int] = None, chain_id: int = 8453) -> List[Dict[str, Any]]:
    """
    Get events emitted by a contract.
    
    Args:
        contract_address: The address of the contract
        event_name: Name of the event to search for
        from_block: Starting block number (optional)
        to_block: Ending block number (optional)
        chain_id: The chain ID of the network
    Returns:
        List of event logs
    """
    web3_client = _get_web3_client(chain_id)
    
    # Validate contract address
    try:
        contract_address = web3_client.to_checksum_address(contract_address)
    except Exception as e:
        raise ValueError(f"Invalid contract address: {contract_address}")
    
    # Get contract ABI
    abi = get_abi(contract_address, chain_id)
    
    # Create contract instance
    contract = web3_client.eth.contract(address=contract_address, abi=abi)
    
    # Get the event
    if not hasattr(contract.events, event_name):
        raise ValueError(f"Event {event_name} not found in contract")
    
    event = getattr(contract.events, event_name)
    
    try:
        # Get events
        events = event.get_logs(from_block=from_block, to_block=to_block)
        return [_convert_to_serializable(event) for event in events]
    except Exception as e:
        raise Exception(f"Failed to get events: {str(e)}")

def get_transaction_receipt(tx_hash: str, chain_id: int = 8453) -> Dict[str, Any]:
    """
    Get the receipt of a transaction.
    
    Args:
        tx_hash: The transaction hash
    
    Returns:
        Transaction receipt as a dictionary
    """
    web3_client = _get_web3_client(chain_id)
    
    try:
        # Convert hex string to bytes if needed
        if isinstance(tx_hash, str):
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            tx_hash = web3_client.to_bytes(hexstr=tx_hash)
        
        receipt = web3_client.eth.get_transaction_receipt(tx_hash)
        return _convert_to_serializable(receipt)
    except Exception as e:
        raise Exception(f"Failed to get transaction receipt: {str(e)}")

# Tool wrappers
@tool
def get_contract_abi_tool(contract_address: str, chain_id: int) -> Dict[str, Any]:
    """Tool wrapper for getting contract ABI."""
    return get_abi(contract_address, chain_id)

@tool
def call_contract_function_tool(contract_address: str, function_name: str, *args, chain_id: int = 8453, is_read: bool = True) -> Union[Any, str]:
    """Tool wrapper for calling contract functions."""
    return call_function(contract_address, function_name, *args, chain_id=chain_id, is_read=is_read)

@tool
def get_contract_events_tool(contract_address: str, event_name: str, from_block: Optional[int] = None, to_block: Optional[int] = None, chain_id: int = 8453) -> List[Dict[str, Any]]:
    """Tool wrapper for getting contract events."""
    return get_events(contract_address, event_name, from_block, to_block, chain_id=chain_id)

@tool
def get_transaction_receipt_tool(tx_hash: str, chain_id: int) -> Dict[str, Any]:
    """Tool wrapper for getting transaction receipt."""
    return get_transaction_receipt(tx_hash, chain_id)

@tool
def get_source_code_tool(contract_address: str, chain_id: int) -> Dict[str, Any]:
    """Tool wrapper for getting contract source code from Basescan."""
    return get_source_code(contract_address, chain_id) 