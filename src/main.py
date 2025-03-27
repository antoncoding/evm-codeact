import os
import signal
import sys
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph_codeact import create_codeact
from langgraph.checkpoint.memory import MemorySaver
from tools.evm_tools import (
    get_contract_abi_tool,
    call_contract_function_tool,
    get_contract_balance_tool,
    get_contract_events_tool,
    get_transaction_receipt_tool
)
from sandbox import eval_in_sandbox

# Load environment variables
load_dotenv()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nGoodbye! 👋")
    sys.exit(0)

def initialize_agent():
    """Initialize the CodeAct agent with EVM tools."""
    # Initialize the model
    model = init_chat_model("claude-3-7-sonnet-latest", model_provider="anthropic")

    # Create CodeAct graph with tools
    code_act = create_codeact(model, [
        get_contract_abi_tool,
        call_contract_function_tool,
        get_contract_balance_tool,
        get_contract_events_tool,
        get_transaction_receipt_tool
    ], eval_in_sandbox)
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
    print("\nType 'exit' to quit or press Ctrl+C to force quit")
    print("=" * 30 + "\n")

def format_message(content: str, role: str) -> str:
    """Format a message with appropriate icon and styling."""
    icon = "👤" if role == "user" else "🤖"
    return f"{icon} {content}"

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize the agent
        agent = initialize_agent()
        print_welcome()

        # Keep track of conversation history
        messages = []

        while True:
            try:
                # Get user input
                user_input = input("\n👤 ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye! 👋")
                    break

                if not user_input:
                    continue

                # Add user message to history
                messages.append({
                    "role": "user",
                    "content": user_input
                })

                # Process the message and stream the response
                print("\n🤖 ", end="")
                last_content = ""
                
                for typ, chunk in agent.stream(
                    {"messages": messages},
                    stream_mode=["values", "messages"],
                    config={"configurable": {"thread_id": 1}},
                ):
                    if typ == "messages":
                        content = chunk[0].content
                        if content != last_content:
                            print(content, end="")
                            last_content = content
                    elif typ == "values":
                        # Only print the actual content, not the full response object
                        if isinstance(chunk, dict) and 'messages' in chunk:
                            last_message = chunk['messages'][-1]
                            if hasattr(last_message, 'content'):
                                print(last_message.content, end="")
                                last_content = last_message.content

                print()  # New line after response

                # Add assistant's response to history
                messages.append({
                    "role": "assistant",
                    "content": last_content
                })

            except KeyboardInterrupt:
                # Handle Ctrl+C during input or processing
                print("\n\nGoodbye! 👋")
                break

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please make sure your RPC_URL and ETHERSCAN_API_KEY environment variables are set correctly.")
        sys.exit(1)

if __name__ == "__main__":
    main() 