document.addEventListener("DOMContentLoaded", function () {
    ////////////////////////////////Navbar Toggle//////////////////////////////////////
    document.getElementById("navbar-toggle").addEventListener("click", function() {
        const navbarLinks = document.getElementById("navbar-links");
        const toggleIcon = document.getElementById("navbar-toggle");

        navbarLinks.classList.toggle("active");
        toggleIcon.classList.toggle("active"); 
    });
    const inputs = document.querySelectorAll(".input");

    function focusFunc() {
        let parent = this.parentNode;
        parent.classList.add("focus");
    }

    function blurFunc() {
        let parent = this.parentNode;
        if (this.value == "") {
            parent.classList.remove("focus");
        }
    }

    inputs.forEach((input) => {
        input.addEventListener("focus", focusFunc);
        input.addEventListener("blur", blurFunc);
    });
});