import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { Dataset, DataType } from '../types';
import { getDatasets } from '../services/api';

const Marketplace: React.FC = () => {
  const { user, logout } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string>('');
  
  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        setLoading(true);
        const data = await getDatasets(selectedType || undefined);
        setDatasets(data);
        setError(null);
      } catch (err: any) {
        setError('Failed to load datasets. Please try again later.');
        console.error('Error fetching datasets:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDatasets();
  }, [selectedType]);
  
  const dataTypeOptions = [
    { value: '', label: 'All Types' },
    { value: DataType.PERSONAL, label: 'Personal' },
    { value: DataType.FINANCIAL, label: 'Financial' },
    { value: DataType.HEALTH, label: 'Health' },
    { value: DataType.BEHAVIORAL, label: 'Behavioral' },
    { value: DataType.OTHER, label: 'Other' },
  ];
  
  return (
    <Layout user={user} onLogout={logout}>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Data Marketplace</h1>
            
            <div className="mt-4 md:mt-0 flex items-center">
              <label htmlFor="dataType" className="mr-2 text-sm font-medium text-gray-700">
                Filter by:
              </label>
              <select
                id="dataType"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                {dataTypeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {error && (
            <div className="rounded-md bg-red-50 p-4 mb-6">
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
          
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
          ) : datasets.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No datasets available.</p>
              {user && (
                <Link
                  to="/datasets/create"
                  className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Share Your Data
                </Link>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {datasets.map((dataset) => (
                <div
                  key={dataset.id}
                  className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-300"
                >
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        dataset.data_type === DataType.PERSONAL ? 'bg-blue-100 text-blue-800' :
                        dataset.data_type === DataType.FINANCIAL ? 'bg-green-100 text-green-800' :
                        dataset.data_type === DataType.HEALTH ? 'bg-red-100 text-red-800' :
                        dataset.data_type === DataType.BEHAVIORAL ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {dataset.data_type}
                      </span>
                    </div>
                    <h3 className="mt-2 text-lg font-medium text-gray-900">{dataset.name}</h3>
                    <p className="mt-1 text-sm text-gray-500 line-clamp-3">{dataset.description}</p>
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-500">
                        Price: <span className="text-gray-900">{dataset.price} ETH</span>
                      </p>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-4 py-4 sm:px-6">
                    <div className="text-sm">
                      <Link
                        to={`/datasets/${dataset.id}`}
                        className="font-medium text-indigo-600 hover:text-indigo-500"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Marketplace;
