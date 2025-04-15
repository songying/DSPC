import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Marketplace from './pages/Marketplace';
import MyDatasets from './pages/MyDatasets';
import CreateDataset from './pages/CreateDataset';
import DatasetDetail from './pages/DatasetDetail';
import MyComputations from './pages/MyComputations';
import ComputationDetail from './pages/ComputationDetail';
import Analytics from './pages/Analytics';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/marketplace" element={<Marketplace />} />
          
          {/* Protected routes */}
          <Route 
            path="/my-datasets" 
            element={
              <ProtectedRoute>
                <MyDatasets />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/datasets/create" 
            element={
              <ProtectedRoute>
                <CreateDataset />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/datasets/:id" 
            element={
              <ProtectedRoute>
                <DatasetDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/my-computations" 
            element={
              <ProtectedRoute>
                <MyComputations />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/computations/:id" 
            element={
              <ProtectedRoute>
                <ComputationDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
