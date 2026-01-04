// Import page JavaScript
const API_URL = 'http://localhost:8000';
const currentUserId = parseInt(sessionStorage.getItem('user_id'));

// Security Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_MIME_TYPES = ['text/csv', 'application/vnd.ms-excel'];
const ALLOWED_EXTENSIONS = ['.csv'];

// State
let selectedFile = null;

// Redirect to login if not authenticated
if (!currentUserId) {
    alert('Please log in first');
    window.location.href = '/';
}

// ==================== PAGE LOAD ====================
document.addEventListener('DOMContentLoaded', () => {
    setupUploadArea();
    setupFileInput();
});

// ==================== TOAST NOTIFICATIONS ====================
function showMessage(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== UPLOAD AREA SETUP ====================
function setupUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    if (!uploadArea || !fileInput) return;

    // Click to upload
    uploadArea.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON') {
            fileInput.click();
        }
    });

    // Drag and drop events
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
}

function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput) return;

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// ==================== FILE VALIDATION ====================
function validateFile(file) {
    // Check if file exists
    if (!file) {
        return { valid: false, error: 'No file selected' };
    }

    // Check file extension
    const fileName = file.name.toLowerCase();
    const hasValidExtension = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));

    if (!hasValidExtension) {
        return {
            valid: false,
            error: 'Invalid file type. Only CSV files are allowed.'
        };
    }

    // Check MIME type
    if (!ALLOWED_MIME_TYPES.includes(file.type) && file.type !== '') {
        return {
            valid: false,
            error: `Invalid file format. Expected: ${ALLOWED_MIME_TYPES.join(', ')}`
        };
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
        const maxSizeMB = (MAX_FILE_SIZE / (1024 * 1024)).toFixed(1);
        return {
            valid: false,
            error: `File too large. Maximum size: ${maxSizeMB} MB`
        };
    }

    // Check for empty file
    if (file.size === 0) {
        return {
            valid: false,
            error: 'File is empty'
        };
    }

    // Additional security: Check file name for suspicious patterns
    const suspiciousPatterns = [
        /\.\./,  // Directory traversal
        /\0/,  // Null bytes
    ];

    for (const pattern of suspiciousPatterns) {
        if (pattern.test(fileName)) {
            return {
                valid: false,
                error: 'Invalid file name format'
            };
        }
    }

    return { valid: true };
}

// ==================== FILE SELECTION ====================
function handleFileSelect(file) {
    // Validate file
    const validation = validateFile(file);

    if (!validation.valid) {
        showMessage(validation.error, 'error');
        return;
    }

    // Store selected file
    selectedFile = file;

    // Update UI
    displaySelectedFile(file);
}

function displaySelectedFile(file) {
    const selectedFileDiv = document.getElementById('selectedFile');
    const fileNameSpan = document.getElementById('fileName');
    const fileSizeSpan = document.getElementById('fileSize');
    const importActions = document.getElementById('importActions');

    if (!selectedFileDiv || !fileNameSpan || !fileSizeSpan || !importActions) return;

    fileNameSpan.textContent = file.name;
    fileSizeSpan.textContent = formatFileSize(file.size);

    selectedFileDiv.classList.add('show');
    importActions.style.display = 'flex';
}

function removeFile() {
    selectedFile = null;

    // Reset UI
    const selectedFileDiv = document.getElementById('selectedFile');
    const importActions = document.getElementById('importActions');
    const fileInput = document.getElementById('fileInput');

    if (selectedFileDiv) selectedFileDiv.classList.remove('show');
    if (importActions) importActions.style.display = 'none';
    if (fileInput) fileInput.value = '';
}

