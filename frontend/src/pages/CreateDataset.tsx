import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { DataType } from '../types';
import { createDataset } from '../services/api';
import { crypto_service } from '../services/crypto';

const CreateDataset: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [dataType, setDataType] = useState<DataType>(DataType.PERSONAL);
  const [price, setPrice] = useState('0.1');
  const [termsOfUse, setTermsOfUse] = useState('');
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [supportsHomomorphic, setSupportsHomomorphic] = useState(false);
  const [supportsZkProof, setSupportsZkProof] = useState(false);
  const [supportsThirdParty, setSupportsThirdParty] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const dataTypeOptions = [
    { value: DataType.PERSONAL, label: 'Personal' },
    { value: DataType.FINANCIAL, label: 'Financial' },
    { value: DataType.HEALTH, label: 'Health' },
    { value: DataType.BEHAVIORAL, label: 'Behavioral' },
    { value: DataType.OTHER, label: 'Other' },
  ];
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setDataFile(e.target.files[0]);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!dataFile) {
      setError('Please select a data file to upload');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const encryptionKey = crypto_service.generateKey();
      
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      formData.append('data_type', dataType);
      formData.append('price', price);
      formData.append('terms_of_use', termsOfUse);
      formData.append('supports_homomorphic', supportsHomomorphic.toString());
      formData.append('supports_zk_proof', supportsZkProof.toString());
      formData.append('supports_third_party', supportsThirdParty.toString());
      
      formData.append('file_name', dataFile.name);
      formData.append('file_type', dataFile.type);
      formData.append('file_size', dataFile.size.toString());
      
      formData.append('file', dataFile);
      
      formData.append('encryption_key', encryptionKey);
      
      const createdDataset = await createDataset(formData);
      
      navigate(`/datasets/${createdDataset.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create dataset. Please try again.');
      console.error('Error creating dataset:', err);
    } finally {
      setLoading(false);
    }
  };
  
  
  return (
    <Layout user={user} onLogout={logout}>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Create New Dataset</h1>
          
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
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Dataset Name
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <div className="mt-1">
                <textarea
                  id="description"
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Briefly describe your dataset, its contents, and potential use cases.
              </p>
            </div>
            
            <div>
              <label htmlFor="dataType" className="block text-sm font-medium text-gray-700">
                Data Type
              </label>
              <div className="mt-1">
                <select
                  id="dataType"
                  value={dataType}
                  onChange={(e) => setDataType(e.target.value as DataType)}
                  required
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  {dataTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                Price (ETH)
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  id="price"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                  min="0"
                  step="0.01"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="termsOfUse" className="block text-sm font-medium text-gray-700">
                Terms of Use
              </label>
              <div className="mt-1">
                <textarea
                  id="termsOfUse"
                  rows={3}
                  value={termsOfUse}
                  onChange={(e) => setTermsOfUse(e.target.value)}
                  required
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Specify how your data can be used, any restrictions, and attribution requirements.
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Privacy Options
              </label>
              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    id="homomorphic"
                    type="checkbox"
                    checked={supportsHomomorphic}
                    onChange={(e) => setSupportsHomomorphic(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="homomorphic" className="ml-2 text-sm text-gray-700">
                    Homomorphic Computing
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    id="zkproof"
                    type="checkbox"
                    checked={supportsZkProof}
                    onChange={(e) => setSupportsZkProof(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="zkproof" className="ml-2 text-sm text-gray-700">
                    ZK Proof
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    id="thirdparty"
                    type="checkbox"
                    checked={supportsThirdParty}
                    onChange={(e) => setSupportsThirdParty(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="thirdparty" className="ml-2 text-sm text-gray-700">
                    3rd-Party Computing
                  </label>
                </div>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Select the privacy-preserving computation methods supported by this dataset.
              </p>
            </div>
            
            <div>
              <label htmlFor="dataFile" className="block text-sm font-medium text-gray-700">
                Data File
              </label>
              <div className="mt-1">
                <input
                  type="file"
                  id="dataFile"
                  onChange={handleFileChange}
                  required
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Upload your data file. It will be encrypted before storage.
              </p>
            </div>
            
            <div className="pt-5">
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => navigate('/my-datasets')}
                  className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className={`ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                    loading ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? 'Creating...' : 'Create Dataset'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default CreateDataset;
