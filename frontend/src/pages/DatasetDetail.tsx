import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { Dataset, ComputationType } from '../types';
import { getDataset, requestComputation } from '../services/api';

const DatasetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [computationType, setComputationType] = useState<ComputationType>(ComputationType.ANALYSIS);
  const [algorithmDetails, setAlgorithmDetails] = useState<string>('{}');
  const [requestLoading, setRequestLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchDataset = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await getDataset(id);
        setDataset(data);
        setError(null);
      } catch (err: any) {
        setError('Failed to load dataset details. Please try again later.');
        console.error('Error fetching dataset:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDataset();
  }, [id]);
  
  const handleRequestComputation = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!id || !user) return;
    
    try {
      setRequestLoading(true);
      setRequestError(null);
      
      let parsedAlgorithmDetails;
      try {
        parsedAlgorithmDetails = JSON.parse(algorithmDetails);
      } catch (err) {
        setRequestError('Invalid algorithm details JSON format');
        setRequestLoading(false);
        return;
      }
      
      const response = await requestComputation({
        dataset_id: id,
        computation_type: computationType,
        algorithm_details: parsedAlgorithmDetails,
      });
      
      navigate(`/computations/${response.id}`);
    } catch (err: any) {
      setRequestError(err.response?.data?.detail || 'Failed to request computation. Please try again.');
      console.error('Error requesting computation:', err);
    } finally {
      setRequestLoading(false);
    }
  };
  
  const computationTypeOptions = [
    { value: ComputationType.ANALYSIS, label: 'Analysis' },
    { value: ComputationType.MACHINE_LEARNING, label: 'Machine Learning' },
    { value: ComputationType.STATISTICAL, label: 'Statistical' },
    { value: ComputationType.CUSTOM, label: 'Custom' },
  ];
  
  if (loading) {
    return (
      <Layout user={user} onLogout={logout}>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      </Layout>
    );
  }
  
  if (error || !dataset) {
    return (
      <Layout user={user} onLogout={logout}>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error || 'Dataset not found'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6">
            <Link
              to="/marketplace"
              className="text-indigo-600 hover:text-indigo-900"
            >
              Back to Marketplace
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
            <h1 className="text-2xl font-bold text-gray-900">{dataset.name}</h1>
            
            <div className="mt-4 md:mt-0">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                dataset.data_type === 'personal' ? 'bg-blue-100 text-blue-800' :
                dataset.data_type === 'financial' ? 'bg-green-100 text-green-800' :
                dataset.data_type === 'health' ? 'bg-red-100 text-red-800' :
                dataset.data_type === 'behavioral' ? 'bg-purple-100 text-purple-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {dataset.data_type}
              </span>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-4">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900">{dataset.description}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Price</dt>
                <dd className="mt-1 text-sm text-gray-900">{dataset.price} ETH</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(dataset.created_at).toLocaleDateString()}
                </dd>
              </div>
              
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Terms of Use</dt>
                <dd className="mt-1 text-sm text-gray-900 whitespace-pre-line">{dataset.terms_of_use}</dd>
              </div>
              
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Privacy Options</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <div className="flex flex-wrap gap-2">
                    {dataset.supports_homomorphic && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Homomorphic Computing
                      </span>
                    )}
                    {dataset.supports_zk_proof && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ZK Proof
                      </span>
                    )}
                    {dataset.supports_third_party && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        3rd-Party Computing
                      </span>
                    )}
                    {!dataset.supports_homomorphic && !dataset.supports_zk_proof && !dataset.supports_third_party && (
                      <span className="text-gray-500">None specified</span>
                    )}
                  </div>
                </dd>
              </div>
            </dl>
          </div>
          
          {user && user.id !== dataset.owner_id && (
            <div className="mt-8 border-t border-gray-200 pt-6">
              <h2 className="text-lg font-medium text-gray-900">Request Computation</h2>
              <p className="mt-1 text-sm text-gray-500">
                Request a privacy-preserving computation on this dataset.
              </p>
              
              {requestError && (
                <div className="mt-4 rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p>{requestError}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <form onSubmit={handleRequestComputation} className="mt-6 space-y-6">
                <div>
                  <label htmlFor="computationType" className="block text-sm font-medium text-gray-700">
                    Computation Type
                  </label>
                  <div className="mt-1">
                    <select
                      id="computationType"
                      value={computationType}
                      onChange={(e) => setComputationType(e.target.value as ComputationType)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      {computationTypeOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div>
                  <label htmlFor="algorithmDetails" className="block text-sm font-medium text-gray-700">
                    Algorithm Details (JSON)
                  </label>
                  <div className="mt-1">
                    <textarea
                      id="algorithmDetails"
                      rows={5}
                      value={algorithmDetails}
                      onChange={(e) => setAlgorithmDetails(e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm font-mono"
                    />
                  </div>
                  <p className="mt-2 text-sm text-gray-500">
                    Specify the algorithm details in JSON format. This will be processed securely.
                  </p>
                </div>
                
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={requestLoading}
                    className={`inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                      requestLoading ? 'opacity-75 cursor-not-allowed' : ''
                    }`}
                  >
                    {requestLoading ? 'Requesting...' : 'Request Computation'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default DatasetDetail;
