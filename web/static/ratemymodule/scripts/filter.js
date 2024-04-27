document.addEventListener("DOMContentLoaded", function() {
    const buttonColor = getComputedStyle(document.documentElement).getPropertyValue('--button-color');
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color');

    const stars = document.querySelectorAll('.filter-rating-star');

    stars.forEach(function(star, index) {
        star.addEventListener('click', function() {
            stars.forEach(function(s, i) {
                if (i <= index) {
                    s.setAttribute('data-selected', 'true');
                    s.style.stroke = buttonColor;
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
            currentURL.searchParams.set("rating", ratingStarsNumber.toString());
        }
        if (filterYear !== '' && !isNaN(filterYear) && Number.isInteger(parseFloat(filterYear))) {
            currentURL.searchParams.set("year", filterYear);
        }

        const selectedTags = [];
        // Get the text content of elements with the "clicked" class
        const clickedElements = document.querySelectorAll('.filter-drop-down-element.clicked');
        clickedElements.forEach(function(element) {
            selectedTags.push(element.textContent.trim());
        });

        // Add selected tags to the URL
        if (selectedTags.length > 0) {
            currentURL.searchParams.set("tags", selectedTags.join(','));
        }

        currentURL.searchParams.delete("action");

        // Redirect to the modified URL
        window.location.href = currentURL.toString();
    }

    filterButton.addEventListener('click', performFilter);

    // Function to handle click event on filter-drop-down-element
    function handleTagSelection(event) {
        const target = event.target;
        target.classList.toggle('clicked');
    }

    // Add event listener to each filter-drop-down-element
    const filterDropDownElements = document.querySelectorAll('.filter-drop-down-element');
    filterDropDownElements.forEach(function(element) {
        element.addEventListener('click', handleTagSelection);
    });
});
