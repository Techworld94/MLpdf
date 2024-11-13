document.addEventListener("DOMContentLoaded", function () {
    ////////////////////////////////Navbar Toggle//////////////////////////////////////
    document.getElementById("navbar-toggle").addEventListener("click", function() {
        const navbarLinks = document.getElementById("navbar-links");
        const toggleIcon = document.getElementById("navbar-toggle");

        navbarLinks.classList.toggle("active");
        toggleIcon.classList.toggle("active"); 
    });
    var learnMoreBtn = document.getElementById("learnMoreBtn");
    var moreContent = document.getElementById("moreContent");

    learnMoreBtn.addEventListener("click", function() {
        if (moreContent.style.display === "none") {
            moreContent.style.display = "block";
            learnMoreBtn.style.display = "none";
        } else {
            moreContent.style.display = "none";
        }
    });
});