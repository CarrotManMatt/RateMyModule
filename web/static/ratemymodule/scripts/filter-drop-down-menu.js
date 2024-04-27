document.addEventListener('DOMContentLoaded', function() {
    var dropDownButton = document.getElementById('filter-drop-down-button');

    dropDownButton.addEventListener('click', function(){
        document.getElementById("filter-drop-down-content").classList.toggle("active");
    });

    var dropDownContent = document.getElementById("filter-drop-down-content");

    document.addEventListener('click', function(event) {
        var isClickInsideDropDown = dropDownButton.contains(event.target) || dropDownContent.contains(event.target);
        if (!isClickInsideDropDown) {
            dropDownContent.classList.remove("active");
        }
    });

    var searchField = document.getElementById('filter-tag-search-input');

    searchField.addEventListener('keyup', function(){
        var input, filter, divs, i, txtValue;
        input = document.getElementById("filter-tag-search-input");
        filter = input.value.toUpperCase();
        divs = document.querySelectorAll(".filter-drop-down-element");
        for (i = 0; i < divs.length; i++) {
            txtValue = divs[i].textContent || divs[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                divs[i].style.display = "";
            } else {
                divs[i].style.display = "none";
            }
        }
    });

});
