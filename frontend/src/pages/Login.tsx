import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMetaMaskLoading, setIsMetaMaskLoading] = useState(false);
  const [pendingMetaMaskRequest, setPendingMetaMaskRequest] = useState(false);
  
  const { login, loginWithMetaMask, isMetaMaskInstalled } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (pendingMetaMaskRequest) {
      timer = setTimeout(() => {
        setPendingMetaMaskRequest(false);
        setError(null);
      }, 5000);
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [pendingMetaMaskRequest]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    try {
      await login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleMetaMaskLogin = async () => {
    if (pendingMetaMaskRequest) {
      window.open('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html');
      return;
    }
    
    setError(null);
    setIsMetaMaskLoading(true);
    
    try {
      await loginWithMetaMask();
      navigate('/');
    } catch (err: any) {
      console.error('MetaMask login error:', err);
      
      if (err.code === -32002) {
        setPendingMetaMaskRequest(true);
        setError('MetaMask request already pending. Please check your MetaMask extension and approve the connection request.');
      } else {
        setError(err.message || 'MetaMask login failed. Please try again.');
      }
    } finally {
      setIsMetaMaskLoading(false);
    }
  };
  
  const handleTestUserLogin = async () => {
    setError(null);
    setIsLoading(true);
    
    try {
      await login('testuser', 'password');
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Test user login failed.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Layout user={null} onLogout={() => {}}>
      <div className="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              create a new account
            </Link>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>{error}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* MetaMask Login Button */}
            {isMetaMaskInstalled ? (
              <div className="mb-6">
                <button
                  type="button"
                  onClick={handleMetaMaskLogin}
                  disabled={isMetaMaskLoading}
                  className={`flex w-full justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                    pendingMetaMaskRequest 
                      ? 'bg-blue-500 hover:bg-blue-600 focus:ring-blue-500' 
                      : 'bg-orange-500 hover:bg-orange-600 focus:ring-orange-500'
                  } ${
                    isMetaMaskLoading ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {isMetaMaskLoading ? (
                    'Connecting to MetaMask...'
                  ) : pendingMetaMaskRequest ? (
                    'Check MetaMask Extension'
                  ) : (
                    <div className="flex items-center">
                      <img 
                        src="/metamask-fox.svg" 
                        alt="MetaMask" 
                        className="h-5 w-5 mr-2" 
                      />
                      Sign in with MetaMask
                    </div>
                  )}
                </button>
              </div>
            ) : (
              <div className="mb-6 p-4 bg-yellow-50 rounded-md">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">MetaMask not detected</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>Please install the MetaMask extension to use Web3 login.</p>
                      <a 
                        href="https://metamask.io/download/" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="font-medium text-yellow-700 underline hover:text-yellow-600"
                      >
                        Download MetaMask
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-gray-500">Or continue with</span>
              </div>
            </div>
            
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  Username
                </label>
                <div className="mt-1">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                    isLoading ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {isLoading ? 'Signing in...' : 'Sign in'}
                </button>
              </div>
              
              <div>
                <button
                  type="button"
                  onClick={handleTestUserLogin}
                  disabled={isLoading}
                  className="flex w-full justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Sign in as Test User
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Login;
