// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('CrashStats loaded successfully!');
    
    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Country filter functionality
    const countryFilter = document.getElementById('countryFilter');
    if (countryFilter) {
        countryFilter.addEventListener('change', function() {
            console.log('Filter changed to:', this.value);
            // Add filtering logic here
        });
    }
});