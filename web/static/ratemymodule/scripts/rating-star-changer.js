document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll('.filter-rating-star');
    const unselectedColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color');

    stars.forEach(function(star, index) {
        star.addEventListener('click', function() {
            stars.forEach(function(s, i) {
                if (i <= index) {
                    s.style.stroke = '#7F4FD9';
                    s.style.fill = '#C7A9FF';
                    s.style.fillOpacity = '100%';
                } else {
                    s.style.removeProperty('stroke');
                    s.style.removeProperty('fill');
                    s.style.removeProperty('fill-opacity');
                }
            });
        });
    });
});
