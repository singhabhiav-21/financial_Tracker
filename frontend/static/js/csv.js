// Import page JavaScript with security measures
const API_URL = 'http://localhost:8000';
const currentUserId = parseInt(sessionStorage.getItem('user_id'));

// Security Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_MIME_TYPES = ['text/csv', 'application/vnd.ms-excel', 'text/plain', 'application/csv'];
const ALLOWED_EXTENSIONS = ['.csv'];

// State
let selectedFile = null;
let uploadInterval = null;

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

// ==================== UPLOAD AREA SETUP ====================
function setupUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

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
            error: `Invalid file type. Only CSV files are allowed.`
        };
    }

    // Check MIME type (allow empty MIME type as some browsers don't send it)
    if (file.type && !ALLOWED_MIME_TYPES.includes(file.type)) {
        return {
            valid: false,
            error: `Invalid file format. Expected: CSV file`
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
        /[<>:"|?*]/,  // Invalid characters
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

    fileNameSpan.textContent = file.name;
    fileSizeSpan.textContent = formatFileSize(file.size);

    selectedFileDiv.classList.add('show');
    importActions.style.display = 'flex';
}

function removeFile() {
    selectedFile = null;

    // Clear any running intervals
    if (uploadInterval) {
        clearInterval(uploadInterval);
        uploadInterval = null;
    }

    // Reset UI
    document.getElementById('selectedFile').classList.remove('show');
    document.getElementById('importActions').style.display = 'none';
    document.getElementById('fileInput').value = '';
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

        // Clear progress interval
        if (uploadInterval) {
            clearInterval(uploadInterval);
            uploadInterval = null;
        }

        updateProgress(100);

        const result = await response.json();

        if (response.ok) {
            showResults(result, true);
        } else {
            hideProgress();
            showMessage(result.message || 'Import failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);

        // Clear progress interval on error
        if (uploadInterval) {
            clearInterval(uploadInterval);
            uploadInterval = null;
        }

        hideProgress();
        showMessage(error.message || 'Failed to upload file', 'error');
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
                const lines = text.split('\n').filter(line => line.trim().length > 0);

                if (lines.length < 2) {
                    reject(new Error('File is too short or empty'));
                    return;
                }

                // Check for header row - normalize and check for required columns
                const header = lines[0].toLowerCase().trim();
                console.log('CSV Header:', header); // Debug log

                // Split by common delimiters and normalize
                const headerCols = header.split(/[,;\t]/).map(col =>
                    col.trim().replace(/['"]/g, '')
                );

                console.log('Parsed columns:', headerCols); // Debug log

                const requiredColumns = ['value date', 'text', 'amount'];

                // Check if each required column exists (flexible matching)
                const missingColumns = requiredColumns.filter(reqCol => {
                    return !headerCols.some(headerCol => {
                        // Flexible matching: remove spaces, special chars
                        const normalized = headerCol.toLowerCase().replace(/[\s_-]/g, '');
                        const reqNormalized = reqCol.toLowerCase().replace(/[\s_-]/g, '');
                        return normalized.includes(reqNormalized) || reqNormalized.includes(normalized);
                    });
                });

                if (missingColumns.length > 0) {
                    console.error('Missing columns:', missingColumns);
                    console.error('Found columns:', headerCols);
                    reject(new Error(`Missing required columns: ${missingColumns.join(', ')}. Expected: Value date, Text, Amount`));
                    return;
                }

                // Check if there's at least one data row
                if (lines.length < 2) {
                    reject(new Error('CSV file has no data rows'));
                    return;
                }

                console.log('CSV validation passed!'); // Debug log
                resolve();
            } catch (error) {
                console.error('CSV parse error:', error);
                reject(new Error('Failed to parse CSV file: ' + error.message));
            }
        };

        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };

        // Read first 50KB for validation (increased from 10KB)
        const blob = file.slice(0, 51200);
        reader.readAsText(blob);
    });
}

// ==================== PROGRESS HANDLING ====================
function showProgress() {
    document.getElementById('progressContainer').classList.add('show');
    document.getElementById('importActions').style.display = 'none';
    document.getElementById('selectedFile').classList.remove('show');

    // Simulate progress
    let progress = 0;
    uploadInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 90) {
            clearInterval(uploadInterval);
            uploadInterval = null;
            progress = 90;
        }
        updateProgress(progress);
    }, 200);
}

function updateProgress(percent) {
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');

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
    // Clear any running intervals
    if (uploadInterval) {
        clearInterval(uploadInterval);
        uploadInterval = null;
    }
    document.getElementById('progressContainer').classList.remove('show');
}

// ==================== RESULTS DISPLAY ====================
function showResults(result, success) {
    hideProgress();

    const resultsDiv = document.getElementById('importResults');
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultStats = document.getElementById('resultStats');

    if (success) {
        resultIcon.textContent = '✅';
        resultTitle.textContent = 'Import Successful!';

        // Use the exact field names from backend response
        const imported = result.imported || 0;
        const duplicates = result.duplicates || 0;
        const total = result.total || 0;

        resultStats.innerHTML = `
            <div class="stat-card">
                <div class="stat-value success">${imported}</div>
                <div class="stat-label">Imported</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">${duplicates}</div>
                <div class="stat-label">Duplicates Skipped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value info">${total}</div>
                <div class="stat-label">Total Processed</div>
            </div>
        `;

        showMessage(`Successfully imported ${imported} transactions!`, 'success');
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
    document.getElementById('importResults').classList.remove('show');
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

function showMessage(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        padding: 16px 24px;
        margin-bottom: 10px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        opacity: 0;
        transform: translateX(100px);
        transition: all 0.3s ease;
        max-width: 400px;
        word-wrap: break-word;
    `;

    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    toast.style.backgroundColor = colors[type] || colors.info;

    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 10);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function logout() {
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('email');
    window.location.href = '/';
}

// Make functions globally accessible
window.uploadFile = uploadFile;
window.removeFile = removeFile;
window.resetImport = resetImport;
window.logout = logout;

console.log('import.js loaded successfully');