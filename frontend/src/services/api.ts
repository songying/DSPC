import axios from 'axios';
import { AuthResponse, User, Dataset, ComputationRequest, ComputationResult } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await axios.post<AuthResponse>(`${API_URL}/token`, formData.toString(), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  return response.data;
};

export const register = async (username: string, email: string, password: string): Promise<User> => {
  const response = await api.post<User>('/users/register', {
    username,
    email,
    password,
  });
  
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/users/me');
  return response.data;
};

export const updateWalletAddress = async (walletAddress: string): Promise<User> => {
  const response = await api.put<User>('/users/me/wallet', { wallet_address: walletAddress });
  return response.data;
};

export const loginWithWallet = async (
  walletAddress: string, 
  message: string, 
  signature: string
): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/users/wallet-login', {
    wallet_address: walletAddress,
    message,
    signature
  });
  return response.data;
};

export const createDataset = async (datasetData: FormData): Promise<Dataset> => {
  const response = await api.post<Dataset>('/datasets', datasetData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getDatasets = async (dataType?: string): Promise<Dataset[]> => {
  const params = dataType ? { data_type: dataType } : {};
  const response = await api.get<Dataset[]>('/datasets', { params });
  return response.data;
};

export const getMyDatasets = async (): Promise<Dataset[]> => {
  const response = await api.get<Dataset[]>('/datasets/my');
  return response.data;
};

export const getDataset = async (datasetId: string): Promise<Dataset> => {
  const response = await api.get<Dataset>(`/datasets/${datasetId}`);
  return response.data;
};

export const updateDataset = async (datasetId: string, datasetData: Partial<Dataset>): Promise<Dataset> => {
  const response = await api.put<Dataset>(`/datasets/${datasetId}`, datasetData);
  return response.data;
};

export const deleteDataset = async (datasetId: string): Promise<void> => {
  await api.delete(`/datasets/${datasetId}`);
};

export const requestComputation = async (computationData: {
  dataset_id: string;
  computation_type: string;
  algorithm_details: Record<string, any>;
}): Promise<ComputationRequest> => {
  const response = await api.post<ComputationRequest>('/computations/request', computationData);
  return response.data;
};

export const getMyComputationRequests = async (): Promise<ComputationRequest[]> => {
  const response = await api.get<ComputationRequest[]>('/computations/my-requests');
  return response.data;
};

export const getDatasetComputationRequests = async (datasetId: string): Promise<ComputationRequest[]> => {
  const response = await api.get<ComputationRequest[]>(`/computations/dataset/${datasetId}`);
  return response.data;
};

export const getComputationRequest = async (requestId: string): Promise<ComputationRequest> => {
  const response = await api.get<ComputationRequest>(`/computations/${requestId}`);
  return response.data;
};

export const processComputation = async (
  requestId: string,
  resultData: { encrypted_result: string }
): Promise<ComputationResult> => {
  const response = await api.post<ComputationResult>(`/computations/${requestId}/process`, resultData);
  return response.data;
};

export const getComputationResult = async (requestId: string): Promise<ComputationResult> => {
  const response = await api.get<ComputationResult>(`/computations/${requestId}/result`);
  return response.data;
};

export default api;
