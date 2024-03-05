document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.filter-rating-star');

    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            // Check if the star is already selected
            const isSelected = this.getAttribute('fill') === '#C7A9FF';

            // Iterate through all stars
            stars.forEach((s, i) => {
                if (i <= index) {
                    // Stars before and including the clicked star
                    s.setAttribute('stroke', '#7F4FD9');
                    s.setAttribute('fill', '#C7A9FF');
                    s.setAttribute('fill-opacity', '100%');
                } else {
                    // Stars after the clicked star
                    s.setAttribute('stroke', '#cbcbcb');
                    s.setAttribute('fill', '#cbcbcb');
                    s.setAttribute('fill-opacity', '39%');
                }
            });

            // Toggle the color based on selection
            if (isSelected) {
                // Change the color back to default
                this.setAttribute('stroke', '#cbcbcb');
                this.setAttribute('fill', '#cbcbcb');
                this.setAttribute('fill-opacity', '39%');
            } else {
                // Change the color to selected
                this.setAttribute('stroke', '#7F4FD9');
                this.setAttribute('fill', '#C7A9FF');
                this.setAttribute('fill-opacity', '100%');
            }
        });
    });
});