// ==================== FILE UPLOAD ====================
async function uploadFile() {
    if (!selectedFile) {
        showMessage('Please select a file first', 'error');
        return;
    }

    // Re-validate before upload
    const validation = validateFile(selectedFile);
    if (!validation.valid) {
        showMessage(validation.error, 'error');
        return;
    }

    // Additional content validation
    try {
        await validateCSVContent(selectedFile);
    } catch (error) {
        showMessage(error.message, 'error');
        return;
    }

    // Show progress
    showProgress();

    // Create FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', currentUserId);

    try {
        const response = await fetch(`${API_URL}/import-csv`, {
            method: 'POST',
            body: formData,
        });

        updateProgress(100);

        if (response.ok) {
            const result = await response.json();
            showResults(result, true);
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to import transactions');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        hideProgress();
        showMessage(error.message || 'Connection error. Please try again.', 'error');
    }
}

// ==================== CSV CONTENT VALIDATION ====================
async function validateCSVContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const text = e.target.result;

                // Check for null bytes (potential security risk)
                if (text.includes('\0')) {
                    reject(new Error('File contains invalid characters'));
                    return;
                }

                // Parse first few lines to validate structure
                const lines = text.split('\n').slice(0, 10);

                if (lines.length < 2) {
                    reject(new Error('File is too short or empty'));
                    return;
                }

                // Check for header row
                const header = lines[0].toLowerCase();
                const requiredColumns = ['value date', 'text', 'amount'];
                const hasRequiredColumns = requiredColumns.every(col =>
                    header.includes(col)
                );

                if (!hasRequiredColumns) {
                    reject(new Error('Missing required columns. Expected: Value date, Text, Amount'));
                    return;
                }

                // Check for semicolon delimiter
                if (!header.includes(';')) {
                    reject(new Error('File must use semicolon (;) as delimiter'));
                    return;
                }

                resolve();
            } catch (error) {
                reject(new Error('Failed to parse CSV file'));
            }
        };

        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };

        // Read first 10KB for validation
        const blob = file.slice(0, 10240);
        reader.readAsText(blob);
    });
}

// ==================== PROGRESS HANDLING ====================
function showProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const importActions = document.getElementById('importActions');
    const selectedFileDiv = document.getElementById('selectedFile');

    if (progressContainer) progressContainer.classList.add('show');
    if (importActions) importActions.style.display = 'none';
    if (selectedFileDiv) selectedFileDiv.classList.remove('show');

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 90) {
            clearInterval(interval);
            progress = 90;
        }
        updateProgress(progress);
    }, 200);
}

function updateProgress(percent) {
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');

    if (!progressBar || !progressStatus) return;

    progressBar.style.width = `${percent}%`;
    progressBar.textContent = `${Math.round(percent)}%`;

    if (percent < 30) {
        progressStatus.textContent = 'Uploading file...';
    } else if (percent < 70) {
        progressStatus.textContent = 'Validating data...';
    } else if (percent < 90) {
        progressStatus.textContent = 'Processing transactions...';
    } else {
        progressStatus.textContent = 'Finalizing import...';
    }
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.classList.remove('show');
    }
}

// ==================== RESULTS DISPLAY ====================
function showResults(result, success) {
    hideProgress();

    const resultsDiv = document.getElementById('importResults');
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultStats = document.getElementById('resultStats');

    if (!resultsDiv || !resultIcon || !resultTitle || !resultStats) return;

    if (success) {
        resultIcon.textContent = '✅';
        resultTitle.textContent = 'Import Successful!';

        resultStats.innerHTML = `
            <div class="stat-card">
                <div class="stat-value success">${result.imported || 0}</div>
                <div class="stat-label">Imported</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">${result.duplicates || 0}</div>
                <div class="stat-label">Duplicates Skipped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value info">${result.total || 0}</div>
                <div class="stat-label">Total Processed</div>
            </div>
        `;

        showMessage(`Successfully imported ${result.imported} transactions!`, 'success');
    } else {
        resultIcon.textContent = '❌';
        resultTitle.textContent = 'Import Failed';

        resultStats.innerHTML = `
            <div class="stat-card">
                <div class="stat-value warning">0</div>
                <div class="stat-label">Imported</div>
            </div>
        `;
    }

    resultsDiv.classList.add('show');
}

function resetImport() {
    const importResults = document.getElementById('importResults');
    if (importResults) {
        importResults.classList.remove('show');
    }
    removeFile();
}

// ==================== UTILITY FUNCTIONS ====================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function logout() {
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('email');
    window.location.href = '/';
}