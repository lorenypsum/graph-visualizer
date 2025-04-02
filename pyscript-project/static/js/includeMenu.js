document.addEventListener("DOMContentLoaded", function () {
    const menuContainer = document.getElementById("menu-container");
    if (menuContainer) {
      fetch("/menu")
        .then((response) => response.text())
        .then((html) => {
          menuContainer.innerHTML = html;
        })
        .catch((error) => {
          console.error("Error loading menu:", error);
        });
    }
  });