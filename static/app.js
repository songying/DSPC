const API_URL = window.location.origin;

let currentPage = 'home';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let marketplacePage = 1;
let myDatasetsPage = 1;

document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    
    if (authToken) {
        getCurrentUser().then(() => {
            updateAuthUI();
        });
    }
    
    navigateTo('home');
});

function initializeUI() {
    document.getElementById('nav-home').addEventListener('click', () => navigateTo('home'));
    document.getElementById('nav-marketplace').addEventListener('click', () => navigateTo('marketplace'));
    document.getElementById('nav-my-datasets').addEventListener('click', () => navigateTo('my-datasets'));
    document.getElementById('nav-create-dataset').addEventListener('click', () => navigateTo('create-dataset'));
    
    const exploreMarketplaceBtn = document.getElementById('explore-marketplace');
    if (exploreMarketplaceBtn) {
        exploreMarketplaceBtn.addEventListener('click', () => navigateTo('marketplace'));
    }
    
    document.getElementById('connect-wallet').addEventListener('click', connectWallet);
    
    const inputMethodRadios = document.querySelectorAll('input[name="input-method"]');
    inputMethodRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const fileInputContainer = document.getElementById('file-input-container');
            const textInputContainer = document.getElementById('text-input-container');
            
            if (radio.value === 'file') {
                fileInputContainer.classList.remove('d-none');
                textInputContainer.classList.add('d-none');
            } else {
                fileInputContainer.classList.add('d-none');
                textInputContainer.classList.remove('d-none');
            }
        });
    });
    
    const createDatasetForm = document.getElementById('create-dataset-form');
    if (createDatasetForm) {
        createDatasetForm.addEventListener('submit', createDataset);
    }
}

async function connectWallet() {
    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            const address = accounts[0];
            
            const response = await fetch(`${API_URL}/api/auth/web3`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ wallet_address: address })
            });
            
            const data = await response.json();
            
            if (data.access_token) {
                authToken = data.access_token;
                localStorage.setItem('authToken', authToken);
                
                await getCurrentUser();
                
                updateAuthUI();
                
                showToast('Connected successfully!', 'success');
                
                navigateTo('marketplace');
            }
        } catch (error) {
            console.error('Error connecting wallet:', error);
            showToast('Error connecting wallet', 'danger');
        }
    } else {
        showToast('MetaMask is not installed', 'warning');
        window.open('https://metamask.io/download.html', '_blank');
    }
}

async function createDataset(e) {
    e.preventDefault();
    
    if (!authToken) {
        showToast('Please connect your wallet first', 'warning');
        return;
    }
    
    try {
        const formData = new FormData(e.target);
        
        const privacyOptions = [];
        document.querySelectorAll('input[name="privacy_options"]:checked').forEach(checkbox => {
            privacyOptions.push(checkbox.value);
        });
        
        formData.delete('privacy_options');
        privacyOptions.forEach(option => {
            formData.append('privacy_options', option);
        });
        
        const inputMethod = document.querySelector('input[name="input-method"]:checked').value;
        if (inputMethod === 'file') {
            const fileInput = document.getElementById('dataset-file');
            if (fileInput.files.length === 0) {
                showToast('Please select a file', 'warning');
                return;
            }
        } else {
            const textData = document.getElementById('dataset-text').value;
            if (!textData.trim()) {
                showToast('Please enter data', 'warning');
                return;
            }
            formData.append('text_data', textData);
        }
        
        const response = await fetch(`${API_URL}/api/datasets`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Dataset created successfully!', 'success');
            navigateTo('my-datasets');
        } else {
            const error = await response.json();
            showToast(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Error creating dataset:', error);
        showToast('Error creating dataset', 'danger');
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_URL}/api/users/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            return currentUser;
        } else {
            authToken = null;
            localStorage.removeItem('authToken');
            return null;
        }
    } catch (error) {
        console.error('Error getting current user:', error);
        authToken = null;
        localStorage.removeItem('authToken');
        return null;
    }
}

function updateAuthUI() {
    const connectWalletBtn = document.getElementById('connect-wallet');
    const walletContainer = document.getElementById('wallet-container');
    const walletAddressSpan = document.getElementById('wallet-address');
    
    if (authToken && currentUser) {
        connectWalletBtn.classList.add('d-none');
        walletContainer.classList.remove('d-none');
        walletAddressSpan.textContent = currentUser.username || currentUser.wallet_address;
    } else {
        connectWalletBtn.classList.remove('d-none');
        walletContainer.classList.add('d-none');
    }
}

