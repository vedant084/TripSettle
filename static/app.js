// Cash Flow Minimizer - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation for expense amounts
    const amountInputs = document.querySelectorAll('input[type="number"][name="amount"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value <= 0 || isNaN(value)) {
                this.setCustomValidity('Amount must be a positive number');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Calculate and display expense split in real-time
    const expenseForm = document.querySelector('form[action*="add_expense"]');
    if (expenseForm) {
        const amountInput = expenseForm.querySelector('input[name="amount"]');
        const participantCheckboxes = expenseForm.querySelectorAll('input[name="participants"]');
        
        function updateExpenseSplit() {
            const amount = parseFloat(amountInput.value) || 0;
            const participantCount = document.querySelectorAll('input[name="participants"]:checked').length;
            
            if (amount > 0 && participantCount > 0) {
                const perPerson = amount / participantCount;
                showExpenseSplit(amount, participantCount, perPerson);
            } else {
                hideExpenseSplit();
            }
        }

        function showExpenseSplit(total, count, perPerson) {
            let splitInfo = document.getElementById('expense-split-info');
            if (!splitInfo) {
                splitInfo = document.createElement('div');
                splitInfo.id = 'expense-split-info';
                splitInfo.className = 'alert alert-info mt-2';
                expenseForm.appendChild(splitInfo);
            }
            
            splitInfo.innerHTML = `
                <i class="fas fa-calculator me-2"></i>
                <strong>Split:</strong> ₹${total.toFixed(2)} ÷ ${count} people = 
                <strong>₹${perPerson.toFixed(2)} per person</strong>
            `;
        }

        function hideExpenseSplit() {
            const splitInfo = document.getElementById('expense-split-info');
            if (splitInfo) {
                splitInfo.remove();
            }
        }

        // Add event listeners
        if (amountInput) {
            amountInput.addEventListener('input', updateExpenseSplit);
        }
        
        participantCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', updateExpenseSplit);
        });
    }

    // Confirm deletion actions
    const deleteButtons = document.querySelectorAll('a[onclick*="confirm"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const confirmMessage = this.getAttribute('onclick').match(/confirm\('([^']+)'\)/)[1];
            
            if (confirm(confirmMessage)) {
                window.location.href = this.href;
            }
        });
        
        // Remove the inline onclick to prevent duplicate confirmation
        button.removeAttribute('onclick');
    });

    // Auto-focus on first input field in forms
    const firstInput = document.querySelector('form input[type="text"]:not([readonly])');
    if (firstInput) {
        firstInput.focus();
    }

    // Add loading states to buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                
                // Re-enable after 3 seconds as a failsafe
                setTimeout(function() {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 3000);
            });
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.querySelector('form');
            if (form && !form.querySelector('button[type="submit"]').disabled) {
                form.submit();
            }
        }
    });

    // Smooth scroll for navigation
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Utility functions
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    // Add to toast container or create one
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    toastContainer.appendChild(toast);

    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Export function for settlement data
function downloadSettlementData(groupId) {
    fetch(`/export_settlement/${groupId}`)
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `settlement_${data.group_name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showToast('Settlement data downloaded successfully!', 'success');
        })
        .catch(error => {
            console.error('Error downloading settlement data:', error);
            showToast('Error downloading settlement data', 'danger');
        });
}
