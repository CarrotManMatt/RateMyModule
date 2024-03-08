document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll('.filter-rating-star');
    const unselectedColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color');

    stars.forEach(function(star, index) {
        star.addEventListener('click', function() {
            stars.forEach(function(s, i) {
                if (i <= index) {
                    s.setAttribute('data-selected', 'true');
                    s.style.stroke = '#7F4FD9';
                    s.style.fill = '#C7A9FF';
                    s.style.fillOpacity = '100%';
                } else {
                    s.setAttribute('data-selected', 'false');
                    s.style.removeProperty('stroke');
                    s.style.removeProperty('fill');
                    s.style.removeProperty('fill-opacity');
                }
            });
        });
    });

    const filterButton = document.getElementById('filter-button');
    const yearInputBox = document.querySelector('.year-input-box');

    function performFilter() {
        const ratingStarsNumber = document.querySelectorAll('.filter-rating-star[data-selected="true"]').length;
        console.log(ratingStarsNumber);
        const filterYear = yearInputBox.value;

        // Get the current URL
        const currentURL = new URL(window.location.href);

        // Construct the filter parameters based on the selected criteria
        if (ratingStarsNumber > 0) {
            currentURL.searchParams.set("rating", ratingStarsNumber.toString())
        }
        if (filterYear !== '' && !isNaN(filterYear) && Number.isInteger(parseFloat(filterYear))) {
            currentURL.searchParams.set("year", filterYear)
        }
        currentURL.searchParams.delete("action");

        // Redirect to the modified URL
        window.location.href = currentURL.toString();
    }

    filterButton.addEventListener('click', performFilter);
});