function navigateTo(page) {
    document.getElementById('home-page').classList.add('d-none');
    document.getElementById('marketplace-page').classList.add('d-none');
    document.getElementById('my-datasets-page').classList.add('d-none');
    document.getElementById('create-dataset-page').classList.add('d-none');
    document.getElementById('dataset-detail-page').classList.add('d-none');
    
    currentPage = page;
    
    switch (page) {
        case 'home':
            document.getElementById('home-page').classList.remove('d-none');
            break;
        case 'marketplace':
            document.getElementById('marketplace-page').classList.remove('d-none');
            loadMarketplaceDatasets();
            break;
        case 'my-datasets':
            if (!authToken) {
                showToast('Please connect your wallet first', 'warning');
                navigateTo('home');
                return;
            }
            document.getElementById('my-datasets-page').classList.remove('d-none');
            loadMyDatasets();
            break;
        case 'create-dataset':
            if (!authToken) {
                showToast('Please connect your wallet first', 'warning');
                navigateTo('home');
                return;
            }
            document.getElementById('create-dataset-page').classList.remove('d-none');
            break;
        case 'dataset-detail':
            document.getElementById('dataset-detail-page').classList.remove('d-none');
            break;
    }
}

async function loadMarketplaceDatasets(page = 1) {
    try {
        const response = await fetch(`${API_URL}/api/datasets?page=${page}&limit=6`);
        const data = await response.json();
        
        const datasetsContainer = document.getElementById('marketplace-datasets');
        datasetsContainer.innerHTML = '';
        
        if (data.datasets.length === 0) {
            datasetsContainer.innerHTML = '<div class="col-12 text-center"><p>No datasets available</p></div>';
            return;
        }
        
        data.datasets.forEach(dataset => {
            datasetsContainer.appendChild(createDatasetCard(dataset));
        });
        
        const paginationContainer = document.getElementById('marketplace-pagination');
        paginationContainer.innerHTML = '';
        
        if (data.pages > 1) {
            paginationContainer.appendChild(createPagination(data.page, data.pages, 'marketplace'));
        }
        
        marketplacePage = data.page;
    } catch (error) {
        console.error('Error loading marketplace datasets:', error);
        showToast('Error loading datasets', 'danger');
    }
}

async function loadMyDatasets(page = 1) {
    try {
        if (!currentUser) {
            await getCurrentUser();
        }
        
        if (!currentUser) {
            showToast('Please connect your wallet first', 'warning');
            navigateTo('home');
            return;
        }
        
        const response = await fetch(`${API_URL}/api/users/${currentUser.wallet_address}/datasets?page=${page}&limit=6`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        const datasetsContainer = document.getElementById('my-datasets-list');
        datasetsContainer.innerHTML = '';
        
        if (data.datasets.length === 0) {
            datasetsContainer.innerHTML = '<div class="col-12 text-center"><p>You have no datasets yet</p></div>';
            return;
        }
        
        data.datasets.forEach(dataset => {
            datasetsContainer.appendChild(createDatasetCard(dataset, true));
        });
        
        const paginationContainer = document.getElementById('my-datasets-pagination');
        paginationContainer.innerHTML = '';
        
        if (data.pages > 1) {
            paginationContainer.appendChild(createPagination(data.page, data.pages, 'my-datasets'));
        }
        
        myDatasetsPage = data.page;
    } catch (error) {
        console.error('Error loading my datasets:', error);
        showToast('Error loading datasets', 'danger');
    }
}

function createDatasetCard(dataset, isOwner = false) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    
    const card = document.createElement('div');
    card.className = 'card h-100';
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    
    const title = document.createElement('h5');
    title.className = 'card-title';
    title.textContent = dataset.name;
    
    const description = document.createElement('p');
    description.className = 'card-text';
    description.textContent = dataset.description.length > 100 ? dataset.description.substring(0, 100) + '...' : dataset.description;
    
    const price = document.createElement('p');
    price.className = 'card-text';
    price.innerHTML = `<strong>Price:</strong> ${dataset.price} ETH`;
    
    const records = document.createElement('p');
    records.className = 'card-text';
    records.innerHTML = `<strong>Records:</strong> ${dataset.records.toLocaleString()}`;
    
    const size = document.createElement('p');
    size.className = 'card-text';
    size.innerHTML = `<strong>Size:</strong> ${dataset.file_size || dataset.size}`;
    
    const privacyOptions = document.createElement('div');
    privacyOptions.className = 'mb-3';
    
    if (dataset.privacy_options && dataset.privacy_options.length > 0) {
        dataset.privacy_options.forEach(option => {
            const badge = document.createElement('span');
            badge.className = 'badge me-1';
            
            if (option === 'Homomorphic Computing') {
                badge.className += ' badge-homomorphic';
            } else if (option === 'ZK Proof') {
                badge.className += ' badge-zk';
            } else if (option === '3rd-Party computing') {
                badge.className += ' badge-thirdparty';
            }
            
            badge.textContent = option;
            privacyOptions.appendChild(badge);
        });
    }
    
    const viewButton = document.createElement('button');
    viewButton.className = 'btn btn-primary';
    viewButton.textContent = 'View Details';
    viewButton.addEventListener('click', () => {
        viewDatasetDetails(dataset._id || dataset.id);
    });
    
    cardBody.appendChild(title);
    cardBody.appendChild(description);
    cardBody.appendChild(price);
    cardBody.appendChild(records);
    cardBody.appendChild(size);
    cardBody.appendChild(privacyOptions);
    cardBody.appendChild(viewButton);
    
    card.appendChild(cardBody);
    col.appendChild(card);
    
    return col;
}

