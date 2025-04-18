import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { User } from '../types';
import { login as apiLogin, register as apiRegister, getCurrentUser, loginWithWallet, updateWalletAddress } from '../services/api';
import { web3Service } from '../services/web3';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  walletAddress: string | null;
  isMetaMaskInstalled: boolean;
  networkName: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  connectWallet: () => Promise<string | null>;
  loginWithMetaMask: () => Promise<void>;
  switchNetwork: (networkId: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [isMetaMaskInstalled, setIsMetaMaskInstalled] = useState<boolean>(false);
  const [networkName, setNetworkName] = useState<string | null>(null);

  useEffect(() => {
    const initWeb3 = async () => {
      const initialized = await web3Service.init();
      setIsMetaMaskInstalled(initialized);
      
      if (initialized) {
        const networkId = web3Service.getNetworkId();
        if (networkId) {
          setNetworkName(web3Service.getNetworkName());
        }
        
        const savedWalletAddress = localStorage.getItem('walletAddress');
        if (savedWalletAddress) {
          setWalletAddress(savedWalletAddress);
        }
      }
    };
    
    initWeb3();
  }, []);

  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
          
          if (userData.wallet_address) {
            setWalletAddress(userData.wallet_address);
          }
        } catch (err) {
          console.error('Failed to load user:', err);
          setToken(null);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  const login = async (username: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiLogin(username, password);
      setToken(response.access_token);
      localStorage.setItem('token', response.access_token);
      const userData = await getCurrentUser();
      setUser(userData);
      
      if (userData.wallet_address) {
        setWalletAddress(userData.wallet_address);
        localStorage.setItem('walletAddress', userData.wallet_address);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      await apiRegister(username, email, password);
      await login(username, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setWalletAddress(null);
    localStorage.removeItem('token');
    localStorage.removeItem('walletAddress');
  };

  const connectWallet = async (): Promise<string | null> => {
    try {
      setLoading(true);
      setError(null);
      
      const address = await web3Service.connect();
      
      if (address) {
        setWalletAddress(address);
        localStorage.setItem('walletAddress', address);
        
        if (user && token) {
          await updateWalletAddress(address);
          
          const userData = await getCurrentUser();
          setUser(userData);
        }
        
        const networkId = web3Service.getNetworkId();
        if (networkId) {
          setNetworkName(web3Service.getNetworkName());
        }
        
        return address;
      }
      
      return null;
    } catch (err: any) {
      if (err.code === -32002) {
        setError('MetaMask request already pending. Please check your MetaMask extension.');
      } else {
        setError(err.message || 'Failed to connect wallet');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loginWithMetaMask = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const address = await connectWallet();
      
      if (!address) {
        throw new Error('Failed to connect to MetaMask');
      }
      
      const message = `Sign this message to authenticate with Privacy Data Protocol: ${Date.now()}`;
      const signature = await web3Service.signMessage(message);
      
      if (!signature) {
        throw new Error('Failed to sign authentication message');
      }
      
      const response = await loginWithWallet(address, message, signature);
      
      setToken(response.access_token);
      localStorage.setItem('token', response.access_token);
      
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      setError(err.message || 'MetaMask login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const switchNetwork = async (networkId: string): Promise<boolean> => {
    try {
      const success = await web3Service.switchNetwork(networkId);
      
      if (success) {
        setNetworkName(web3Service.getNetworkName());
      }
      
      return success;
    } catch (err) {
      console.error('Failed to switch network:', err);
      return false;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        walletAddress,
        isMetaMaskInstalled,
        networkName,
        login,
        register,
        logout,
        connectWallet,
        loginWithMetaMask,
        switchNetwork,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
