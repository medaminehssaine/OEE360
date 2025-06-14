// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
  const tocItems = document.querySelectorAll('.rtd-toc-item');
  const tocLinks = document.querySelectorAll('.rtd-toc-item a');
  
  // Add click handlers to TOC items
  tocLinks.forEach(link => {
      link.addEventListener('click', function(e) {
          e.preventDefault();
          
          // Remove active class from all items
          tocItems.forEach(item => {
              item.classList.remove('rtd-toc-item-active');
          });
          
          // Add active class to clicked item's parent
          this.closest('.rtd-toc-item').classList.add('rtd-toc-item-active');
          
          // Smooth scroll to target
          const targetId = this.getAttribute('href').substring(1);
          const targetElement = document.getElementById(targetId);
          
          if (targetElement) {
              targetElement.scrollIntoView({
                  behavior: 'smooth',
                  block: 'start'
              });
          }
      });
  });
  
  // Update active navigation item on scroll
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              const id = entry.target.id;
              const correspondingLink = document.querySelector(`a[href="#${id}"]`);
              
              if (correspondingLink) {
                  // Remove active class from all items
                  tocItems.forEach(item => {
                      item.classList.remove('rtd-toc-item-active');
                  });
                  
                  // Add active class to corresponding item
                  correspondingLink.closest('.rtd-toc-item').classList.add('rtd-toc-item-active');
              }
          }
      });
  }, {
      rootMargin: '-20% 0px -70% 0px'
  });
  
  // Observe all sections
  const sections = document.querySelectorAll('h1[id], h2[id], h3[id]');
  sections.forEach(section => {
      observer.observe(section);
  });
});