// DayCare Invoice Tracker - Enhanced JavaScript with Theme System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme system
    initializeTheme();
    
    // Initialize all other features
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeConfirmationDialogs();
    initializeFileUpload();
    initializeSearch();
    initializePlaceholderFeatures();

    // Theme System
    function initializeTheme() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        
        // Get saved theme or system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        
        // Apply initial theme
        setTheme(initialTheme);
        
        // Theme toggle functionality
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                setTheme(newTheme);
            });
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
        
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            
            // Remove FOUC loading class
            document.body.classList.remove('theme-loading');
            
            if (themeIcon) {
                themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
            }
            
            // Update theme toggle aria-label
            if (themeToggle) {
                themeToggle.setAttribute('aria-label', 
                    theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
                );
                themeToggle.setAttribute('title', 
                    theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
                );
            }
        }
    }

    // Placeholder Features System - Updated for Phase 2
    function initializePlaceholderFeatures() {
        const featureModal = document.getElementById('featureModal');
        if (!featureModal) return;
        
        const modalInstance = new bootstrap.Modal(featureModal);
        const featureName = document.getElementById('featureName');
        const featureDescription = document.getElementById('featureDescription');
        const featurePhase = document.getElementById('featurePhase');
        
        // Only future features get placeholders - Phase 2 features are working
        const futureFeatures = {
            'settings': {
                name: 'User Settings',
                description: 'Customize your account preferences, notification settings, and configure email automation rules for invoice processing.',
                phase: 'Phase 3'
            },
            'reports': {
                name: 'Advanced Reporting',
                description: 'Generate detailed financial reports, payment analytics, and export data with customizable date ranges and filtering options.',
                phase: 'Phase 4'
            },
            'email-automation': {
                name: 'Email Automation',
                description: 'Automatically process emails from daycare providers, extract invoice PDFs, and streamline the invoice workflow.',
                phase: 'Phase 3'
            },
            'bulk-actions': {
                name: 'Bulk Actions',
                description: 'Select multiple invoices or payments to perform bulk operations like bulk payments, status updates, or export.',
                phase: 'Phase 3'
            },
            'notifications': {
                name: 'Smart Notifications',
                description: 'Automated reminders for overdue payments, upcoming due dates, and invoice processing notifications.',
                phase: 'Phase 3'
            }
        };
        
        // Add click handlers ONLY to future features
        document.addEventListener('click', function(e) {
            const featureLink = e.target.closest('[data-feature]');
            if (featureLink) {
                const featureKey = featureLink.getAttribute('data-feature');
                const feature = futureFeatures[featureKey];
                
                // Only prevent default and show modal for FUTURE features
                if (feature) {
                    e.preventDefault();
                    featureName.textContent = feature.name;
                    featureDescription.textContent = feature.description;
                    featurePhase.textContent = feature.phase;
                    modalInstance.show();
                }
                // Phase 2 features (invoices, payments, children) will work normally
            }
        });
    }

    // Initialize tooltips
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide alerts after 5 seconds
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                if (alert.classList.contains('show')) {
                    bsAlert.close();
                }
            }, 5000);
        });
    }

    // Form validation and loading state handler
    function initializeFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                // Check form validity
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    form.classList.add('was-validated');
                    return;
                }
                
                // Form is valid, show loading state
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    const originalContent = submitButton.innerHTML;
                    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                    submitButton.disabled = true;
                    
                    // Re-enable button if form submission fails (fallback)
                    setTimeout(function() {
                        if (submitButton.disabled) {
                            submitButton.innerHTML = originalContent;
                            submitButton.disabled = false;
                        }
                    }, 15000); // 15 second timeout
                }
                
                form.classList.add('was-validated');
            });
        });
    }

    // Confirmation dialogs
    function initializeConfirmationDialogs() {
        const deleteButtons = document.querySelectorAll('.btn-delete');
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(event) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    event.preventDefault();
                }
            });
        });
    }

    // File upload preview
    function initializeFileUpload() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(function(input) {
            input.addEventListener('change', function(event) {
                const file = event.target.files[0];
                const preview = input.parentElement.querySelector('.file-preview');
                
                if (file && preview) {
                    preview.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
                    preview.classList.remove('d-none');
                }
            });
        });
    }

    // Search functionality
    function initializeSearch() {
        const searchInput = document.querySelector('#search-input');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                const searchTerm = this.value.toLowerCase();
                const searchableItems = document.querySelectorAll('.searchable-item');
                
                searchableItems.forEach(function(item) {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }, 300));
        }
    }

    // Utility function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Currency formatting
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const value = parseFloat(input.value);
            if (!isNaN(value)) {
                input.value = value.toFixed(2);
            }
        });
    });

    // Debounce function for search
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

    // Enhanced keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
        
        // Ctrl/Cmd + / to focus search (if exists)
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('#search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + D to toggle theme
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                themeToggle.click();
            }
        }
    });

    // Add smooth scroll behavior for anchor links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });

    // Performance optimization: Intersection Observer for animations
    if ('IntersectionObserver' in window) {
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe dashboard cards for scroll animations
        document.querySelectorAll('.dashboard-card').forEach((card) => {
            animateOnScroll.observe(card);
        });
    }

    // Add CSS animation classes for scroll animations
    const style = document.createElement('style');
    style.textContent = `
        .dashboard-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .dashboard-card.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        @media (prefers-reduced-motion: reduce) {
            .dashboard-card {
                opacity: 1;
                transform: none;
                transition: none;
            }
        }
    `;
    document.head.appendChild(style);
});
