import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { ComputationRequest, ComputationResult } from '../types';
import { getComputationRequest, getComputationResult } from '../services/api';
import { crypto_service } from '../services/crypto';

const ComputationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, logout } = useAuth();
  
  const [computation, setComputation] = useState<ComputationRequest | null>(null);
  const [result, setResult] = useState<ComputationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [decryptedResult, setDecryptedResult] = useState<string | null>(null);
  const [decryptionKey, setDecryptionKey] = useState<string>('');
  
  useEffect(() => {
    const fetchComputation = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const computationData = await getComputationRequest(id);
        setComputation(computationData);
        
        if (computationData.status === 'completed' && computationData.result_hash) {
          try {
            const resultData = await getComputationResult(id);
            setResult(resultData);
          } catch (resultErr) {
            console.error('Error fetching computation result:', resultErr);
          }
        }
        
        setError(null);
      } catch (err: any) {
        setError('Failed to load computation details. Please try again later.');
        console.error('Error fetching computation:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchComputation();
    
    let interval: any;
    if (computation && (computation.status === 'pending' || computation.status === 'processing')) {
      interval = setInterval(fetchComputation, 10000); // Poll every 10 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [id, computation?.status]);
  
  const handleDecrypt = () => {
    if (!result || !decryptionKey) return;
    
    try {
      const decrypted = crypto_service.decryptData(result.encrypted_result, decryptionKey);
      setDecryptedResult(decrypted);
    } catch (err) {
      setError('Failed to decrypt result. Please check your decryption key.');
      console.error('Error decrypting result:', err);
    }
  };
  
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  if (loading) {
    return (
      <Layout user={user} onLogout={logout}>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      </Layout>
    );
  }
  
  if (error || !computation) {
    return (
      <Layout user={user} onLogout={logout}>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error || 'Computation request not found'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6">
            <Link
              to="/my-computations"
              className="text-indigo-600 hover:text-indigo-900"
            >
              Back to My Computations
            </Link>
          </div>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout user={user} onLogout={logout}>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Computation Request</h1>
            
            <div className="mt-4 md:mt-0">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(computation.status)}`}>
                {computation.status}
              </span>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-4">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Computation ID</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">{computation.id}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Dataset ID</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">
                  <Link
                    to={`/datasets/${computation.dataset_id}`}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    {computation.dataset_id}
                  </Link>
                </dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Computation Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{computation.computation_type}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(computation.created_at).toLocaleString()}
                </dd>
              </div>
              
              {computation.transaction_hash && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Transaction Hash</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-mono break-all">
                    <a
                      href={`https://etherscan.io/tx/${computation.transaction_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      {computation.transaction_hash}
                    </a>
                  </dd>
                </div>
              )}
              
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Algorithm Details</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <pre className="bg-gray-50 p-4 rounded-md overflow-auto max-h-60 font-mono text-xs">
                    {JSON.stringify(computation.algorithm_details, null, 2)}
                  </pre>
                </dd>
              </div>
            </dl>
          </div>
          
          {computation.status === 'completed' && result && (
            <div className="mt-8 border-t border-gray-200 pt-6">
              <h2 className="text-lg font-medium text-gray-900">Computation Result</h2>
              
              {!decryptedResult ? (
                <div className="mt-4">
                  <p className="text-sm text-gray-500 mb-4">
                    Enter your decryption key to view the result.
                  </p>
                  
                  <div className="flex space-x-4">
                    <input
                      type="text"
                      value={decryptionKey}
                      onChange={(e) => setDecryptionKey(e.target.value)}
                      placeholder="Enter decryption key"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                    <button
                      onClick={handleDecrypt}
                      className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      Decrypt
                    </button>
                  </div>
                  
                  <div className="mt-4">
                    <dt className="text-sm font-medium text-gray-500">Result Hash</dt>
                    <dd className="mt-1 text-sm text-gray-900 font-mono break-all">
                      {result.result_hash}
                    </dd>
                  </div>
                </div>
              ) : (
                <div className="mt-4">
                  <dt className="text-sm font-medium text-gray-500">Decrypted Result</dt>
                  <dd className="mt-1">
                    <pre className="bg-gray-50 p-4 rounded-md overflow-auto max-h-60 font-mono text-xs">
                      {decryptedResult}
                    </pre>
                  </dd>
                </div>
              )}
            </div>
          )}
          
          {(computation.status === 'pending' || computation.status === 'processing') && (
            <div className="mt-8 border-t border-gray-200 pt-6">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mr-3"></div>
                <p className="text-gray-500">
                  {computation.status === 'pending' ? 'Waiting for processing...' : 'Processing computation...'}
                </p>
              </div>
              <p className="mt-2 text-sm text-gray-500 text-center">
                This page will automatically update when the computation is complete.
              </p>
            </div>
          )}
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-start">
              <Link
                to="/my-computations"
                className="text-indigo-600 hover:text-indigo-900"
              >
                Back to My Computations
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ComputationDetail;
