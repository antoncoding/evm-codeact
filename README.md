# EVM CodeAct

A proof-of-concept project demonstrating the use of CodeAct architecture with EVM (Ethereum Virtual Machine) actions. This project allows an AI agent to interact with Ethereum smart contracts by writing and executing Python scripts.

## Features

- Uses CodeAct architecture to enable AI-driven contract interactions
- Supports reading contract functions and their signatures
- Allows executing contract calls through Python scripts
- Built on top of langgraph-codeact
- Integrates with web3.py for Ethereum interactions

## Prerequisites

- Python 3.8+
- An Ethereum node or provider (e.g., Infura, Alchemy)
- Basic understanding of Ethereum smart contracts
- UV package manager (recommended)

## Installation

### Using UV (Recommended)

1. Install UV if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

### Using pip (Alternative)

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## Project Structure

```
emv-codeact/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── evm_tools.py
│   └── main.py
└── examples/
    └── contract_examples.py
```

## Usage

1. Set up your environment variables:
```bash
export RPC_URL="your_ethereum_node_url"
```

2. Run the example:
```bash
python src/main.py
```

## Example Interaction

```python
# Example of how the AI agent will interact with contracts
messages = [{
    "role": "user",
    "content": "Read the balance of this contract: 0x..."
}]
```

## Development

This is a proof-of-concept project. Contributions and improvements are welcome!

## License

MIT 