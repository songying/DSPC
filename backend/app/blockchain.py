from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import json
import os
from typing import Dict, Any, Optional

ETHEREUM_NODE_URL = "https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"  # Sepolia testnet

CONTRACT_ABI = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "datasetId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "dataHash",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "price",
                "type": "uint256"
            }
        ],
        "name": "registerDataset",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "datasetId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "requestId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "computationType",
                "type": "string"
            }
        ],
        "name": "requestComputation",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "requestId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "resultHash",
                "type": "string"
            }
        ],
        "name": "submitComputationResult",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"  # Placeholder

class BlockchainService:
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode
        
        if self.simulation_mode:
            print("Using simulated blockchain for testing")
            self.connected = True
            self.w3 = Web3()  # Create a Web3 instance without a provider for simulation
            self.contract = None
        else:
            try:
                self.w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
                self.contract = self.w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
                self.connected = self.w3.is_connected()
            except Exception as e:
                print(f"Failed to connect to Ethereum node: {e}")
                self.connected = False
                self.w3 = None
                self.contract = None
    
    def is_connected(self) -> bool:
        return self.connected and self.w3 is not None
    
    def create_wallet(self) -> Dict[str, str]:
        """Create a new Ethereum wallet"""
        account = Account.create()
        private_key = account.key.hex()
        address = account.address
        return {"address": address, "private_key": private_key}
    
    def sign_message(self, message: str, private_key: str) -> str:
        """Sign a message with a private key"""
        message_hash = encode_defunct(text=message)
        signed_message = Account.sign_message(message_hash, private_key)
        return signed_message.signature.hex()
    
    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """Verify a signature"""
        if self.simulation_mode:
            print(f"Simulating signature verification for {address}")
            return True
            
        message_hash = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == address.lower()
    
    def register_dataset(self, dataset_id: str, data_hash: str, price: float, owner_address: str, private_key: str) -> Optional[str]:
        """Register a dataset on the blockchain"""
        if not self.is_connected():
            return None
        
        if self.simulation_mode:
            print(f"Simulating dataset registration for {dataset_id}")
            import hashlib
            fake_tx_hash = hashlib.sha256(f"{dataset_id}:{data_hash}:{price}".encode()).hexdigest()
            return "0x" + fake_tx_hash
            
        try:
            price_wei = self.w3.to_wei(price, 'ether')
            
            tx = self.contract.functions.registerDataset(
                dataset_id,
                data_hash,
                price_wei
            ).build_transaction({
                'from': owner_address,
                'nonce': self.w3.eth.get_transaction_count(owner_address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_receipt['transactionHash'].hex()
        except Exception as e:
            print(f"Error registering dataset: {e}")
            return None
    
    def request_computation(self, dataset_id: str, request_id: str, computation_type: str, 
                           requester_address: str, private_key: str, price: float) -> Optional[str]:
        """Request computation on a dataset"""
        if not self.is_connected():
            return None
            
        if self.simulation_mode:
            print(f"Simulating computation request for {dataset_id}")
            import hashlib
            fake_tx_hash = hashlib.sha256(f"{dataset_id}:{request_id}:{computation_type}".encode()).hexdigest()
            return "0x" + fake_tx_hash
        
        try:
            price_wei = self.w3.to_wei(price, 'ether')
            
            tx = self.contract.functions.requestComputation(
                dataset_id,
                request_id,
                computation_type
            ).build_transaction({
                'from': requester_address,
                'nonce': self.w3.eth.get_transaction_count(requester_address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'value': price_wei
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_receipt['transactionHash'].hex()
        except Exception as e:
            print(f"Error requesting computation: {e}")
            return None
    
    def submit_computation_result(self, request_id: str, result_hash: str, 
                                 provider_address: str, private_key: str) -> Optional[str]:
        """Submit computation result"""
        if not self.is_connected():
            return None
            
        if self.simulation_mode:
            print(f"Simulating computation result submission for {request_id}")
            import hashlib
            fake_tx_hash = hashlib.sha256(f"{request_id}:{result_hash}".encode()).hexdigest()
            return "0x" + fake_tx_hash
        
        try:
            tx = self.contract.functions.submitComputationResult(
                request_id,
                result_hash
            ).build_transaction({
                'from': provider_address,
                'nonce': self.w3.eth.get_transaction_count(provider_address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_receipt['transactionHash'].hex()
        except Exception as e:
            print(f"Error submitting computation result: {e}")
            return None

blockchain_service = BlockchainService(simulation_mode=False)
