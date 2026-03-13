/**
 * AI Resume Analyzer - Frontend JavaScript
 * Handles form submissions, AJAX requests, and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Try both form IDs for compatibility
    const resumeForm = document.getElementById('analyzeForm') || document.getElementById('resumeForm');
    if (resumeForm) {
        resumeForm.addEventListener('submit', handleFormSubmit);
    }

    // Drag and drop handler
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }

    // File input change handler
    const fileInput = document.getElementById('resumeFile') || document.getElementById('resume');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Update file name display
    const fileNameDisplay = document.getElementById('fileName');
    if (fileNameDisplay) {
        fileNameDisplay.textContent = file.name;
        fileNameDisplay.classList.add('active');
    }

    // Validate file
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (file.size > maxSize) {
        showError('File size exceeds 5MB limit');
        event.target.value = '';
        if (fileNameDisplay) {
            fileNameDisplay.textContent = '';
            fileNameDisplay.classList.remove('active');
        }
        return;
    }

    if (!allowedTypes.includes(file.type)) {
        showError('Only PDF and DOCX files are allowed');
        event.target.value = '';
        if (fileNameDisplay) {
            fileNameDisplay.textContent = '';
            fileNameDisplay.classList.remove('active');
        }
        return;
    }

    clearMessages();
}

/**
 * Handle drag over
 */
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    this.style.borderColor = '#764ba2';
    this.style.background = 'rgba(102, 126, 234, 0.15)';
}

/**
 * Handle drag leave
 */
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    this.style.borderColor = '#667eea';
    this.style.background = 'rgba(102, 126, 234, 0.05)';
}

/**
 * Handle drop
 */
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    this.style.borderColor = '#667eea';
    this.style.background = 'rgba(102, 126, 234, 0.05)';

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = document.getElementById('resumeFile') || document.getElementById('resume');
        if (fileInput) {
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    }
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const resumeInput = document.getElementById('resumeFile') || document.getElementById('resume');
    const jobDescInput = document.getElementById('jobDescription') || document.getElementById('job_description');
    
    // Validate inputs
    if (!resumeInput || !resumeInput.files[0]) {
        showError('Please select a resume file');
        return;
    }

    if (!jobDescInput || !jobDescInput.value.trim()) {
        showError('Please enter a job description');
        return;
    }

    // Show loading state
    showLoading(true);
    clearMessages();

    try {
        const formData = new FormData();
        formData.append('resume', resumeInput.files[0]);
        formData.append('job_description', jobDescInput.value);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Upload failed');
        }

        const result = await response.json();
        
        // Store resume filename in localStorage for comparison feature
        localStorage.setItem('currentResumeFile', result.filename);
        
        // Show success message
        showSuccess('Analysis complete! Redirecting to results...');
        
        // Redirect after 1.5 seconds
        setTimeout(() => {
            window.location.href = '/result/' + result.filename;
        }, 1500);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred during analysis');
    } finally {
        showLoading(false);
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.getElementById('errorAlert');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    const successDiv = document.getElementById('successAlert');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.classList.add('show');
    }
}

/**
 * Clear all messages
 */
function clearMessages() {
    const errorDiv = document.getElementById('errorAlert');
    const successDiv = document.getElementById('successAlert');
    
    if (errorDiv) errorDiv.classList.remove('show');
    if (successDiv) successDiv.classList.remove('show');
}

/**
 * Show/hide loading state
 */
function showLoading(show) {
    const btnSpinner = document.getElementById('btnSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (analyzeBtn) {
        if (show) {
            if (btnSpinner) btnSpinner.style.display = 'inline-block';
            analyzeBtn.disabled = true;
        } else {
            if (btnSpinner) btnSpinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number format
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccess('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showError('Failed to copy to clipboard');
    });
}

/**
 * Export data as JSON
 */
function exportAsJSON(data, filename) {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'export.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Export data as CSV
 */
function exportAsCSV(data, filename) {
    let csv = '';
    
    // Add headers
    if (Array.isArray(data) && data.length > 0) {
        csv = Object.keys(data[0]).join(',') + '\n';
        
        // Add rows
        data.forEach(row => {
            csv += Object.values(row).map(val => {
                const escaped = String(val).replace(/"/g, '""');
                return `"${escaped}"`;
            }).join(',') + '\n';
        });
    }
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'export.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for scroll events
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Get URL parameters
 */
function getUrlParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');
    
    pairs.forEach(pair => {
        const [key, value] = pair.split('=');
        params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    });
    
    return params;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style toast
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: ${getToastColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after duration
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
}

/**
 * Get toast color based on type
 */
function getToastColor(type) {
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    return colors[type] || colors.info;
}

/**
 * Add CSS animations dynamically
 */
function addAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Add animations on page load
addAnimations();

// Add service worker for offline support (optional)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
        console.log('ServiceWorker registration failed: ', err);
    });
}
