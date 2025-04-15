"""
Blockchain integration for the Privacy Data Protocol.
This module handles the deployment and interaction with smart contracts on the Ethereum blockchain.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount

ETHEREUM_NODE_URL = os.environ.get("ETHEREUM_NODE_URL", "https://sepolia.infura.io/v3/your-infura-key")
CHAIN_ID = int(os.environ.get("CHAIN_ID", "11155111"))  # Sepolia testnet

w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Required for some testnets

CONTRACT_ABI_PATH = os.path.join(os.path.dirname(__file__), "../../contracts/abi/DatasetContract.json")
with open(CONTRACT_ABI_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)

CONTRACT_BYTECODE_PATH = os.path.join(os.path.dirname(__file__), "../../contracts/bytecode/DatasetContract.bin")
with open(CONTRACT_BYTECODE_PATH, "r") as f:
    CONTRACT_BYTECODE = f.read().strip()

def get_account(private_key: str) -> LocalAccount:
    """
    Get an Ethereum account from a private key
    
    Args:
        private_key: Ethereum private key
        
    Returns:
        Ethereum account
    """
    return Account.from_key(private_key)

def deploy_dataset_contract(
    private_key: str,
    name: str,
    description: str,
    price_eth: float,
    file_index: str,
    privacy_options: List[str],
    record_count: int
) -> Tuple[str, str]:
    """
    Deploy a new dataset contract to the Ethereum blockchain
    
    Args:
        private_key: Ethereum private key of the deployer
        name: Dataset name
        description: Dataset description
        price_eth: Dataset price in ETH
        file_index: Index reference to the file in the filesystem
        privacy_options: List of privacy options for the dataset
        record_count: Number of records in the dataset
        
    Returns:
        Tuple containing (contract_address, transaction_hash)
    """
    account = get_account(private_key)
    
    price_wei = w3.to_wei(price_eth, "ether")
    
    DatasetContract = w3.eth.contract(abi=CONTRACT_ABI, bytecode=CONTRACT_BYTECODE)
    
    construct_txn = DatasetContract.constructor(
        name,
        description,
        price_wei,
        file_index,
        privacy_options,
        record_count
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID
    })
    
    signed_txn = account.sign_transaction(construct_txn)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt.contractAddress, tx_hash.hex()

def get_dataset_info(contract_address: str) -> Dict[str, Any]:
    """
    Get dataset information from a contract
    
    Args:
        contract_address: Ethereum contract address
        
    Returns:
        Dictionary containing dataset information
    """
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    
    owner, name, description, price_wei, file_index, record_count, created_at = contract.functions.getDatasetInfo().call()
    
    privacy_options = contract.functions.getPrivacyOptions().call()
    
    price_eth = w3.from_wei(price_wei, "ether")
    
    return {
        "owner": owner,
        "name": name,
        "description": description,
        "price": float(price_eth),
        "file_index": file_index,
        "privacy_options": privacy_options,
        "record_count": record_count,
        "created_at": created_at
    }

def update_dataset_price(private_key: str, contract_address: str, new_price_eth: float) -> str:
    """
    Update the price of a dataset
    
    Args:
        private_key: Ethereum private key of the owner
        contract_address: Ethereum contract address
        new_price_eth: New price in ETH
        
    Returns:
        Transaction hash
    """
    account = get_account(private_key)
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    
    new_price_wei = w3.to_wei(new_price_eth, "ether")
    
    txn = contract.functions.updatePrice(new_price_wei).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID
    })
    
    signed_txn = account.sign_transaction(txn)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()

def update_privacy_options(private_key: str, contract_address: str, new_privacy_options: List[str]) -> str:
    """
    Update privacy options for a dataset
    
    Args:
        private_key: Ethereum private key of the owner
        contract_address: Ethereum contract address
        new_privacy_options: New list of privacy options
        
    Returns:
        Transaction hash
    """
    account = get_account(private_key)
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    
    txn = contract.functions.updatePrivacyOptions(new_privacy_options).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID
    })
    
    signed_txn = account.sign_transaction(txn)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()

def is_contract_owner(contract_address: str, wallet_address: str) -> bool:
    """
    Check if a wallet address is the owner of a contract
    
    Args:
        contract_address: Ethereum contract address
        wallet_address: Ethereum wallet address
        
    Returns:
        True if the wallet address is the owner, False otherwise
    """
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    owner = contract.functions.owner().call()
    return owner.lower() == wallet_address.lower()
