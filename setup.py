from setuptools import setup, find_packages

setup(
    name="emv-codeact",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langgraph-codeact>=0.1.0",
        "langchain>=0.1.0",
        "langchain-anthropic>=0.0.1",
        "web3>=6.11.1",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
) 