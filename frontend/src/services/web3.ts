import Web3 from 'web3';
import detectEthereumProvider from '@metamask/detect-provider';

/**
 * Web3 Service for MetaMask integration
 * 
 * This service provides functions for connecting to MetaMask,
 * signing messages, and interacting with Ethereum.
 */

class Web3Service {
  private web3: Web3 | null = null;
  private provider: any = null;
  private networkId: string | null = null;
  private accounts: string[] = [];

  /**
   * Initialize the Web3 service
   * @returns Promise that resolves when the service is initialized
   */
  async init(): Promise<boolean> {
    try {
      console.log('Initializing Web3Service...');
      
      if (typeof window !== 'undefined' && window.ethereum) {
        console.log('MetaMask detected in window.ethereum');
        this.provider = window.ethereum;
      } else {
        console.log('Using detectEthereumProvider...');
        this.provider = await detectEthereumProvider();
      }
      
      if (this.provider) {
        console.log('Provider found:', this.provider);
        this.web3 = new Web3(this.provider as any);
        
        try {
          const networkId = await this.web3.eth.net.getId();
          this.networkId = networkId.toString();
          console.log('Current network ID:', this.networkId);
          
          if (this.networkId !== '11155111') {
            console.log('Not on Sepolia testnet, attempting to switch...');
            await this.switchNetwork('11155111');
          }
        } catch (networkError) {
          console.error('Error getting network ID:', networkError);
        }
        
        return true;
      } else {
        console.error('Please install MetaMask!');
        return false;
      }
    } catch (error) {
      console.error('Error initializing Web3:', error);
      return false;
    }
  }

  /**
   * Connect to MetaMask
   * @returns Promise that resolves to the connected account address
   */
  async connect(): Promise<string | null> {
    console.log('Connecting to MetaMask...');
    
    if (!this.provider) {
      console.log('Provider not initialized, initializing...');
      const initialized = await this.init();
      if (!initialized) {
        console.error('Failed to initialize provider');
        throw new Error('MetaMask not installed or detected');
      }
    }

    try {
      console.log('Requesting accounts...');
      this.accounts = await this.provider.request({ method: 'eth_requestAccounts' });
      console.log('Accounts received:', this.accounts);
      
      if (this.accounts.length > 0) {
        if (this.networkId !== '11155111') {
          console.log('Switching to Sepolia testnet...');
          await this.switchNetwork('11155111');
        }
        
        return this.accounts[0];
      }
      
      throw new Error('No accounts found in MetaMask');
    } catch (error: any) {
      console.error('Error connecting to MetaMask:', error);
      
      if (error.code === -32002) {
        console.log('MetaMask request already pending, returning special error');
        throw {
          code: -32002,
          message: 'MetaMask request already pending. Please check your MetaMask extension and approve the connection request.'
        };
      }
      
      if (error.code === 4001) {
        throw new Error('MetaMask connection rejected by user');
      }
      
      throw new Error('Failed to connect to MetaMask');
    }
  }

  /**
   * Get the current account
   * @returns The current account address
   */
  getCurrentAccount(): string | null {
    return this.accounts.length > 0 ? this.accounts[0] : null;
  }

  /**
   * Get the current network ID
   * @returns The current network ID
   */
  getNetworkId(): string | null {
    return this.networkId;
  }

  /**
   * Get the network name based on the network ID
   * @returns The network name
   */
  getNetworkName(): string {
    if (!this.networkId) return 'Unknown';
    
    switch (this.networkId) {
      case '1':
        return 'Ethereum Mainnet';
      case '5':
        return 'Goerli Testnet';
      case '11155111':
        return 'Sepolia Testnet';
      default:
        return `Unknown Network (${this.networkId})`;
    }
  }

