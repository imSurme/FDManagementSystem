document.addEventListener("DOMContentLoaded", function () {
    const menuCards = document.querySelectorAll('.table-card');
    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.menu-id')?.textContent.trim() || '';
        const name = card.querySelector('.menu-name')?.textContent.trim() || '';
        const type = card.querySelector('.menu-type')?.textContent.trim() || '';
        const cuisine = card.querySelector('.menu-cuisine')?.textContent.trim() || '';
        const price = card.querySelector('.menu-price')?.textContent.trim() || '';
        const restaurantId = card.querySelector('.menu-restaurant-id')?.textContent.trim() || '';

        document.getElementById('menu-id').value = id;
        document.getElementById('food-name').value = name;
        document.getElementById('food-type').value = type === 'Veg' ? 'Veg' : 'Non-veg';
        document.getElementById('menu-cuisine').value = cuisine;
        document.getElementById('menu-price').value = price;
        document.getElementById('menu-restaurant-id').value = restaurantId;
        document.getElementById('update-menu-id').value = id;
    }

    function clearInputs() {
        document.getElementById('menu-id').value = '';
        document.getElementById('food-name').value = '';
        document.getElementById('food-type').value = '';
        document.getElementById('menu-cuisine').value = '';
        document.getElementById('menu-price').value = '';
        document.getElementById('menu-restaurant-id').value = '';
        document.getElementById('update-menu-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            menuCards.forEach(card => {
                const otherCheckbox = card.querySelector('input[type="checkbox"]');
                if (otherCheckbox !== checkbox) {
                    otherCheckbox.checked = false;
                }
            });
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
            
            const card = checkbox.closest('.table-card');
            const menuId = card.querySelector('.menu-id').textContent.trim();
            document.getElementById('update-menu-id').value = menuId;
        } else {
            lastCheckedBox = null;
            clearInputs();
            document.getElementById('update-menu-id').value = '';
        }
    }

    menuCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

function collectSelected() {
    const selectedCheckboxes = document.querySelectorAll('.table-card input[type="checkbox"]:checked');
    const selectedIds = Array.from(selectedCheckboxes).map(checkbox => {
        const card = checkbox.closest('.table-card');
        return card.querySelector('.menu-id').textContent.trim();
    });
    
    if (selectedIds.length === 0) {
        alert("Please select at least one menu item.");
        return false;
    }
    
    console.log("Selected IDs:", selectedIds);
    document.getElementById('selected-menu-items').value = selectedIds.join(',');
    console.log("Form value:", document.getElementById('selected-menu-items').value);
    return true;
}

document.addEventListener("DOMContentLoaded", function() {
    const deleteButton = document.querySelector('.delete-button');
    if (deleteButton) {
        deleteButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (collectSelected()) {
                const form = document.getElementById('menu-form');
                // Ensure the action is set to delete
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = 'delete';
                form.appendChild(actionInput);
                
                console.log("Form being submitted with data:", new FormData(form));
                form.submit();
            }
        });
    }
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchMenu() {
    const idInput = document.getElementById('menu-id').value.trim().toLowerCase();
    const foodNameInput = document.getElementById('food-name').value.trim().toLowerCase();
    const foodTypeInput = document.getElementById('food-type').value.trim();
    const cuisineInput = document.getElementById('menu-cuisine').value.trim().toLowerCase();
    const priceInput = document.getElementById('menu-price').value.trim().toLowerCase();
    const restaurantIdInput = document.getElementById('menu-restaurant-id').value.trim().toLowerCase();
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !foodNameInput && !foodTypeInput && !cuisineInput && !priceInput && !restaurantIdInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.menu-id').textContent.toLowerCase();
        const foodName = card.querySelector('.menu-name').textContent.toLowerCase();
        const foodType = card.querySelector('.menu-type').textContent;
        const cuisine = card.querySelector('.menu-cuisine').textContent.toLowerCase();
        const price = card.querySelector('.menu-price').textContent.toLowerCase();
        const restaurantId = card.querySelector('.menu-restaurant-id').textContent.toLowerCase();

        if (
            (!idInput || id.includes(idInput)) &&
            (!foodNameInput || foodName.includes(foodNameInput)) &&
            (!foodTypeInput || foodType === foodTypeInput) &&
            (!cuisineInput || cuisine.includes(cuisineInput)) &&
            (!priceInput || price.includes(priceInput)) &&
            (!restaurantIdInput || restaurantId.includes(restaurantIdInput))
        ) {
            matchedCards.push(card);
        }
    });

    if (matchedCards.length > 0) {
        if (matchedCards.length === 1) {
            document.getElementById('navigation').classList.add('hidden');
        } else {
            document.getElementById('navigation').classList.remove('hidden');
        }
        goToNextMatch();
    } else {
        document.getElementById('navigation').classList.add('hidden');
        alert("No menu items found matching the criteria.");
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
    document.getElementById('menu-id').value = "";
    document.getElementById('food-name').value = "";
    document.getElementById('menu-cuisine').value = "";
    document.getElementById('menu-price').value = "";
    document.getElementById('menu-restaurant-id').value = "";

    document.getElementById('clear-filter').value = "true";
    document.getElementById('menu-form').submit();

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
    const sortMenu = document.getElementById('sort-menu');
    const overlay = document.getElementById('overlay');
    const isHidden = sortMenu.style.display === 'none' || !sortMenu.style.display;

    if (isHidden) {
        sortMenu.style.display = 'block';
        overlay.style.display = 'block';

        const buttonRect = event.target.getBoundingClientRect();
        sortMenu.style.top = `${buttonRect.top + window.scrollY}px`;
        sortMenu.style.left = `${buttonRect.right + 10}px`;
    } else {
        sortMenu.style.display = 'none';
        overlay.style.display = 'none';
    }
}

document.getElementById('overlay').addEventListener('click', function () {
    document.getElementById('sort-menu').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
});

document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.display = "none";
        }, 5000);
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const updateButton = document.querySelector('.update-button');
    if (updateButton) {
        updateButton.addEventListener('click', function(e) {
            e.preventDefault();
            const updateMenuId = document.getElementById('update-menu-id').value;
            if (!updateMenuId) {
                alert('Please select a menu item to update.');
                return;
            }
            
            const form = document.getElementById('menu-form');
            // Set the action value before submitting
            document.getElementById('form-action').value = 'update';
            
            const formData = new FormData(form);
            console.log('Form data being sent:', {
                action: formData.get('action'),
                update_menu_id: formData.get('update_menu_id'),
                name: formData.get('name'),
                food_type: formData.get('food_type'),
                cuisine: formData.get('cuisine'),
                price: formData.get('price'),
                restaurant_id: formData.get('restaurant_id')
            });
            
            form.submit();
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const addButton = document.querySelector('.add-button');
    if (addButton) {
        addButton.addEventListener('click', function(e) {
            e.preventDefault();
            const form = document.getElementById('menu-form');
            document.getElementById('form-action').value = 'add';
            form.submit();
        });
    }
});
