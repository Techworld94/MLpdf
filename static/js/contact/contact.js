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

    document.querySelector("form").addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });
    
            const result = await response.json();
            
            if (result.status === "success") {
                Toastify({
                    text: result.message,
                    duration: 3000,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "green",
                    close: true,
                }).showToast();
                form.reset();
            } else {
                Toastify({
                    text: result.message,
                    duration: 3000,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "red",
                    close: true,
                }).showToast();
            }
        } catch (error) {
            Toastify({
                text: "An unexpected error occurred. Please try again later.",
                duration: 3000,
                gravity: "top",
                position: "right",
                backgroundColor: "red",
                close: true,
            }).showToast();
        }
    });
    
});