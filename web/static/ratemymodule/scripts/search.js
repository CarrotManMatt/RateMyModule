document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.querySelector('.search-input');
    var searchIcon = document.getElementById('search-icon');

    function performSearch() {
        const query = searchInput.value;
        if (query !== ""){
            const currentURL = new URL(window.location.href);
            currentURL.searchParams.set("q", encodeURIComponent(query));
            window.location.href = currentURL.toString();
        }
    }

    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            performSearch();
        }
    });

    searchIcon.addEventListener('click', performSearch);
});
