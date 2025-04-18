import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';

const Home: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <Layout user={user} onLogout={logout}>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Privacy Data Trading Protocol
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            A decentralized protocol for privacy-preserving data trading and computing with Web3 technology.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-indigo-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-indigo-700 mb-2">For Data Providers</h2>
              <p className="text-gray-600 mb-4">
                Securely share your data while maintaining privacy and control. Earn rewards for valuable datasets.
              </p>
              {user ? (
                <Link
                  to="/datasets/create"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Share Your Data
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Get Started
                </Link>
              )}
            </div>
            
            <div className="bg-emerald-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-emerald-700 mb-2">For Data Consumers</h2>
              <p className="text-gray-600 mb-4">
                Access high-quality data and perform computations without compromising data privacy.
              </p>
              {user ? (
                <Link
                  to="/marketplace"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
                >
                  Browse Marketplace
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
                >
                  Get Started
                </Link>
              )}
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white mb-4">
                  1
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Secure Data Sharing</h3>
                <p className="text-gray-600">
                  Data providers encrypt their data and register it on the blockchain with terms of use.
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white mb-4">
                  2
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Privacy-Preserving Computation</h3>
                <p className="text-gray-600">
                  Data consumers request computations on encrypted data using secure multi-party computation.
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white mb-4">
                  3
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Transparent Transactions</h3>
                <p className="text-gray-600">
                  Smart contracts ensure fair payment and compliance with terms of use for all parties.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Home;
