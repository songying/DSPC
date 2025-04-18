from typing import Dict, List, Optional, Any
import uuid

class InMemoryDB:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.computation_requests: Dict[str, Dict[str, Any]] = {}
        self.computation_results: Dict[str, Dict[str, Any]] = {}
        self.user_by_username: Dict[str, str] = {}  # username -> user_id

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        user_data["id"] = user_id
        self.users[user_id] = user_data
        self.user_by_username[user_data["username"]] = user_id
        return user_data

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user_id = self.user_by_username.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
        
    def get_user_by_wallet_address(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        for user in self.users.values():
            if user.get("wallet_address", "").lower() == wallet_address.lower():
                return user
        return None

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if user_id in self.users:
            self.users[user_id].update(user_data)
            return self.users[user_id]
        return None

    def create_dataset(self, dataset_data: Dict[str, Any]) -> Dict[str, Any]:
        dataset_id = str(uuid.uuid4())
        dataset_data["id"] = dataset_id
        self.datasets[dataset_id] = dataset_data
        return dataset_data

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return self.datasets.get(dataset_id)

    def get_datasets_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        return [dataset for dataset in self.datasets.values() if dataset["owner_id"] == owner_id]

    def get_available_datasets(self) -> List[Dict[str, Any]]:
        return [dataset for dataset in self.datasets.values() if dataset.get("is_available", True)]

    def update_dataset(self, dataset_id: str, dataset_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if dataset_id in self.datasets:
            self.datasets[dataset_id].update(dataset_data)
            return self.datasets[dataset_id]
        return None

    def create_computation_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        request_data["id"] = request_id
        self.computation_requests[request_id] = request_data
        return request_data

    def get_computation_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self.computation_requests.get(request_id)

    def get_computation_requests_by_requester(self, requester_id: str) -> List[Dict[str, Any]]:
        return [req for req in self.computation_requests.values() if req["requester_id"] == requester_id]

    def get_computation_requests_by_dataset(self, dataset_id: str) -> List[Dict[str, Any]]:
        return [req for req in self.computation_requests.values() if req["dataset_id"] == dataset_id]

    def update_computation_request(self, request_id: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if request_id in self.computation_requests:
            self.computation_requests[request_id].update(request_data)
            return self.computation_requests[request_id]
        return None

    def create_computation_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        result_id = str(uuid.uuid4())
        result_data["id"] = result_id
        self.computation_results[result_id] = result_data
        return result_data

    def get_computation_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        return self.computation_results.get(result_id)

    def get_computation_result_by_computation(self, computation_id: str) -> Optional[Dict[str, Any]]:
        for result in self.computation_results.values():
            if result["computation_id"] == computation_id:
                return result
        return None

db = InMemoryDB()

def create_test_user_if_not_exists():
    from .auth import get_password_hash
    from datetime import datetime
    
    existing_user = db.get_user_by_username('testuser')
    if existing_user:
        print(f"Test user already exists: {existing_user['username']}")
        return existing_user
    
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': get_password_hash('password'),
        'wallet_address': '0x0',
        'created_at': datetime.now()
    }
    
    created_user = db.create_user(user_data)
    print(f"Test user created: {created_user['username']}")
    return created_user

create_test_user_if_not_exists()
