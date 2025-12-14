// static/js/profile.js - Profile management with multi-role support

async function loadProfile() {
    try {
        const response = await fetch('/api/profile/get');
        const data = await response.json();
        
        if (data.exists) {
            // Profile exists, show main interface
            document.getElementById('profile-setup').style.display = 'none';
            document.querySelector('.tab-container').style.display = 'flex';
            
            // Store profile data globally
            window.userProfile = data;
            
            // Load initial content
            if (typeof loadMemories === 'function') {
                loadMemories();
            }
        } else {
            // Show profile setup
            document.getElementById('profile-setup').style.display = 'block';
            document.querySelector('.tab-container').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function saveProfile() {
    try {
        const name = document.getElementById('user-name').value.trim();
        const birthDate = document.getElementById('birth-date').value;
        const birthPlace = document.getElementById('birth-place').value.trim();
        
        // Get all checked family roles
        const roleCheckboxes = document.querySelectorAll('input[name="family-role"]:checked');
        const roles = Array.from(roleCheckboxes).map(cb => cb.value);
        
        // Validation
        if (!name) {
            alert('Please enter your name');
            return;
        }
        
        if (!birthDate) {
            alert('Please enter your birth date');
            return;
        }
        
        if (roles.length === 0) {
            alert('Please select at least one family role');
            return;
        }
        
        // Join roles with comma for storage
        const familyRole = roles.join(', ');
        
        const response = await fetch('/api/profile/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                birth_date: birthDate,
                family_role: familyRole,
                birth_place: birthPlace
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Hide setup, show main interface
            document.getElementById('profile-setup').style.display = 'none';
            document.querySelector('.tab-container').style.display = 'flex';
            
            // Store profile
            window.userProfile = {
                name: name,
                birth_date: birthDate,
                family_role: familyRole,
                birth_place: birthPlace
            };
            
            // Show welcome message
            alert(`Welcome to The Circle, ${name}!`);
            
            // Load initial content
            if (typeof loadMemories === 'function') {
                loadMemories();
            }
        } else {
            alert('Error saving profile: ' + data.message);
        }
        
    } catch (error) {
        console.error('Error saving profile:', error);
        alert('Error saving profile. Please try again.');
    }
}

function editProfile() {
    // Show profile setup with current values
    if (window.userProfile) {
        document.getElementById('user-name').value = window.userProfile.name || '';
        document.getElementById('birth-date').value = window.userProfile.birth_date || '';
        document.getElementById('birth-place').value = window.userProfile.birth_place || '';
        
        // Check the appropriate role checkboxes
        if (window.userProfile.family_role) {
            const roles = window.userProfile.family_role.split(',').map(r => r.trim().toLowerCase());
            const checkboxes = document.querySelectorAll('input[name="family-role"]');
            checkboxes.forEach(cb => {
                cb.checked = roles.includes(cb.value.toLowerCase());
            });
        }
    }
    
    document.getElementById('profile-setup').style.display = 'block';
    document.querySelector('.tab-container').style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
});
