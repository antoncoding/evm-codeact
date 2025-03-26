import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph_codeact import create_codeact
from langgraph.checkpoint.memory import MemorySaver
from tools.evm_tools import EVMTools

# Load environment variables
load_dotenv()

def create_sandbox(code: str, _locals: dict) -> tuple[str, dict]:
    """Simple sandbox for code execution."""
    import builtins
    import contextlib
    import io
    from typing import Any

    # Store original keys before execution
    original_keys = set(_locals.keys())

    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exec(code, builtins.__dict__, _locals)
        result = f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except Exception as e:
        result = f"Error during execution: {repr(e)}"

    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars

def initialize_agent():
    """Initialize the CodeAct agent with EVM tools."""
    # Initialize Web3 provider
    web3_provider_uri = os.getenv("RPC_URL")
    if not web3_provider_uri:
        raise ValueError("RPC_URL environment variable not set")
    
    # Initialize EVM tools
    evm_tools = EVMTools(web3_provider_uri)
    tools = [
        evm_tools.get_contract_abi,
        evm_tools.get_contract_functions,
        evm_tools.call_contract_function,
        evm_tools.get_contract_balance,
    ]

    # Initialize the model
    model = init_chat_model("claude-3-7-sonnet-latest", model_provider="anthropic")

    # Create CodeAct graph
    code_act = create_codeact(model, tools, create_sandbox)
    return code_act.compile(checkpointer=MemorySaver())

def print_welcome():
    """Print welcome message and usage instructions."""
    print("\n=== EVM CodeAct Agent ===")
    print("Ask me anything about Ethereum contracts!")
    print("\nExample queries:")
    print("- Get the balance of contract: 0x1234...")
    print("- List all functions in contract: 0x1234...")
    print("- Get the ABI of contract: 0x1234...")
    print("- Call function 'balanceOf' on contract: 0x1234...")
    print("\nType 'exit' to quit")
    print("=" * 30 + "\n")

def main():
    try:
        # Initialize the agent
        agent = initialize_agent()
        print_welcome()

        # Keep track of conversation history
        messages = []

        while True:
            # Get user input
            user_input = input("\nYour question: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            # Add user message to history
            messages.append({
                "role": "user",
                "content": user_input
            })

            # Process the message and stream the response
            print("\nAgent's response:")
            for typ, chunk in agent.stream(
                {"messages": messages},
                stream_mode=["values", "messages"],
                config={"configurable": {"thread_id": 1}},
            ):
                if typ == "messages":
                    print(chunk[0].content, end="")
                elif typ == "values":
                    print("\n\n---answer---\n\n", chunk)

            # Add assistant's response to history
            messages.append({
                "role": "assistant",
                "content": chunk if typ == "values" else chunk[0].content
            })

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please make sure your RPC_URL environment variable is set correctly.")

if __name__ == "__main__":
    main() 