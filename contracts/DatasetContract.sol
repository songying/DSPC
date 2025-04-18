// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DatasetContract
 * @dev Contract for registering and managing dataset information on the blockchain
 */
contract DatasetContract {
    address public owner;
    string public datasetName;
    string public datasetDescription;
    uint256 public price;
    string public fileIndex;
    string[] public privacyOptions;
    uint256 public recordCount;
    uint256 public createdAt;
    
    // Events
    event DatasetRegistered(address indexed owner, string name, string fileIndex);
    event PriceUpdated(uint256 oldPrice, uint256 newPrice);
    event PrivacyOptionsUpdated(string[] options);
    
    /**
     * @dev Constructor to create a new dataset contract
     * @param _name Name of the dataset
     * @param _description Description of the dataset
     * @param _price Price in wei
     * @param _fileIndex Index reference to the file in the filesystem
     * @param _privacyOptions Array of privacy options for the dataset
     * @param _recordCount Number of records in the dataset
     */
    constructor(
        string memory _name,
        string memory _description,
        uint256 _price,
        string memory _fileIndex,
        string[] memory _privacyOptions,
        uint256 _recordCount
    ) {
        owner = msg.sender;
        datasetName = _name;
        datasetDescription = _description;
        price = _price;
        fileIndex = _fileIndex;
        privacyOptions = _privacyOptions;
        recordCount = _recordCount;
        createdAt = block.timestamp;
        
        emit DatasetRegistered(owner, _name, _fileIndex);
    }
    
    /**
     * @dev Modifier to restrict function access to the owner
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function");
        _;
    }
    
    /**
     * @dev Update the price of the dataset
     * @param _newPrice New price in wei
     */
    function updatePrice(uint256 _newPrice) public onlyOwner {
        uint256 oldPrice = price;
        price = _newPrice;
        emit PriceUpdated(oldPrice, _newPrice);
    }
    
    /**
     * @dev Update privacy options for the dataset
     * @param _newPrivacyOptions New array of privacy options
     */
    function updatePrivacyOptions(string[] memory _newPrivacyOptions) public onlyOwner {
        privacyOptions = _newPrivacyOptions;
        emit PrivacyOptionsUpdated(_newPrivacyOptions);
    }
    
    /**
     * @dev Get all privacy options
     * @return Array of privacy options
     */
    function getPrivacyOptions() public view returns (string[] memory) {
        return privacyOptions;
    }
    
    /**
     * @dev Get dataset information
     * @return Tuple containing dataset information
     */
    function getDatasetInfo() public view returns (
        address, 
        string memory, 
        string memory, 
        uint256, 
        string memory, 
        uint256, 
        uint256
    ) {
        return (
            owner,
            datasetName,
            datasetDescription,
            price,
            fileIndex,
            recordCount,
            createdAt
        );
    }
}
