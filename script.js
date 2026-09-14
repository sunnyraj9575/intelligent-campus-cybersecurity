const steps = [...document.querySelectorAll('.step')];

steps.forEach((step) => {
  step.addEventListener('click', () => {
    steps.forEach((item) => item.classList.remove('active'));
    step.classList.add('active');
  });
});

const revealItems = document.querySelectorAll('.feature-card, .strip-stat, .workflow-copy, .workflow-visual');
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.animate(
        [{ opacity: 0, transform: 'translateY(18px)' }, { opacity: 1, transform: 'translateY(0)' }],
        { duration: 650, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards' },
      );
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

revealItems.forEach((item) => observer.observe(item));
