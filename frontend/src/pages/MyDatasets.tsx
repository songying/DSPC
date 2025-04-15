import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { Dataset } from '../types';
import { getMyDatasets, deleteDataset } from '../services/api';

const MyDatasets: React.FC = () => {
  const { user, logout } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        setLoading(true);
        const data = await getMyDatasets();
        setDatasets(data);
        setError(null);
      } catch (err: any) {
        setError('Failed to load your datasets. Please try again later.');
        console.error('Error fetching datasets:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDatasets();
  }, []);
  
  const handleDelete = async (datasetId: string) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }
    
    try {
      setDeleteLoading(datasetId);
      await deleteDataset(datasetId);
      setDatasets(datasets.filter(dataset => dataset.id !== datasetId));
    } catch (err: any) {
      setError('Failed to delete dataset. Please try again later.');
      console.error('Error deleting dataset:', err);
    } finally {
      setDeleteLoading(null);
    }
  };
  
  return (
    <Layout user={user} onLogout={logout}>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">My Datasets</h1>
            
            <div className="mt-4 md:mt-0">
              <Link
                to="/datasets/create"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Add New Dataset
              </Link>
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
              <p className="text-gray-500 text-lg">You haven't shared any datasets yet.</p>
              <Link
                to="/datasets/create"
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Share Your First Dataset
              </Link>
            </div>
          ) : (
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                      Name
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Type
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Price (ETH)
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created
                    </th>
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {datasets.map((dataset) => (
                    <tr key={dataset.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                        {dataset.name}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {dataset.data_type}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {dataset.price}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          dataset.is_available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {dataset.is_available ? 'Available' : 'Unavailable'}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {new Date(dataset.created_at).toLocaleDateString()}
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <Link
                          to={`/datasets/${dataset.id}`}
                          className="text-indigo-600 hover:text-indigo-900 mr-4"
                        >
                          View
                        </Link>
                        <button
                          onClick={() => handleDelete(dataset.id)}
                          disabled={deleteLoading === dataset.id}
                          className={`text-red-600 hover:text-red-900 ${
                            deleteLoading === dataset.id ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                        >
                          {deleteLoading === dataset.id ? 'Deleting...' : 'Delete'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default MyDatasets;
