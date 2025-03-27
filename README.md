# EVM CodeAct

A demonstration of how CodeAct can be used to analyze and interact with Ethereum smart contracts using natural language. Built with [langgraph-codeact](https://github.com/langchain-ai/langgraph-codeact), this project showcases how CodeAct's ability to write and analyze code makes it particularly powerful in the Web3 ecosystem.

## About CodeAct

CodeAct is an alternative to JSON function-calling that enables solving complex tasks in fewer steps. It leverages the full power of a Turing complete programming language (Python in this case) to combine and transform outputs from multiple tools. Key features include:

- Persistent message history and Python variables between turns
- Support for custom tools, LangChain tools, and MCP tools
- Streaming token-by-token output
- Customizable system messages
- Flexible code sandbox integration

## Why Web3 is Perfect for CodeAct

Web3 presents an ideal playground for CodeAct because:
- Smart contracts are self-contained, verifiable code
- All contract source code is publicly available
- Contract interactions follow well-defined patterns
- Results are deterministic and verifiable
- The agent can analyze both code and on-chain data

This project demonstrates how CodeAct can:
- Read and analyze smart contract source code
- Understand contract functionality through code inspection
- Generate code to interact with contracts
- Process and analyze transaction data

## Quick Start

1. Install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
uv pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
ALCHEMY_API_KEY="alchemy key"
ETHERSCAN_API_KEY="your_etherscan_api_key"
```

3. Run the agent:
```bash
python src/main.py
```

## Example Queries

- "What does the contract 0xabcd... do?"
- "What is this transaction {0xTxHash} doing?"

## Development

This project serves as a demonstration of CodeAct's capabilities in the Web3 space. It shows how an AI agent can effectively analyze and interact with smart contracts by leveraging its ability to write and understand code.

To run the tests:
```bash
pytest tests/test_evm_tools.py -v
```

## License

MIT 