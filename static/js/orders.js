document.addEventListener("DOMContentLoaded", function () {
    const orderCards = document.querySelectorAll('.table-card');

    let lastCheckedBox = null;

    function updateInputs(checkbox) {
        const card = checkbox.closest('.table-card');
        const id = card.querySelector('.order-id').textContent.trim();
        const restaurantID = card.querySelector('.order-restaurant-id').textContent.trim();
        const orderDate = card.querySelector('.order-date').textContent.trim();
        const orderStatus = card.querySelector('.order-status').textContent.trim();
        const salesQty = card.querySelector('.sales-qty').textContent.trim();
        const salesAmount = card.querySelector('.sales-amount').textContent.trim();

        document.getElementById('order-id').value = id;
        document.getElementById('order-restaurant-id').value = restaurantID;
        document.getElementById('order-date').value = orderDate;
        document.getElementById('order-status').value = orderStatus;
        document.getElementById('sales-qty').value = salesQty;
        document.getElementById('sales-amount').value = salesAmount;
        document.getElementById('update-order-id').value = id;
    }

    function clearInputs() {
        document.getElementById('order-id').value = '';
        document.getElementById('order-restaurant-id').value = '';
        document.getElementById('order-date').value = '';
        document.getElementById('order-status').value = '';
        document.getElementById('sales-qty').value = '';
        document.getElementById('sales-amount').value = '';
        document.getElementById('update-order-id').value = '';
    }

    function handleCheckboxChange(event) {
        const checkbox = event.target;
        if (checkbox.checked) {
            lastCheckedBox = checkbox;
            updateInputs(checkbox);
        } else if (lastCheckedBox === checkbox) {
            lastCheckedBox = null;
            const selectedCheckboxes = Array.from(document.querySelectorAll('#order-list input[type="checkbox"]:checked'));
            if (selectedCheckboxes.length > 0) {
                lastCheckedBox = selectedCheckboxes[selectedCheckboxes.length - 1];
                updateInputs(lastCheckedBox);
            } else {
                clearInputs();
            }
        }
    }

    orderCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});

let matchedCards = [];
let currentMatchIndex = 0;

function searchOrder() {
    const idInput = document.getElementById('order-id').value.trim();
    const restaurantIDInput = document.getElementById('order-restaurant-id').value.trim();
    const orderDateInput = document.getElementById('order-date').value.trim();
    const orderStatusInput = document.getElementById('order-status').value.trim();
    const salesQtyInput = document.getElementById('order-sales-quantity').value.trim();
    const salesAmountInput = document.getElementById('order-sales-amount').value.trim();
    
    const cards = document.querySelectorAll('.table-card');
    matchedCards = [];
    currentMatchIndex = -1;

    if (!idInput && !restaurantIDInput && !orderDateInput && 
        !orderStatusInput && !salesQtyInput && !salesAmountInput) {
        alert("Please enter at least one search criterion.");
        return;
    }

    cards.forEach(card => card.classList.remove('highlight'));

    cards.forEach(card => {
        const id = card.querySelector('.order-id').textContent.trim();
        const restaurantID = card.querySelector('.order-restaurant-id').textContent.trim();
        const orderDate = card.querySelector('.order-date').textContent.trim();
        const orderStatus = card.querySelector('.order-status').textContent.trim();
        const salesQty = card.querySelector('.order-sales-quantity').textContent.trim();
        const salesAmount = card.querySelector('.order-sales-amount').textContent.trim();

        if (
            (!idInput || id === idInput) &&
            (!restaurantIDInput || restaurantID === restaurantIDInput) &&
            (!orderDateInput || orderDate === orderDateInput) &&
            (!orderStatusInput || orderStatus.toLowerCase() === orderStatusInput.toLowerCase()) &&
            (!salesQtyInput || salesQty === salesQtyInput) &&
            (!salesAmountInput || salesAmount === salesAmountInput)
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
        alert("No orders found matching the criteria.");
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
    document.getElementById('order-id').value = "";
    document.getElementById('order-restaurant-id').value = "";
    document.getElementById('order-date').value = "";
    document.getElementById('order-status').value = "";
    document.getElementById('sales-qty').value = "";
    document.getElementById('sales-amount').value = "";

    document.getElementById('clear-filter').value = "true";
    document.getElementById('order-form').submit();

    document.querySelectorAll('.table-card').forEach(card => card.classList.remove('highlight'));
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);

    matchedCards = [];
    currentMatchIndex = 0;

    document.getElementById('navigation').classList.add('hidden');
}

function collectSelected() {
    const selectedOrders = [];
    const checkboxes = document.querySelectorAll('#order-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedOrders.push(checkbox.value);
    });

    document.getElementById('selected-orders').value = selectedOrders.join(',');
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