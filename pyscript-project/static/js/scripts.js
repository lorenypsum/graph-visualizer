document.addEventListener('DOMContentLoaded', function() {
    const cartButton = document.getElementById('cart-button');
    const userButton = document.getElementById('user-button');

    if (cartButton) {
        cartButton.addEventListener('click', function() {
            window.location.href = '/cart';
        });
    }

    if (userButton) {
        userButton.addEventListener('click', function() {
            window.location.href = '/user';
        });
    }
});