document.addEventListener("DOMContentLoaded", function () {
    const userCards = document.querySelectorAll('.table-card');

    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.user-id').textContent.trim();
        const name = card.querySelector('.name').textContent.trim();
        const email = card.querySelector('.email').textContent.trim();
        const password = card.querySelector('.password').textContent.trim();
        const age = card.querySelector('.age').textContent.trim();
        const gender = card.querySelector('.gender').textContent.trim();

        document.getElementById('user-id').value = id;
        document.getElementById('name').value = name;
        document.getElementById('email').value = email;
        document.getElementById('password').value = password;
        document.getElementById('age').value = age;
        document.getElementById('gender').value = gender;
        document.getElementById('update-user-id').value = id;
    }

    function clearInputs() {
        document.getElementById('user-id').value = '';
        document.getElementById('name').value = '';
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        document.getElementById('age').value = '';
        document.getElementById('gender').value = '';
        document.getElementById('update-user-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
        } else if (lastCheckedBox === checkbox) {
            lastCheckedBox = null;
            const selectedCheckboxes = Array.from(document.querySelectorAll('#user-list input[type="checkbox"]:checked'));
            if (selectedCheckboxes.length > 0) {
                lastCheckedBox = selectedCheckboxes[selectedCheckboxes.length - 1];
                updateInputs(lastCheckedBox);
            } else {
                clearInputs();
            }
        }
    }

    userCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchUser() {
    const idInput = document.getElementById('user-id').value.trim();
    const nameInput = document.getElementById('name').value.trim();
    const emailInput = document.getElementById('email').value.trim();
    const passwordInput = document.getElementById('password').value.trim();
    const ageInput = document.getElementById('age').value.trim();
    const genderInput = document.getElementById('gender').value.trim();

    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !nameInput && !emailInput &&
        !passwordInput && !ageInput && !genderInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.user-id').textContent.toLowerCase();
        const name = card.querySelector('.name').textContent.toLowerCase();
        const email = card.querySelector('.email').textContent.toLowerCase();
        const password = card.querySelector('.password').textContent.toLowerCase();
        const age = card.querySelector('.age').textContent.toLowerCase();
        const gender = card.querySelector('.gender').textContent.toLowerCase();

        if (
            (!idInput || id === idInput) &&
            (!nameInput || name.includes(nameInput)) &&
            (!emailInput || email === emailInput) &&
            (!passwordInput || password === passwordInput) &&
            (!ageInput || age === ageInput) &&
            (!genderInput || gender === genderInput)
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
        alert("No users found matching the criteria.");
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
    document.getElementById('user-id').value = "";
    document.getElementById('name').value = "";
    document.getElementById('email').value = "";
    document.getElementById('password').value = "";
    document.getElementById('age').value = "";
    document.getElementById('gender').value = "";

    document.getElementById('clear-filter').value = "true";
    document.getElementById('user-form').submit();

    document.querySelectorAll('.table-card').forEach(card => card.classList.remove('highlight'));
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);

    matchedCards = [];
    currentMatchIndex = 0;

    document.getElementById('navigation').classList.add('hidden');
}

function collectSelected() {
    const selectedUsers = [];
    const checkboxes = document.querySelectorAll('#user-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedUsers.push(checkbox.value);
    });

    document.getElementById('selected-users').value = selectedUsers.join(',');
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