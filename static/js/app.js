// BZD Taper Generator Web App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the app
    initializeApp();
    
    // Set default start date to today
    document.getElementById('start_date').value = new Date().toISOString().split('T')[0];
    
    // Load medications
    loadMedications();
});

function initializeApp() {
    // Form submission handler
    document.getElementById('taperForm').addEventListener('submit', handleFormSubmit);
    
    // Medication change handler
    document.getElementById('medication').addEventListener('change', handleMedicationChange);
}

async function loadMedications() {
    try {
        const response = await fetch('/api/medications');
        const medications = await response.json();
        
        const select = document.getElementById('medication');
        medications.forEach(med => {
            const option = document.createElement('option');
            option.value = med;
            option.textContent = med.charAt(0).toUpperCase() + med.slice(1);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading medications:', error);
        showError('Failed to load medications');
    }
}

function handleMedicationChange(event) {
    const medication = event.target.value;
    if (medication) {
        loadStrengths(medication);
    }
}

async function loadStrengths(medication) {
    try {
        const response = await fetch(`/api/strengths/${medication}`);
        const strengths = await response.json();
        
        // Update dose input with available strengths as placeholder
        const doseInput = document.getElementById('dose');
        if (strengths.length > 0) {
            doseInput.placeholder = `Available: ${strengths.join(', ')} mg`;
        }
    } catch (error) {
        console.error('Error loading strengths:', error);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Show loading state
    showLoading(true);
    hideResults();
    
    // Collect form data
    const formData = {
        medication: document.getElementById('medication').value,
        dose: parseFloat(document.getElementById('dose').value),
        speed: document.getElementById('speed').value,
        start_date: document.getElementById('start_date').value,
        frequency: document.getElementById('frequency').value
    };
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
        } else {
            showError(result.error || 'Failed to generate taper plan');
        }
    } catch (error) {
        console.error('Error generating taper plan:', error);
        showError('Network error. Please try again.');
    } finally {
        showLoading(false);
    }
}

function displayResults(result) {
    // Display warning if present
    const warningAlert = document.getElementById('warningAlert');
    const warningMessage = document.getElementById('warningMessage');
    
    if (result.warning) {
        warningMessage.textContent = result.warning;
        warningAlert.style.display = 'block';
    } else {
        warningAlert.style.display = 'none';
    }
    
    // Display patient instructions
    const patientInstructions = document.getElementById('patientInstructions');
    patientInstructions.innerHTML = result.patient_instructions.map(line => 
        `<p class="mb-1">${line}</p>`
    ).join('');
    
    // Display schedule summary
    const scheduleSummary = document.getElementById('scheduleSummary');
    scheduleSummary.innerHTML = `
        <div class="alert alert-info">
            <strong>${result.ehr_summary}</strong>
        </div>
        <div class="schedule-timeline">
            ${result.plan.map(step => formatScheduleStep(step)).join('')}
        </div>
    `;
    
    // Display pharmacy orders
    const pharmacyOrders = document.getElementById('pharmacyOrders');
    pharmacyOrders.innerHTML = result.pharmacy_orders.map(order => `
        <div class="card mb-2">
            <div class="card-body">
                <h6 class="card-title">${order.date}</h6>
                <p class="card-text"><strong>${order.product}</strong></p>
                <p class="card-text">${order.sig}</p>
                <p class="card-text text-muted">${order.dispense}</p>
            </div>
        </div>
    `).join('');
    
    // Display pill count
    const pillCount = document.getElementById('pillCount');
    pillCount.innerHTML = Object.entries(result.pill_summary).map(([strength, count]) => `
        <div class="pill-count-item">
            <span class="pill-strength">Diazepam ${strength} mg</span>
            <span class="pill-quantity">${Math.round(count)} tablets</span>
        </div>
    `).join('');
    
    // Show results with animation
    showResults();
}

function formatScheduleStep(step) {
    const dosingSchedule = Object.entries(step.dosing_schedule).map(([time, combo]) => {
        const doseStr = Object.entries(combo).map(([strength, count]) => 
            `${count} × ${strength}mg`
        ).join(' + ');
        return `<div class="dose-combo">${time}: ${doseStr}</div>`;
    }).join('');
    
    return `
        <div class="schedule-step">
            <h6>${step.week_label}</h6>
            <p><strong>${step.start_date} to ${step.end_date}</strong></p>
            <p>Daily dose: <strong>${step.dose_mg} mg</strong> (${step.dosing_frequency})</p>
            ${dosingSchedule}
            ${step.note ? `<p class="text-muted"><em>${step.note}</em></p>` : ''}
        </div>
    `;
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    const generateBtn = document.getElementById('generateBtn');
    
    if (show) {
        loading.style.display = 'block';
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    } else {
        loading.style.display = 'none';
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Taper Plan';
    }
}

function showResults() {
    const results = document.getElementById('results');
    results.style.display = 'block';
    results.classList.add('fade-in');
}

function hideResults() {
    const results = document.getElementById('results');
    results.style.display = 'none';
    results.classList.remove('fade-in');
    // Also hide warning alert
    document.getElementById('warningAlert').style.display = 'none';
}

function showError(message) {
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    document.getElementById('errorMessage').textContent = message;
    errorModal.show();
}

// Export functions
function exportToPDF() {
    // Implementation for PDF export
    alert('PDF export functionality will be implemented in the next version.');
}

function exportToCSV() {
    // Implementation for CSV export
    alert('CSV export functionality will be implemented in the next version.');
}

function printSchedule() {
    window.print();
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function validateForm() {
    const medication = document.getElementById('medication').value;
    const dose = document.getElementById('dose').value;
    const startDate = document.getElementById('start_date').value;
    
    if (!medication || !dose || !startDate) {
        showError('Please fill in all required fields.');
        return false;
    }
    
    if (parseFloat(dose) <= 0) {
        showError('Dose must be greater than 0.');
        return false;
    }
    
    return true;
}

// Add form validation
document.getElementById('taperForm').addEventListener('submit', function(event) {
    if (!validateForm()) {
        event.preventDefault();
    }
}); 