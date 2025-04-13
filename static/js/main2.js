/**
 * Main JavaScript file for the Disaster Awareness Portal
 */
document.addEventListener('DOMContentLoaded', function() {
    // Navigation active state based on scroll position
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    function setActiveLink() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollY >= (sectionTop - 100)) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }
    
    window.addEventListener('scroll', setActiveLink);
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70, // Adjust for navbar height
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // State selector for emergency contacts
    const stateSelector = document.getElementById('stateSelector');
    if (stateSelector) {
        stateSelector.addEventListener('change', function() {
            // Hide all contact sections
            document.querySelectorAll('.contact-section').forEach(section => {
                section.classList.add('d-none');
            });
            
            // Show the selected state's contacts
            const selectedState = this.value;
            const contactSection = document.getElementById(selectedState + '-contacts');
            
            // Fallback to national if not found
            if (contactSection) {
                contactSection.classList.remove('d-none');
            } else {
                document.getElementById('national-contacts').classList.remove('d-none');
            }
        });
    }
});