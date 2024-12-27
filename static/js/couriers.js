document.addEventListener("DOMContentLoaded", function () {
    const courierCards = document.querySelectorAll('.table-card');

    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.courier-id').textContent.trim();
        const name = card.querySelector('.courier-name').textContent.trim();
        const gender = card.querySelector('.courier-gender').textContent.trim();
        const birthDate = card.querySelector('.courier-birthdate').textContent.trim();
        const restaurantId = card.querySelector('.courier-restaurant-id').textContent.trim();

        document.getElementById('courier-id').value = id;
        document.getElementById('courier-name').value = name;
        document.getElementById('courier-gender').value = gender;
        document.getElementById('courier-birthdate').value = birthDate;
        document.getElementById('courier-restaurant-id').value = restaurantId;
        document.getElementById('update-courier-id').value = id;
    }

    function clearInputs() {
        document.getElementById('courier-id').value = '';
        document.getElementById('courier-name').value = '';
        document.getElementById('courier-gender').value = '';
        document.getElementById('courier-birthdate').value = '';
        document.getElementById('courier-restaurant-id').value = '';
        document.getElementById('update-courier-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
        } else if (lastCheckedBox === checkbox) {
            lastCheckedBox = null;
            const selectedCheckboxes = Array.from(document.querySelectorAll('#courier-list input[type="checkbox"]:checked'));
            if (selectedCheckboxes.length > 0) {
                lastCheckedBox = selectedCheckboxes[selectedCheckboxes.length - 1];
                updateInputs(lastCheckedBox);
            } else {
                clearInputs();
            }
        }
    }

    courierCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchCourier() {
    const idInput = document.getElementById('courier-id').value.trim().toLowerCase();
    const nameInput = document.getElementById('courier-name').value.trim().toLowerCase();
    const genderInput = document.getElementById('courier-gender').value.trim().toLowerCase();
    const birthdateInput = document.getElementById('courier-birthdate').value.trim().toLowerCase();
    const restaurantIdInput = document.getElementById('courier-restaurant-id').value.trim().toLowerCase();
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !nameInput && !genderInput && !birthdateInput && !restaurantIdInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.courier-id').textContent.toLowerCase();
        const name = card.querySelector('.courier-name').textContent.toLowerCase();
        const gender = card.querySelector('.courier-gender').textContent.toLowerCase();
        const birthdate = card.querySelector('.courier-birthdate').textContent.toLowerCase();
        const restaurantId = card.querySelector('.courier-restaurant-id').textContent.toLowerCase();

        if (
            (!idInput || id === idInput) &&
            (!nameInput || name.includes(nameInput)) &&
            (!genderInput || gender === genderInput) &&
            (!birthdateInput || birthdate === birthdateInput) &&
            (!restaurantIdInput || restaurantId === restaurantIdInput)
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
        alert("No courier found matching all the criteria exactly.");
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
    document.getElementById('courier-id').value = "";
    document.getElementById('courier-name').value = "";
    document.getElementById('courier-gender').value = "";
    document.getElementById('courier-birthdate').value = "";
    document.getElementById('courier-restaurant-id').value = "";

    document.getElementById('clear-filter').value = "true";
    document.getElementById('courier-form').submit();

    document.querySelectorAll('.table-card').forEach(card => card.classList.remove('highlight'));
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);

    matchedCards = [];
    currentMatchIndex = 0;

    document.getElementById('navigation').classList.add('hidden');
}

function collectSelected() {
    const selectedCouriers = [];
    const checkboxes = document.querySelectorAll('#courier-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedCouriers.push(checkbox.value);
    });

    document.getElementById('selected-couriers').value = selectedCouriers.join(',');
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