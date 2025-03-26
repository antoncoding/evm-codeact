from src.main import main

def example_contract_interaction():
    """
    Example of how to use the EVM CodeAct agent to interact with a contract.
    """
    # Example contract address (USDT on Ethereum mainnet)
    contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    
    # Example messages that demonstrate different capabilities
    example_messages = [
        {
            "role": "user",
            "content": f"Get the balance of this contract: {contract_address}"
        },
        {
            "role": "user",
            "content": f"List all available functions in this contract: {contract_address}"
        },
        {
            "role": "user",
            "content": f"Get the ABI of this contract: {contract_address}"
        }
    ]
    
    # Run the agent with example messages
    main()

if __name__ == "__main__":
    example_contract_interaction() 