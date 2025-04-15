export interface User {
  id: string;
  username: string;
  email: string;
  wallet_address?: string;
  created_at: string;
}

export enum DataType {
  PERSONAL = "personal",
  FINANCIAL = "financial",
  HEALTH = "health",
  BEHAVIORAL = "behavioral",
  OTHER = "other"
}

export enum ComputationType {
  ANALYSIS = "analysis",
  MACHINE_LEARNING = "machine_learning",
  STATISTICAL = "statistical",
  CUSTOM = "custom"
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  data_type: DataType;
  price: number;
  terms_of_use: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  is_available: boolean;
  supports_homomorphic?: boolean;
  supports_zk_proof?: boolean;
  supports_third_party?: boolean;
}

export interface ComputationRequest {
  id: string;
  dataset_id: string;
  requester_id: string;
  computation_type: ComputationType;
  algorithm_details: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
  transaction_hash?: string;
  result_hash?: string;
}

export interface ComputationResult {
  id: string;
  computation_id: string;
  encrypted_result: string;
  result_hash: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
