document.addEventListener("DOMContentLoaded", function () {
    const restaurantCards = document.querySelectorAll('.table-card');

    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.restaurant-id').textContent.trim();
        const userId = card.querySelector('.user-id').textContent.trim();
        const name = card.querySelector('.restaurant-name').textContent.trim();
        const city = card.querySelector('.restaurant-city').textContent.trim();
        const rating = card.querySelector('.restaurant-rating').textContent.trim();
        const ratingCount = card.querySelector('.restaurant-rating-count').textContent.trim();
        const averageCost = card.querySelector('.restaurant-average-cost').textContent.trim();
        const cuisine = card.querySelector('.restaurant-cuisine').textContent.trim();
        const address = card.querySelector('.restaurant-address').textContent.trim();

        document.getElementById('restaurant-id').value = id;
        document.getElementById('user-id').value = userId;
        document.getElementById('restaurant-name').value = name;
        document.getElementById('restaurant-city').value = city;
        document.getElementById('restaurant-rating').value = rating;
        document.getElementById('restaurant-rating-count').value = ratingCount;
        document.getElementById('restaurant-average-cost').value = averageCost;
        document.getElementById('restaurant-cuisine').value = cuisine;
        document.getElementById('restaurant-address').value = address;
        document.getElementById('update-restaurant-id').value = id;
    }

    function clearInputs() {
        document.getElementById('restaurant-id').value = '';
        document.getElementById('user-id').value = '';
        document.getElementById('restaurant-name').value = '';
        document.getElementById('restaurant-city').value = '';
        document.getElementById('restaurant-rating').value = '';
        document.getElementById('restaurant-rating-count').value = '';
        document.getElementById('restaurant-average-cost').value = '';
        document.getElementById('restaurant-cuisine').value = '';
        document.getElementById('restaurant-address').value = '';
        document.getElementById('update-restaurant-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
        } else if (lastCheckedBox === checkbox) {
            lastCheckedBox = null;
            const selectedCheckboxes = Array.from(document.querySelectorAll('#restaurant-list input[type="checkbox"]:checked'));
            if (selectedCheckboxes.length > 0) {
                lastCheckedBox = selectedCheckboxes[selectedCheckboxes.length - 1];
                updateInputs(lastCheckedBox);
            } else {
                clearInputs();
            }
        }
    }

    restaurantCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchRestaurant() {
    const idInput = document.getElementById('restaurant-id').value.trim().toLowerCase();
    const userIdInput = document.getElementById('user-id').value.trim().toLowerCase();
    const nameInput = document.getElementById('restaurant-name').value.trim().toLowerCase();
    const cityInput = document.getElementById('restaurant-city').value.trim().toLowerCase();
    const ratingInput = document.getElementById('restaurant-rating').value.trim().toLowerCase();
    const ratingCountInput = document.getElementById('restaurant-rating-count').value.trim().toLowerCase();
    const averageCostInput = document.getElementById('restaurant-average-cost').value.trim().toLowerCase();
    const cuisineInput = document.getElementById('restaurant-cuisine').value.trim().toLowerCase();
    const addressInput = document.getElementById('restaurant-address').value.trim().toLowerCase();
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !userIdInput && !nameInput && !cityInput && !ratingInput && !ratingCountInput && !averageCostInput && !cuisineInput && !addressInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.restaurant-id').textContent.toLowerCase();
        const userId = card.querySelector('.user-id').textContent.toLowerCase();
        const name = card.querySelector('.restaurant-name').textContent.toLowerCase();
        const city = card.querySelector('.restaurant-city').textContent.toLowerCase();
        const rating = card.querySelector('.restaurant-rating').textContent.toLowerCase();
        const ratingCount = card.querySelector('.restaurant-rating-count').textContent.toLowerCase();
        const averageCost = card.querySelector('.restaurant-average-cost').textContent.toLowerCase();
        const cuisine = card.querySelector('.restaurant-cuisine').textContent.toLowerCase();
        const address = card.querySelector('.restaurant-address').textContent.toLowerCase();

        if (
            (!idInput || id === idInput) &&
            (!userIdInput || userId === userIdInput) &&
            (!nameInput || name.includes(nameInput)) &&
            (!cityInput || city.includes(cityInput)) &&
            (!ratingInput || rating === ratingInput) &&
            (!ratingCountInput || ratingCount === ratingCountInput) &&
            (!averageCostInput || averageCost === averageCostInput) &&
            (!cuisineInput || cuisine.includes(cuisineInput)) &&
            (!addressInput || address.includes(addressInput))
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
        alert("No restaurant found matching all the criteria exactly.");
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
    // Basic form clearing
    document.getElementById('restaurant-id').value = "";
    document.getElementById('user-id').value = "";
    document.getElementById('restaurant-name').value = "";
    document.getElementById('restaurant-city').value = "";
    document.getElementById('restaurant-rating').value = "";
    document.getElementById('restaurant-rating-count').value = "";
    document.getElementById('restaurant-average-cost').value = "";
    document.getElementById('restaurant-cuisine').value = "";
    document.getElementById('restaurant-address').value = "";
    
    // Clear checkboxes and highlights
    document.querySelectorAll('.table-card').forEach(card => card.classList.remove('highlight'));
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);
    
    // Submit the form with clear action
    const form = document.getElementById('restaurant-form');
    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = 'clear';
    form.appendChild(actionInput);
    
    form.submit();
}

// Separate the unload handler into its own function
function clearOnUnload() {
    fetch('/restaurant_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'action=clear&clear_filter=true',
        keepalive: true
    });
}

// Update the unload event listener
window.addEventListener('beforeunload', clearOnUnload);

function collectSelected() {
    const selectedRestaurants = [];
    const checkboxes = document.querySelectorAll('#restaurant-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedRestaurants.push(checkbox.value);
    });

    document.getElementById('selected-restaurants').value = selectedRestaurants.join(',');
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

// Add window unload event handler
window.addEventListener('beforeunload', clearOnUnload);