  /**
   * Sign a message with the current account
   * @param message The message to sign
   * @returns Promise that resolves to the signature
   */
  async signMessage(message: string): Promise<string | null> {
    if (!this.web3 || !this.accounts.length) {
      console.error('Cannot sign message: Web3 or accounts not initialized');
      return null;
    }
    
    try {
      console.log('Signing message:', message);
      
      const signature = await this.web3.eth.personal.sign(
        message,
        this.accounts[0],
        '' // Password (not needed for MetaMask)
      );
      
      console.log('Message signed successfully');
      return signature;
    } catch (error) {
      console.error('Error signing message:', error);
      return null;
    }
  }

  /**
   * Verify a signature
   * @param message The original message
   * @param signature The signature to verify
   * @param address The address that signed the message
   * @returns Whether the signature is valid
   */
  async verifySignature(message: string, signature: string, address: string): Promise<boolean> {
    try {
      console.log('Verifying signature for message:', message);
      
      const messageHash = this.web3?.utils.sha3(message);
      if (!messageHash) {
        console.error('Failed to create message hash');
        return false;
      }
      
      const recoveredAddress = this.web3?.eth.accounts.recover(message, signature);
      if (!recoveredAddress) {
        console.error('Failed to recover address from signature');
        return false;
      }
      
      console.log('Recovered address:', recoveredAddress);
      console.log('Expected address:', address);
      
      return recoveredAddress.toLowerCase() === address.toLowerCase();
    } catch (error) {
      console.error('Error verifying signature:', error);
      return false;
    }
  }

  /**
   * Switch to a specific Ethereum network
   * @param networkId The network ID to switch to
   * @returns Promise that resolves when the network is switched
   */
  async switchNetwork(networkId: string): Promise<boolean> {
    if (!this.provider) {
      console.error('Cannot switch network: Provider not initialized');
      return false;
    }
    
    try {
      console.log('Switching to network ID:', networkId);
      const networkIdHex = `0x${parseInt(networkId).toString(16)}`;
      
      await this.provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: networkIdHex }],
      });
      
      this.networkId = networkId;
      console.log('Network switched successfully');
      
      return true;
    } catch (error: any) {
      if (error.code === 4902) {
        console.log('Network not configured in MetaMask, adding it...');
        return await this.addNetwork(networkId);
      }
      
      console.error('Error switching network:', error);
      return false;
    }
  }

  /**
   * Add a network to MetaMask
   * @param networkId The network ID to add
   * @returns Promise that resolves when the network is added
   */
  async addNetwork(networkId: string): Promise<boolean> {
    if (!this.provider) {
      console.error('Cannot add network: Provider not initialized');
      return false;
    }
    
    try {
      console.log('Adding network ID:', networkId);
      const networkParams = this.getNetworkParams(networkId);
      
      if (!networkParams) {
        console.error('Unknown network ID:', networkId);
        return false;
      }
      
      await this.provider.request({
        method: 'wallet_addEthereumChain',
        params: [networkParams],
      });
      
      this.networkId = networkId;
      console.log('Network added successfully');
      
      return true;
    } catch (error) {
      console.error('Error adding network:', error);
      return false;
    }
  }

  /**
   * Get network parameters for adding a network to MetaMask
   * @param networkId The network ID
   * @returns The network parameters
   */
  private getNetworkParams(networkId: string): any {
    const networkIdHex = `0x${parseInt(networkId).toString(16)}`;
    
    switch (networkId) {
      case '11155111': // Sepolia
        return {
          chainId: networkIdHex,
          chainName: 'Sepolia Testnet',
          nativeCurrency: {
            name: 'Sepolia ETH',
            symbol: 'ETH',
            decimals: 18,
          },
          rpcUrls: ['https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'],
          blockExplorerUrls: ['https://sepolia.etherscan.io'],
        };
      default:
        return null;
    }
  }

  /**
   * Check if MetaMask is installed
   * @returns Whether MetaMask is installed
   */
  isMetaMaskInstalled(): boolean {
    return !!this.provider;
  }
}

const web3Service = new Web3Service();
export { web3Service };
