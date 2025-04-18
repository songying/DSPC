import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import Layout from '../components/Layout';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TaskStatus {
  task_id: string;
  status: 'running' | 'completed' | 'failed';
  message: string;
  progress: number;
  visualization_files?: {
    filename: string;
    url: string;
  }[];
  result?: any;
}

interface AnalysisResults {
  short_video_analysis: {
    total_visits: number;
    short_video_visits: number;
    short_video_percentage: number;
    users_primarily_video: number;
    users_primarily_video_percentage: number;
  };
  ecommerce_after_video_analysis: {
    short_video_visits: number;
    ecommerce_after_video: number;
    ecommerce_after_video_percentage: number;
    users_with_pattern: number;
    users_with_pattern_percentage: number;
  };
  dataset_info: {
    total_users: number;
    sampled_users: number;
    date_range: string;
  };
}

const Analytics: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [datasetTask, setDatasetTask] = useState<TaskStatus | null>(null);
  const [analysisTask, setAnalysisTask] = useState<TaskStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [numUsers, setNumUsers] = useState(1000);
  const [eventsPerUser, setEventsPerUser] = useState(1000);
  const [sampleSize, setSampleSize] = useState(1000);
  const [activeTab, setActiveTab] = useState<'dataset' | 'analysis' | 'results'>('dataset');

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  useEffect(() => {
    let datasetInterval: ReturnType<typeof setInterval> | null = null;
    let analysisInterval: ReturnType<typeof setInterval> | null = null;

    if (datasetTask && datasetTask.status === 'running') {
      datasetInterval = setInterval(async () => {
        try {
          const response = await api.get(`/analytics/task/${datasetTask.task_id}`);
          setDatasetTask(response.data);
          
          if (response.data.status !== 'running') {
            if (datasetInterval) clearInterval(datasetInterval);
          }
        } catch (err) {
          console.error('Error polling dataset task:', err);
          if (datasetInterval) clearInterval(datasetInterval);
        }
      }, 2000);
    }

    if (analysisTask && analysisTask.status === 'running') {
      analysisInterval = setInterval(async () => {
        try {
          const response = await api.get(`/analytics/task/${analysisTask.task_id}`);
          setAnalysisTask(response.data);
          
          if (response.data.status === 'completed') {
            const resultsResponse = await api.get(`/analytics/results/${analysisTask.task_id}`);
            setResults(resultsResponse.data);
            
            const visualizationsResponse = await api.get(`/analytics/available-visualizations/${analysisTask.task_id}`);
            setAnalysisTask(prev => ({
              ...prev!,
              visualization_files: visualizationsResponse.data.visualization_files
            }));
            
            if (analysisInterval) clearInterval(analysisInterval);
          } else if (response.data.status === 'failed') {
            if (analysisInterval) clearInterval(analysisInterval);
          }
        } catch (err) {
          console.error('Error polling analysis task:', err);
          if (analysisInterval) clearInterval(analysisInterval);
        }
      }, 2000);
    }

    return () => {
      if (datasetInterval) clearInterval(datasetInterval);
      if (analysisInterval) clearInterval(analysisInterval);
    };
  }, [datasetTask, analysisTask]);

  const generateDataset = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post('/analytics/generate-dataset', {
        num_users: numUsers,
        events_per_user: eventsPerUser
      });
      
      setDatasetTask(response.data);
      setActiveTab('analysis');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate dataset');
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post('/analytics/run-analysis', {
        sample_size: sampleSize
      });
      
      setAnalysisTask(response.data);
      setActiveTab('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run analysis');
    } finally {
      setLoading(false);
    }
  };

  const renderDatasetTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Generate Test Dataset</h2>
      <p className="mb-4 text-gray-600">
        Generate a synthetic browser history dataset for testing the privacy-preserving analytics capabilities.
      </p>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Number of Users</label>
        <input
          type="number"
          min="10"
          max="10000"
          value={numUsers}
          onChange={(e) => setNumUsers(parseInt(e.target.value))}
          className="w-full p-2 border border-gray-300 rounded-md"
        />
        <p className="text-xs text-gray-500 mt-1">
          For demonstration purposes, limit to 10,000 users max. Production would support 1,000,000 users.
        </p>
      </div>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">Events Per User</label>
        <input
          type="number"
          min="100"
          max="10000"
          value={eventsPerUser}
          onChange={(e) => setEventsPerUser(parseInt(e.target.value))}
          className="w-full p-2 border border-gray-300 rounded-md"
        />
      </div>
      
      <button
        onClick={generateDataset}
        disabled={loading || (datasetTask?.status === 'running')}
        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
      >
        {loading ? 'Generating...' : 'Generate Dataset'}
      </button>
      
      {datasetTask && (
        <div className="mt-6 p-4 border border-gray-200 rounded-md">
          <h3 className="font-medium mb-2">Dataset Generation Status</h3>
          <div className="flex items-center mb-2">
            <div className="mr-2">
              {datasetTask.status === 'running' && <span className="text-yellow-500">⏳</span>}
              {datasetTask.status === 'completed' && <span className="text-green-500">✅</span>}
              {datasetTask.status === 'failed' && <span className="text-red-500">❌</span>}
            </div>
            <div className="text-sm">{datasetTask.message}</div>
          </div>
          
          {datasetTask.status === 'running' && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${datasetTask.progress}%` }}
              ></div>
            </div>
          )}
          
          {datasetTask.status === 'completed' && datasetTask.result && (
            <div className="mt-2 text-sm">
              <p>Generated dataset with {datasetTask.result.num_users} users and {datasetTask.result.total_events} total events.</p>
              <p>Date range: {datasetTask.result.date_range}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderAnalysisTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Run Privacy-Preserving Analysis</h2>
      <p className="mb-4 text-gray-600">
        Run homomorphic encryption-based analysis on the browser history dataset to answer key questions about user behavior.
      </p>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">Sample Size (Number of Users)</label>
        <input
          type="number"
          min="10"
          max={numUsers}
          value={sampleSize}
          onChange={(e) => setSampleSize(parseInt(e.target.value))}
          className="w-full p-2 border border-gray-300 rounded-md"
        />
        <p className="text-xs text-gray-500 mt-1">
          For faster analysis, you can sample a subset of users from the dataset.
        </p>
      </div>
      
      <button
        onClick={runAnalysis}
        disabled={loading || !datasetTask || datasetTask.status !== 'completed' || (analysisTask?.status === 'running')}
        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
      >
        {loading ? 'Analyzing...' : 'Run Analysis'}
      </button>
      
      {analysisTask && (
        <div className="mt-6 p-4 border border-gray-200 rounded-md">
          <h3 className="font-medium mb-2">Analysis Status</h3>
          <div className="flex items-center mb-2">
            <div className="mr-2">
              {analysisTask.status === 'running' && <span className="text-yellow-500">⏳</span>}
              {analysisTask.status === 'completed' && <span className="text-green-500">✅</span>}
              {analysisTask.status === 'failed' && <span className="text-red-500">❌</span>}
            </div>
            <div className="text-sm">{analysisTask.message}</div>
          </div>
          
          {analysisTask.status === 'running' && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${analysisTask.progress}%` }}
              ></div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderResultsTab = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
      
      {!analysisTask && (
        <p className="text-gray-600">Run an analysis to see results here.</p>
      )}
      
      {analysisTask && analysisTask.status === 'running' && (
        <div className="flex flex-col items-center justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
          <p className="text-gray-600">Analysis in progress... {analysisTask.progress}%</p>
          <p className="text-sm text-gray-500">{analysisTask.message}</p>
        </div>
      )}
      
      {analysisTask && analysisTask.status === 'failed' && (
        <div className="bg-red-50 p-4 rounded-md text-red-700">
          <p>Analysis failed: {analysisTask.message}</p>
        </div>
      )}
      
      {analysisTask && analysisTask.status === 'completed' && results && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Dataset Information</h3>
              <ul className="space-y-1 text-sm">
                <li><span className="font-medium">Total Users:</span> {results.dataset_info.total_users.toLocaleString()}</li>
                <li><span className="font-medium">Sampled Users:</span> {results.dataset_info.sampled_users.toLocaleString()}</li>
                <li><span className="font-medium">Date Range:</span> {results.dataset_info.date_range}</li>
                <li><span className="font-medium">Total Visits:</span> {results.short_video_analysis.total_visits.toLocaleString()}</li>
              </ul>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-2">Key Findings</h3>
              <ul className="space-y-1 text-sm">
                <li><span className="font-medium">Short Video Content:</span> {results.short_video_analysis.short_video_percentage.toFixed(1)}% of all content views</li>
                <li><span className="font-medium">Users Primarily Watching Short Videos:</span> {results.short_video_analysis.users_primarily_video_percentage.toFixed(1)}%</li>
                <li><span className="font-medium">E-commerce After Videos:</span> {results.ecommerce_after_video_analysis.ecommerce_after_video_percentage.toFixed(1)}% of short video views</li>
                <li><span className="font-medium">Users with Video→E-commerce Pattern:</span> {results.ecommerce_after_video_analysis.users_with_pattern_percentage.toFixed(1)}%</li>
              </ul>
            </div>
          </div>
          
          <h3 className="font-semibold text-lg mb-4">Visualizations</h3>
          
          {analysisTask.visualization_files && analysisTask.visualization_files.length > 0 ? (
            <div className="grid grid-cols-1 gap-6">
              {analysisTask.visualization_files.map((file) => (
                <div key={file.filename} className="border border-gray-200 rounded-lg overflow-hidden">
                  <h4 className="bg-gray-100 p-3 font-medium">{file.filename.replace('.png', '').replace(/_/g, ' ')}</h4>
                  <div className="p-4 flex justify-center">
                    <img 
                      src={`${API_URL}${file.url}`} 
                      alt={file.filename} 
                      className="max-w-full h-auto"
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600">No visualizations available.</p>
          )}
          
          <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
            <h3 className="font-semibold mb-2">Privacy Preservation</h3>
            <p className="text-sm text-gray-700">
              All analysis was performed using homomorphic encryption, which allows computation on encrypted data without decrypting it.
              This ensures that individual user data remains private while still enabling valuable aggregate insights.
            </p>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <Layout user={user} onLogout={() => {
      localStorage.removeItem('token');
      navigate('/login');
    }}>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Privacy-Preserving Analytics</h1>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
        
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('dataset')}
                className={`py-2 px-4 border-b-2 font-medium text-sm ${
                  activeTab === 'dataset'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                1. Generate Dataset
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`py-2 px-4 border-b-2 font-medium text-sm ${
                  activeTab === 'analysis'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                disabled={!datasetTask || datasetTask.status !== 'completed'}
              >
                2. Run Analysis
              </button>
              <button
                onClick={() => setActiveTab('results')}
                className={`py-2 px-4 border-b-2 font-medium text-sm ${
                  activeTab === 'results'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                disabled={!analysisTask}
              >
                3. View Results
              </button>
            </nav>
          </div>
        </div>
        
        <div className="mt-6">
          {activeTab === 'dataset' && renderDatasetTab()}
          {activeTab === 'analysis' && renderAnalysisTab()}
          {activeTab === 'results' && renderResultsTab()}
        </div>
      </div>
    </Layout>
  );
};

export default Analytics;
