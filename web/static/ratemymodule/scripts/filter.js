document.addEventListener('DOMContentLoaded', function() {
    const filterButton = document.getElementById('filter-button');
    const yearInputBox = document.querySelector('.year-input-box');
    const ratingStars = document.querySelectorAll('.filter-rating-star');

    function performFilter() {
        const ratingStarsNumber = document.querySelectorAll('.filter-rating-star[stroke="#7F4FD9"]').length;
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

        // Redirect to the modified URL
        window.location.href = currentURL.toString();
    }

    filterButton.addEventListener('click', performFilter);
});
