document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tag-input-container').forEach(containerElement => {
        const inputType = containerElement.dataset.tagType;
        const input = containerElement.querySelector('input[type="text"]');
        const hiddenInput = containerElement.querySelector('input[type="hidden"]');

        containerElement.selectedTags = hiddenInput.value ? hiddenInput.value.split(',') : [];
        containerElement.customTags = [];

        input.addEventListener('input', function () {
            let dropdown = containerElement.querySelector('.autocomplete-results');
            if (!dropdown) {
                dropdown = document.createElement('div');
                dropdown.classList.add('autocomplete-results');
                containerElement.appendChild(dropdown);
            }

            dropdown.innerHTML = '';
            if (input.value.trim() !== '') {
                fetchAutocompleteResults(input.value.trim(), inputType, dropdown, containerElement, hiddenInput, input);
            }
        });

        input.addEventListener('blur', function () {
            setTimeout(() => {
                let dropdown = containerElement.querySelector('.autocomplete-results');
                if (dropdown) {
                    dropdown.remove();
                }
                input.value = '';
            }, 200);
        });
    });

    // Clear errors when typing in the input fields of modals
    document.querySelectorAll('.modal-content input[type="text"]').forEach(inputElement => {
        inputElement.addEventListener('input', () => {
            const modalType = inputElement.id.split('TagNameInput')[0];
            const errorElement = document.getElementById(`${modalType}TagError`);
            if (errorElement) {
                errorElement.style.display = 'none';
                errorElement.textContent = '';
            }
        });
    });

    // Event listeners for modal form submissions
    ['tool', 'topic', 'other'].forEach(type => {
        const formId = `${type}TagSubmissionForm`;
        document.getElementById(formId).addEventListener('submit', function (e) {
            e.preventDefault();
            submitCustomTagHandler(e, type);
        });
    });
});

function fetchAutocompleteResults(term, inputType, dropdown, containerElement, hiddenInput, input) {
    // Construct the URL for the autocomplete endpoint
    const url = `/autocomplete/${inputType}?term=${encodeURIComponent(term)}`;

    // Fetch the autocomplete results and process them
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Populate the autocomplete dropdown
            dropdown.innerHTML = '';
            data.forEach(tag => {
                if (!containerElement.selectedTags.includes(String(tag.id))) {
                    let item = document.createElement('div');
                    item.classList.add('autocomplete-item');
                    item.textContent = tag.name;
                    item.dataset.tagId = tag.id;

                    item.addEventListener('click', function () {
                        if (!containerElement.selectedTags.includes(String(tag.id))) {
                            containerElement.selectedTags.push(String(tag.id));
                            addSelectedTag(tag, containerElement, hiddenInput, false);
                            dropdown.innerHTML = ''; // Clear the dropdown after selection
                            input.value = ''; // Clear the input field
                        }
                    });

                    dropdown.appendChild(item);
                }
            });

            // Add an 'Add your own' option
            let addYourOwnOption = document.createElement('div');
            addYourOwnOption.classList.add('autocomplete-item', 'add-your-own-tag');
            addYourOwnOption.textContent = 'Add your own';
            addYourOwnOption.addEventListener('click', function (e) {
                e.stopPropagation(); // Prevent click event propagation
                let modalType = inputType.split('_')[0];
                let modal = document.getElementById(`${modalType}TagSubmissionModal`);
                if (modal) {
                    modal.style.display = 'block';
                }
                input.value = ''; // Clear the input field
                document.getElementById(`${modalType}TagNameInput`).value = '';
            });

            dropdown.appendChild(addYourOwnOption);
        })
        .catch(error => {
            console.error('Error fetching autocomplete results:', error);
        });
}

function submitCustomTagHandler(e, modalType) {
    e.preventDefault();
    const container = document.querySelector(`.tag-input-container[data-tag-type="${modalType}_tags"]`);
    const hiddenInput = container.querySelector('input[type="hidden"]');
    const tagNameInput = document.getElementById(`${modalType}TagNameInput`);

    if (tagNameInput.value.trim() !== '') {
        submitCustomTag(tagNameInput.value.trim(), modalType, container, hiddenInput);
    } else {
        console.error('Tag name input is empty or not found.');
    }
}

