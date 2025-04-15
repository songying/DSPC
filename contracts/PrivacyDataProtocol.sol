// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Privacy Data Protocol
 * @dev Smart contract for privacy-preserving data trading and computing
 */
contract PrivacyDataProtocol {
    // Events
    event DatasetRegistered(bytes32 indexed datasetId, address indexed owner, uint256 price);
    event ComputationRequested(bytes32 indexed computationId, bytes32 indexed datasetId, address indexed requester);
    event ComputationCompleted(bytes32 indexed computationId, bytes32 resultHash);
    event PaymentReleased(bytes32 indexed computationId, address to, uint256 amount);

    // Enum for dataset types
    enum DataType { PERSONAL, FINANCIAL, HEALTH, BEHAVIORAL, OTHER }
    
    // Enum for computation types
    enum ComputationType { ANALYSIS, MACHINE_LEARNING, STATISTICAL, CUSTOM }

    // Dataset struct
    struct Dataset {
        bytes32 id;
        address owner;
        string name;
        string description;
        DataType dataType;
        uint256 price;
        string termsHash;
        bool isAvailable;
        uint256 createdAt;
    }

    // Computation request struct
    struct ComputationRequest {
        bytes32 id;
        bytes32 datasetId;
        address requester;
        ComputationType computationType;
        string algorithmDetailsHash;
        bytes32 resultHash;
        RequestStatus status;
        uint256 createdAt;
        uint256 completedAt;
    }

    // Request status enum
    enum RequestStatus { PENDING, PROCESSING, COMPLETED, FAILED }

    // Mappings
    mapping(bytes32 => Dataset) public datasets;
    mapping(bytes32 => ComputationRequest) public computations;
    mapping(address => bytes32[]) public userDatasets;
    mapping(address => bytes32[]) public userComputations;

    // Constructor
    constructor() {
        // Initialization if needed
    }

    /**
     * @dev Register a new dataset
     * @param _name Name of the dataset
     * @param _description Description of the dataset
     * @param _dataType Type of data
     * @param _price Price in wei
     * @param _termsHash Hash of terms of use
     * @param _metadataHash Hash of encrypted metadata
     * @return datasetId The ID of the registered dataset
     */
    function registerDataset(
        string memory _name,
        string memory _description,
        DataType _dataType,
        uint256 _price,
        string memory _termsHash,
        string memory _metadataHash
    ) public returns (bytes32) {
        // Generate a unique ID for the dataset
        bytes32 datasetId = keccak256(abi.encodePacked(msg.sender, _name, block.timestamp, _metadataHash));
        
        // Create the dataset
        Dataset memory newDataset = Dataset({
            id: datasetId,
            owner: msg.sender,
            name: _name,
            description: _description,
            dataType: _dataType,
            price: _price,
            termsHash: _termsHash,
            isAvailable: true,
            createdAt: block.timestamp
        });
        
        // Store the dataset
        datasets[datasetId] = newDataset;
        userDatasets[msg.sender].push(datasetId);
        
        // Emit event
        emit DatasetRegistered(datasetId, msg.sender, _price);
        
        return datasetId;
    }

    /**
     * @dev Request a computation on a dataset
     * @param _datasetId ID of the dataset
     * @param _computationType Type of computation
     * @param _algorithmDetailsHash Hash of algorithm details
     * @return computationId The ID of the computation request
     */
    function requestComputation(
        bytes32 _datasetId,
        ComputationType _computationType,
        string memory _algorithmDetailsHash
    ) public payable returns (bytes32) {
        // Get the dataset
        Dataset storage dataset = datasets[_datasetId];
        
        // Check if dataset exists and is available
        require(dataset.owner != address(0), "Dataset does not exist");
        require(dataset.isAvailable, "Dataset is not available");
        
        // Check if payment is sufficient
        require(msg.value >= dataset.price, "Insufficient payment");
        
        // Generate a unique ID for the computation
        bytes32 computationId = keccak256(abi.encodePacked(msg.sender, _datasetId, block.timestamp, _algorithmDetailsHash));
        
        // Create the computation request
        ComputationRequest memory newComputation = ComputationRequest({
            id: computationId,
            datasetId: _datasetId,
            requester: msg.sender,
            computationType: _computationType,
            algorithmDetailsHash: _algorithmDetailsHash,
            resultHash: bytes32(0),
            status: RequestStatus.PENDING,
            createdAt: block.timestamp,
            completedAt: 0
        });
        
        // Store the computation request
        computations[computationId] = newComputation;
        userComputations[msg.sender].push(computationId);
        
        // Emit event
        emit ComputationRequested(computationId, _datasetId, msg.sender);
        
        return computationId;
    }

    /**
     * @dev Submit computation result
     * @param _computationId ID of the computation
     * @param _resultHash Hash of the encrypted result
     */
    function submitComputationResult(bytes32 _computationId, bytes32 _resultHash) public {
        // Get the computation request
        ComputationRequest storage computation = computations[_computationId];
        
        // Get the dataset
        Dataset storage dataset = datasets[computation.datasetId];
        
        // Check if computation exists
        require(computation.requester != address(0), "Computation does not exist");
        
        // Check if caller is the dataset owner
        require(msg.sender == dataset.owner, "Only dataset owner can submit results");
        
        // Check if computation is in pending or processing status
        require(
            computation.status == RequestStatus.PENDING || 
            computation.status == RequestStatus.PROCESSING, 
            "Computation is not in a valid state for result submission"
        );
        
        // Update computation status
        computation.status = RequestStatus.COMPLETED;
        computation.resultHash = _resultHash;
        computation.completedAt = block.timestamp;
        
        // Emit event
        emit ComputationCompleted(_computationId, _resultHash);
        
        // Release payment to dataset owner
        payable(dataset.owner).transfer(dataset.price);
        
        // Emit payment event
        emit PaymentReleased(_computationId, dataset.owner, dataset.price);
    }

    /**
     * @dev Update dataset availability
     * @param _datasetId ID of the dataset
     * @param _isAvailable New availability status
     */
    function updateDatasetAvailability(bytes32 _datasetId, bool _isAvailable) public {
        // Get the dataset
        Dataset storage dataset = datasets[_datasetId];
        
        // Check if dataset exists
        require(dataset.owner != address(0), "Dataset does not exist");
        
        // Check if caller is the dataset owner
        require(msg.sender == dataset.owner, "Only dataset owner can update availability");
        
        // Update availability
        dataset.isAvailable = _isAvailable;
    }

    /**
     * @dev Update computation status
     * @param _computationId ID of the computation
     * @param _status New status
     */
    function updateComputationStatus(bytes32 _computationId, RequestStatus _status) public {
        // Get the computation request
        ComputationRequest storage computation = computations[_computationId];
        
        // Get the dataset
        Dataset storage dataset = datasets[computation.datasetId];
        
        // Check if computation exists
        require(computation.requester != address(0), "Computation does not exist");
        
        // Check if caller is the dataset owner
        require(msg.sender == dataset.owner, "Only dataset owner can update status");
        
        // Update status
        computation.status = _status;
        
        // If failed, refund the requester
        if (_status == RequestStatus.FAILED) {
            payable(computation.requester).transfer(dataset.price);
            emit PaymentReleased(_computationId, computation.requester, dataset.price);
        }
    }

    /**
     * @dev Get dataset details
     * @param _datasetId ID of the dataset
     * @return Dataset details
     */
    function getDataset(bytes32 _datasetId) public view returns (
        bytes32 id,
        address owner,
        string memory name,
        string memory description,
        DataType dataType,
        uint256 price,
        bool isAvailable,
        uint256 createdAt
    ) {
        Dataset memory dataset = datasets[_datasetId];
        return (
            dataset.id,
            dataset.owner,
            dataset.name,
            dataset.description,
            dataset.dataType,
            dataset.price,
            dataset.isAvailable,
            dataset.createdAt
        );
    }

    /**
     * @dev Get computation details
     * @param _computationId ID of the computation
     * @return Computation details
     */
    function getComputation(bytes32 _computationId) public view returns (
        bytes32 id,
        bytes32 datasetId,
        address requester,
        ComputationType computationType,
        RequestStatus status,
        bytes32 resultHash,
        uint256 createdAt,
        uint256 completedAt
    ) {
        ComputationRequest memory computation = computations[_computationId];
        return (
            computation.id,
            computation.datasetId,
            computation.requester,
            computation.computationType,
            computation.status,
            computation.resultHash,
            computation.createdAt,
            computation.completedAt
        );
    }

    /**
     * @dev Get user datasets
     * @param _user Address of the user
     * @return Array of dataset IDs
     */
    function getUserDatasets(address _user) public view returns (bytes32[] memory) {
        return userDatasets[_user];
    }

    /**
     * @dev Get user computations
     * @param _user Address of the user
     * @return Array of computation IDs
     */
    function getUserComputations(address _user) public view returns (bytes32[] memory) {
        return userComputations[_user];
    }
}
