document.addEventListener("DOMContentLoaded", function () {
    ////////////////////////////////Navbar Toggle//////////////////////////////////////
    document.getElementById("navbar-toggle").addEventListener("click", function() {
        const navbarLinks = document.getElementById("navbar-links");
        const toggleIcon = document.getElementById("navbar-toggle");

        navbarLinks.classList.toggle("active");
        toggleIcon.classList.toggle("active"); 
    });
});