function submitCustomTag(tagValue, modalType, container, hiddenInput) {
    const errorElement = document.getElementById(`${modalType}TagError`);
    errorElement.style.display = 'none';

    if (!isValidTag(tagValue)) {
        showError(errorElement, 'Invalid tag format. Please match the requested format.');
        return;
    }

    if (container.selectedTags.includes(tagValue) || container.customTags.some(tag => tag.name === tagValue)) {
        showError(errorElement, `Tag "${tagValue}" already exists.`);
        return;
    }

    const newTag = {
        id: `custom-${Date.now()}`,
        name: `custom-${tagValue}`
    };

    addSelectedTag(newTag, container, hiddenInput, true);

    closeModal(modalType);
}

function addSelectedTag(tag, container, hiddenInput, isCustom) {
    console.log(`Adding tag - isCustom: ${isCustom}, tag:`, tag);
    const tagIdString = String(tag.id); // Consistently handle IDs as strings
    const selectedTagsContainer = container.querySelector('.selected-tags-container');

    const tagName = isCustom ? tag.name.replace(/^custom-/i, '') : tag.name;

    const tagElement = document.createElement('div');
    tagElement.classList.add('selected-tag');
    tagElement.textContent = tagName;
    tagElement.dataset.tagId = tagIdString;

    if (isCustom) {
        tagElement.classList.add('custom-tag');
        tagElement.title = 'Custom tag, pending verification';
        // Only add if not already present
        if (!container.customTags.some(t => t.id === tagIdString)) {
            container.customTags.push({...tag, id: tagIdString});
        }
    } else {
        // Only add if not already present
        if (!container.selectedTags.includes(tagIdString)) {
            container.selectedTags.push(tagIdString);
        }
    }

    const removeBtn = document.createElement('span');
    removeBtn.classList.add('remove-tag');
    removeBtn.textContent = '×';
    removeBtn.addEventListener('click', () => {
        removeTag(tagElement, container, hiddenInput);
    });

    tagElement.appendChild(removeBtn);
    selectedTagsContainer.appendChild(tagElement);

    // After adding a tag, update the list of tags in hidden input
    updateSelectedTags(hiddenInput, container, 'addSelectedTag');
}


function removeTag(tagElement, container, hiddenInput) {
    const tagIdToRemove = tagElement.dataset.tagId;
    // Remove from selected or custom tags based on presence
    container.selectedTags = container.selectedTags.filter(id => id !== tagIdToRemove);
    container.customTags = container.customTags.filter(tag => tag.id !== tagIdToRemove);

    tagElement.remove();

    // Update tag lists after removal
    updateSelectedTags(hiddenInput, container, 'removeTag');
}

function updateSelectedTags(hiddenInput, container, caller) {
    const selectedTagIds = container.selectedTags;  // Predefined tags' IDs
    const customTagNames = container.customTags.map(tag => `custom-${tag.name}`);  // Custom tags formatted

    // Combine selected tag IDs and custom tag names
    const allTags = [...selectedTagIds, ...customTagNames];

    // Ensure no duplicates or empty names
    const uniqueTags = [...new Set(allTags.filter(name => name !== ''))];

    // Update the hidden input value to a comma-separated string
    hiddenInput.value = uniqueTags.join(',');

    console.log(`DEBUG - Updating hidden input for ${hiddenInput.name}. New value:`, hiddenInput.value, `Called by: ${caller}`);
}


function isValidTag(tag) {
    const tagRegex = /^[a-zA-Z0-9!?¿¡' +&()#.-]{2,60}$/;
    return tagRegex.test(tag);
}

function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

function closeModal(modalType) {
    const modal = document.getElementById(`${modalType}TagSubmissionModal`);
    if (modal) {
        modal.style.display = 'none';
        const errorElement = document.getElementById(`${modalType}TagError`);
        if (errorElement) {
            errorElement.style.display = 'none';
            errorElement.textContent = '';
        }
        const input = modal.querySelector('input[type="text"]');
        if (input) input.value = '';
    }
}
