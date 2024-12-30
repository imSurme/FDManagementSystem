document.addEventListener("DOMContentLoaded", function () {
    const menuCards = document.querySelectorAll('.table-card');
    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.menu-id').textContent.trim();
        const foodId = card.querySelector('.food-id').textContent.trim();
        const cuisine = card.querySelector('.menu-cuisine').textContent.trim();
        const price = card.querySelector('.menu-price').textContent.trim();
        const restaurantId = card.querySelector('.menu-restaurant-id').textContent.trim();

        document.getElementById('menu-id').value = id;
        document.getElementById('food-id').value = foodId;
        document.getElementById('menu-cuisine').value = cuisine;
        document.getElementById('menu-price').value = price;
        document.getElementById('menu-restaurant-id').value = restaurantId;
        document.getElementById('update-menu-id').value = id;
    }

    function clearInputs() {
        document.getElementById('menu-id').value = '';
        document.getElementById('food-id').value = '';
        document.getElementById('menu-cuisine').value = '';
        document.getElementById('menu-price').value = '';
        document.getElementById('menu-restaurant-id').value = '';
        document.getElementById('update-menu-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
        } else if (lastCheckedBox === checkbox) {
            lastCheckedBox = null;
            const selectedCheckboxes = Array.from(document.querySelectorAll('#menu-list input[type="checkbox"]:checked'));
            if (selectedCheckboxes.length > 0) {
                lastCheckedBox = selectedCheckboxes[selectedCheckboxes.length - 1];
                updateInputs(lastCheckedBox);
            } else {
                clearInputs();
            }
        }
    }

    menuCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchMenu() {
    const idInput = document.getElementById('menu-id').value.trim().toLowerCase();
    const foodNameInput = document.getElementById('food-name').value.trim().toLowerCase();
    const cuisineInput = document.getElementById('menu-cuisine').value.trim().toLowerCase();
    const priceInput = document.getElementById('menu-price').value.trim().toLowerCase();
    const restaurantIdInput = document.getElementById('menu-restaurant-id').value.trim().toLowerCase();
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !foodNameInput && !cuisineInput && !priceInput && !restaurantIdInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.menu-id').textContent.toLowerCase();
        const foodName = card.querySelector('.menu-name').textContent.toLowerCase();
        const cuisine = card.querySelector('.menu-cuisine').textContent.toLowerCase();
        const price = card.querySelector('.menu-price').textContent.toLowerCase();
        const restaurantId = card.querySelector('.menu-restaurant-id').textContent.toLowerCase();

        if (
            (!idInput || id.includes(idInput)) &&
            (!foodNameInput || foodName.includes(foodNameInput)) &&
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

function collectSelected() {
    const selectedItems = [];
    const checkboxes = document.querySelectorAll('#menu-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedItems.push(checkbox.value);
    });

    document.getElementById('selected-menu-items').value = selectedItems.join(',');
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
