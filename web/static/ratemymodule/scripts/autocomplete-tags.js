document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tag-input-container').forEach(container => {
        const inputType = container.dataset.tagType; // Will be 'tool_tags', 'topic_tags', or 'other_tags'
        const input = container.querySelector('input[type="text"]');
        const hiddenInput = container.querySelector('input[type="hidden"]');
        container.selectedTags = hiddenInput.value ? hiddenInput.value.split(',') : [];

        console.log(inputType + " - Initial selected tags:", container.selectedTags); // Debugging statement

        input.addEventListener('input', function () {
            let dropdown = container.querySelector('.autocomplete-results');
            if (!dropdown) {
                dropdown = document.createElement('div');
                dropdown.classList.add('autocomplete-results');
                container.appendChild(dropdown);
            }

            dropdown.innerHTML = '';
            if (input.value.trim() !== '') {
                fetchAutocompleteResults(input.value.trim(), inputType, dropdown, container, hiddenInput);
            }
        });

        input.addEventListener('blur', function () {
            setTimeout(() => {
                let dropdown = container.querySelector('.autocomplete-results');
                if (dropdown) {
                    dropdown.remove();
                }
            }, 200);
        });
    });
});

function fetchAutocompleteResults(term, inputType, dropdown, container, hiddenInput) {
    const url = `/autocomplete/${inputType}?term=${encodeURIComponent(term)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            dropdown.innerHTML = '';
            data.forEach(tag => {
                if (!container.selectedTags.includes(String(tag.id))) {
                    let item = document.createElement('div');
                    item.classList.add('autocomplete-item');
                    item.textContent = tag.name;
                    item.dataset.tagId = tag.id;

                    item.addEventListener('click', function () {
                        if (!container.selectedTags.includes(String(tag.id))) {
                            container.selectedTags.push(String(tag.id));
                            updateHiddenInput(hiddenInput, container.selectedTags);
                            addSelectedTag(tag, container, hiddenInput); // Call addSelectedTag here
                            dropdown.innerHTML = ''; // Clear the dropdown after selection

                            console.log(inputType + " - Tag selected:", tag.name); // Debugging statement
                            console.log(inputType + " - Updated selected tags:", container.selectedTags); // Debugging statement
                        }
                    });

                    dropdown.appendChild(item);
                }
            });
        })
        .catch(error => console.error('Error:', error));
}

function updateHiddenInput(hiddenInput, selectedTags) {
    hiddenInput.value = selectedTags.join(',');
    console.log(hiddenInput.name + " - Hidden input updated to:", hiddenInput.value); // Debugging statement
}

function addSelectedTag(tag, container, hiddenInput) {
    const inputField = container.querySelector('input[type="text"]');
    const selectedTagsContainer = container.querySelector('.selected-tags-container');

    // Immediately clear the input field when a tag is selected
    inputField.value = '';
    // Optionally, you might want to trigger the 'change' event if there are listeners
    inputField.dispatchEvent(new Event('change'));

    let tagElement = document.createElement('div');
    tagElement.classList.add('selected-tag');
    tagElement.textContent = tag.name;

    let removeBtn = document.createElement('span');
    removeBtn.classList.add('remove-tag');
    removeBtn.innerHTML = '&times;';
    removeBtn.addEventListener('click', function () {
        let index = container.selectedTags.indexOf(String(tag.id));
        if (index > -1) {
            container.selectedTags.splice(index, 1);
            updateHiddenInput(hiddenInput, container.selectedTags);
            tagElement.remove();
        }
    });

    tagElement.appendChild(removeBtn);
    selectedTagsContainer.appendChild(tagElement);
}
