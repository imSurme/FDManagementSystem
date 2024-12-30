document.addEventListener("DOMContentLoaded", function () {
    const foodCards = document.querySelectorAll('.table-card');
    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.food-id')?.textContent.trim() || '';
        const name = card.querySelector('.food-name')?.textContent.trim() || '';
        const type = card.querySelector('.food-type')?.textContent.trim() || '';

        document.getElementById('food-id').value = id;
        document.getElementById('food-name').value = name;
        document.getElementById('food-type').value = type;
        document.getElementById('update-food-id').value = id;
    }

    function clearInputs() {
        document.getElementById('food-id').value = '';
        document.getElementById('food-name').value = '';
        document.getElementById('food-type').value = '';
        document.getElementById('update-food-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            foodCards.forEach(card => {
                const otherCheckbox = card.querySelector('input[type="checkbox"]');
                if (otherCheckbox !== checkbox) {
                    otherCheckbox.checked = false;
                }
            });
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
            
            const card = checkbox.closest('.table-card');
            const foodId = card.querySelector('.food-id').textContent.trim();
            document.getElementById('update-food-id').value = foodId;
        } else {
            lastCheckedBox = null;
            clearInputs();
            document.getElementById('update-food-id').value = '';
        }
    }

    foodCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

function collectSelected() {
    const selectedCheckboxes = document.querySelectorAll('.table-card input[type="checkbox"]:checked');
    const selectedIds = Array.from(selectedCheckboxes).map(checkbox => {
        const card = checkbox.closest('.table-card');
        return card.querySelector('.food-id').textContent.trim();
    });
    
    if (selectedIds.length === 0) {
        alert("Please select at least one food item.");
        return false;
    }
    
    document.getElementById('selected-food-items').value = selectedIds.join(',');
    return true;
}

let matchedCards = [];
let currentMatchIndex = 0;

function searchFood() {
    const idInput = document.getElementById('food-id').value.trim().toLowerCase();
    const nameInput = document.getElementById('food-name').value.trim().toLowerCase();
    const typeInput = document.getElementById('food-type').value.trim();
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !nameInput && !typeInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.food-id').textContent.toLowerCase();
        const name = card.querySelector('.food-name').textContent.toLowerCase();
        const type = card.querySelector('.food-type').textContent;

        if (
            (!idInput || id.includes(idInput)) &&
            (!nameInput || name.includes(nameInput)) &&
            (!typeInput || type === typeInput)
        ) {
            matchedCards.push(card);
        }
    });

    if (matchedCards.length > 0) {
        document.getElementById('navigation').classList.toggle('hidden', matchedCards.length === 1);
        goToNextMatch();
    } else {
        document.getElementById('navigation').classList.add('hidden');
        alert("No food items found matching the criteria.");
    }
}

function goToNextMatch() {
    if (currentMatchIndex >= 0 && currentMatchIndex < matchedCards.length) {
        matchedCards[currentMatchIndex].classList.remove('highlight');
    }

    currentMatchIndex = (currentMatchIndex + 1) % matchedCards.length;
    const nextCard = matchedCards[currentMatchIndex];

    nextCard.classList.add('highlight');
    nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearSearch() {
    document.getElementById('food-id').value = "";
    document.getElementById('food-name').value = "";
    document.getElementById('food-type').value = "";
    
    document.getElementById('form-action').value = 'clear';
    document.getElementById('food-form').submit();

    document.querySelectorAll('.table-card').forEach(card => card.classList.remove('highlight'));
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);

    matchedCards = [];
    currentMatchIndex = 0;

    document.getElementById('navigation').classList.add('hidden');
}

const scrollTopBtn = document.getElementById("scrollTopBtn");

function checkScrollPosition() {
    if (window.scrollY > 100) {
        scrollTopBtn.classList.add("visible");
    } else {
        scrollTopBtn.classList.remove("visible");
    }
}

window.addEventListener("load", checkScrollPosition);
window.addEventListener("scroll", checkScrollPosition);

scrollTopBtn.addEventListener("click", function() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});

function toggleSortMenu(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const sortMenu = document.getElementById('sort-menu');
    const overlay = document.getElementById('overlay');
    const button = event.target.closest('.sort-button');
    
    sortMenu.classList.toggle('hidden');
    overlay.classList.toggle('hidden');

    if (!sortMenu.classList.contains('hidden')) {
        const buttonRect = button.getBoundingClientRect();
        
        const top = buttonRect.bottom + window.scrollY;
        const left = buttonRect.left;
        
        sortMenu.style.top = `${top}px`;
        sortMenu.style.left = `${left}px`;
        
        const menuRect = sortMenu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        
        if (menuRect.right > viewportWidth) {
            sortMenu.style.left = `${viewportWidth - menuRect.width - 20}px`;
        }
    }
}

// Merge all DOMContentLoaded event listeners into one
document.addEventListener("DOMContentLoaded", function() {
    const foodForm = document.getElementById('food-form');
    const foodCards = document.querySelectorAll('.table-card');
    let lastCheckedBox = null;
    
    // Add event listener for sort button
    const sortButton = document.querySelector('.sort-button');
    if (sortButton) {
        sortButton.addEventListener('click', toggleSortMenu);
    }

    // Add event listener for overlay to close the sort menu
    const overlay = document.getElementById('overlay');
    const sortMenu = document.getElementById('sort-menu');
    if (overlay) {
        overlay.addEventListener('click', function() {
            sortMenu.classList.add('hidden');
            overlay.classList.add('hidden');
        });
    }

    // Close sort menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.sort-button') && 
            !event.target.closest('.sort-menu') && 
            !sortMenu.classList.contains('hidden')) {
            sortMenu.classList.add('hidden');
            overlay.classList.add('hidden');
        }
    });

    // Prevent clicks inside the sort menu from closing it
    sortMenu.addEventListener('click', function(event) {
        event.stopPropagation();
    });

    // Add event listeners for action buttons
    ['add-button', 'delete-button', 'update-button', 'filter-button'].forEach(buttonClass => {
        const button = document.querySelector('.' + buttonClass);
        if (button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const action = this.getAttribute('value');
                
                if (action === 'delete' && !collectSelected()) {
                    return;
                }
                
                if (action === 'update' && !document.getElementById('update-food-id').value) {
                    alert('Please select a food item to update.');
                    return;
                }
                
                document.getElementById('form-action').value = action;
                foodForm.submit();
            });
        }
    });

    // Rest of your existing DOMContentLoaded code...
    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.food-id')?.textContent.trim() || '';
        const name = card.querySelector('.food-name')?.textContent.trim() || '';
        const type = card.querySelector('.food-type')?.textContent.trim() || '';

        document.getElementById('food-id').value = id;
        document.getElementById('food-name').value = name;
        document.getElementById('food-type').value = type;
        document.getElementById('update-food-id').value = id;
    }

    function clearInputs() {
        document.getElementById('food-id').value = '';
        document.getElementById('food-name').value = '';
        document.getElementById('food-type').value = '';
        document.getElementById('update-food-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            foodCards.forEach(card => {
                const otherCheckbox = card.querySelector('input[type="checkbox"]');
                if (otherCheckbox !== checkbox) {
                    otherCheckbox.checked = false;
                }
            });
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
            
            const card = checkbox.closest('.table-card');
            const foodId = card.querySelector('.food-id').textContent.trim();
            document.getElementById('update-food-id').value = foodId;
        } else {
            lastCheckedBox = null;
            clearInputs();
            document.getElementById('update-food-id').value = '';
        }
    }

    foodCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
}); 