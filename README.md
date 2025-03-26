# EVM CodeAct

An AI agent that can interact with Ethereum smart contracts using natural language. Built with [langgraph-codeact](https://github.com/langchain-ai/langgraph-codeact), implementing the CodeAct architecture.

## About CodeAct

CodeAct is an alternative to JSON function-calling that enables solving complex tasks in fewer steps. It leverages the full power of a Turing complete programming language (Python in this case) to combine and transform outputs from multiple tools. Key features include:

- Persistent message history and Python variables between turns
- Support for custom tools, LangChain tools, and MCP tools
- Streaming token-by-token output
- Customizable system messages
- Flexible code sandbox integration

## Quick Start

1. Install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
uv pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
RPC_URL="your_ethereum_node_url"
ETHERSCAN_API_KEY="your_etherscan_api_key"
```

3. Run the agent:
```bash
python src/main.py
```

## Example Queries

- "What does the contract 0xabcd... do?"
- "Is this contract 0xabcd... still frequently used?"
- "My address is {}, how to i withdraw from contract {}"

## Development

This is a proof-of-concept project. Contributions are welcome!

## License

MIT 