function createPagination(currentPage, totalPages, pageType) {
    const nav = document.createElement('nav');
    const ul = document.createElement('ul');
    ul.className = 'pagination';
    
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    
    const prevLink = document.createElement('a');
    prevLink.className = 'page-link';
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    
    if (currentPage > 1) {
        prevLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (pageType === 'marketplace') {
                loadMarketplaceDatasets(currentPage - 1);
            } else {
                loadMyDatasets(currentPage - 1);
            }
        });
    }
    
    prevLi.appendChild(prevLink);
    ul.appendChild(prevLi);
    
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);
    
    if (endPage - startPage + 1 < maxPages) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
        
        const pageLink = document.createElement('a');
        pageLink.className = 'page-link';
        pageLink.href = '#';
        pageLink.textContent = i;
        
        if (i !== currentPage) {
            pageLink.addEventListener('click', (e) => {
                e.preventDefault();
                if (pageType === 'marketplace') {
                    loadMarketplaceDatasets(i);
                } else {
                    loadMyDatasets(i);
                }
            });
        }
        
        pageLi.appendChild(pageLink);
        ul.appendChild(pageLi);
    }
    
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    
    const nextLink = document.createElement('a');
    nextLink.className = 'page-link';
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    
    if (currentPage < totalPages) {
        nextLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (pageType === 'marketplace') {
                loadMarketplaceDatasets(currentPage + 1);
            } else {
                loadMyDatasets(currentPage + 1);
            }
        });
    }
    
    nextLi.appendChild(nextLink);
    ul.appendChild(nextLi);
    
    nav.appendChild(ul);
    return nav;
}

async function viewDatasetDetails(datasetId) {
    try {
        const response = await fetch(`${API_URL}/api/datasets/${datasetId}`);
        const dataset = await response.json();
        
        const detailContent = document.getElementById('dataset-detail-content');
        
        let privacyOptionsHtml = '';
        if (dataset.privacy_options && dataset.privacy_options.length > 0) {
            dataset.privacy_options.forEach(option => {
                let badgeClass = '';
                
                if (option === 'Homomorphic Computing') {
                    badgeClass = 'badge-homomorphic';
                } else if (option === 'ZK Proof') {
                    badgeClass = 'badge-zk';
                } else if (option === '3rd-Party computing') {
                    badgeClass = 'badge-thirdparty';
                }
                
                privacyOptionsHtml += `<span class="badge me-1 ${badgeClass}">${option}</span>`;
            });
        }
        
        detailContent.innerHTML = `
            <div class="card mb-4">
                <div class="card-body">
                    <h2 class="card-title">${dataset.name}</h2>
                    <p class="card-text">${dataset.description}</p>
                    <div class="mb-3">
                        ${privacyOptionsHtml}
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <p><strong>Price:</strong> ${dataset.price} ETH</p>
                        </div>
                        <div class="col-md-4">
                            <p><strong>Records:</strong> ${dataset.records.toLocaleString()}</p>
                        </div>
                        <div class="col-md-4">
                            <p><strong>Size:</strong> ${dataset.file_size || dataset.size}</p>
                        </div>
                    </div>
                    <div class="mb-3">
                        <p><strong>Contract Address:</strong> ${dataset.contract_address || 'Not registered'}</p>
                    </div>
                    <button class="btn btn-primary" onclick="navigateTo('marketplace')">Back to Marketplace</button>
                </div>
            </div>
        `;
        
        navigateTo('dataset-detail');
    } catch (error) {
        console.error('Error loading dataset details:', error);
        showToast('Error loading dataset details', 'danger');
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body d-flex justify-content-between align-items-center';
    toastBody.innerHTML = `
        <span>${message}</span>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
    `;
    
    toast.appendChild(toastBody);
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 500);
    }, 5000);
    
    const closeButton = toastBody.querySelector('.btn-close');
    closeButton.addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 500);
    });
}
