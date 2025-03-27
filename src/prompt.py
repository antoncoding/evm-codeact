

ADDITIONAL_PROMPT = """

You can use the python library web3.py to read and write to the blockchain.

A couple of hints for using web3.py
- Get current block number: web3.eth.block_number, you can later use get_block() to get info like timestamp
- Always use the checksum address

When it comes to replying and logging:
- Pay attention to decimal of each token. If a token balance is 800000018 with decimals = 6, show balance of 80.0000018
- Don't guess what a contract does based on its address, try query source code for contract name, or check ERC20 info to be sure.
- Read the contract code to understand the big picture of called functions. 
  - For example: Having 2 tokens transfers events does not mean it's a swap, could be minting a share token.
  

"""