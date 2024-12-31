document.addEventListener("DOMContentLoaded", function () {
    /////////////Signup-Signin Mode////////////////////

    const sign_in_btn = document.querySelector("#sign-in-btn");
    const sign_up_btn = document.querySelector("#sign-up-btn");
    const container = document.querySelector(".container");

    sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
    });

    sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
    });

    ////////////////////////////Password Eye ////////////////////////////////////////////
    document.getElementById("toggle-password").addEventListener("click", function () {
        var passwordField = document.getElementById("password");
        var eyeIcon = document.getElementById("toggle-password");

        if (passwordField.type === "password") {
            passwordField.type = "text";
            eyeIcon.classList.remove("fa-eye");
            eyeIcon.classList.add("fa-eye-slash");
        } else {
            passwordField.type = "password";
            eyeIcon.classList.remove("fa-eye-slash");
            eyeIcon.classList.add("fa-eye");
        }
    });

    ///////////////////////////////Signup Password eye///////////////////////////////////// 
    document.getElementById("Signup-toggle-password").addEventListener("click", function () {
        var passwordField = document.getElementById("SignUpPassword");
        var eyeIcon = document.getElementById("Signup-toggle-password");
    
        if (passwordField.type === "password") {
        passwordField.type = "text";
        eyeIcon.classList.remove("fa-eye");
        eyeIcon.classList.add("fa-eye-slash");
        } else {
        passwordField.type = "password";
        eyeIcon.classList.remove("fa-eye-slash");
        eyeIcon.classList.add("fa-eye");
        }
    });

    ////////////////////////////////Navbar Toggle//////////////////////////////////////
    document.getElementById("navbar-toggle").addEventListener("click", function() {
        const navbarLinks = document.getElementById("navbar-links");
        const toggleIcon = document.getElementById("navbar-toggle");
    
        navbarLinks.classList.toggle("active");
        toggleIcon.classList.toggle("active"); 
    });

    /////////////////////////////// Account Activation //////////////////////////////////

    var successMessage = document.getElementById('success-message');

    if (successMessage && !sessionStorage.getItem('toastDisplayed')) {
        Toastify({
            text: successMessage.innerText,
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "green",
            close: true
        }).showToast();
        sessionStorage.setItem('toastDisplayed', 'true');
    }

    ////////////////////////////////////////LOGIN ///////////////////////////////////////
    
    document.querySelector('.sign-in-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const username = document.querySelector('#Username').value.trim();
        const password = document.querySelector('#password').value.trim();

        if (!username || !password) {
            Toastify({
                text: "Please fill the required fields.",
                duration: 3000,
                backgroundColor: "red",
                close: true,
                gravity: "top",
                position: "right"
            }).showToast();
            return;
        }

        const data = new FormData();
        data.append('username', username);
        data.append('password', password);

        fetch('/login', {
            method: 'POST',
            body: data,
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                Toastify({
                    text: data.error,
                    duration: 3000,
                    backgroundColor: "red",
                    close: true,
                    gravity: "top",
                    position: "right"
                }).showToast();
            }
        })
        .catch(error => {
            Toastify({
                text: "An error occurred. Please try again.",
                duration: 3000,
                backgroundColor: "red",
                close: true,
                gravity: "top",
                position: "right"
            }).showToast();
        });
    });

    ////////////////////////////////////////SIGNUP //////////////////////////////////////
    document.querySelector('.sign-up-form').addEventListener('submit', function (event) {
        event.preventDefault(); 
    
        const username = document.querySelector('#SignUpUsername').value.trim();
        const password = document.querySelector('#SignUpPassword').value.trim();
        const email = document.querySelector('#email').value.trim();
        
        if (!username || !password ||!email) {
            Toastify({
                text: "Please fill the required fields.",
                duration: 3000,
                backgroundColor: "red",
                close: true,
                gravity: "top",
                position: "right"
            }).showToast();
            return;
        }

        const data = new FormData();
        data.append('username', username);
        data.append('password', password);
        data.append('email', email);
    
        fetch('/signup', {
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Toastify({
                    text: "User registered successfully!",
                    duration: 3000,
                    backgroundColor: "green",
                    close: true,
                    gravity: "top",
                    position: "right"
                }).showToast();
            } else {
                Toastify({
                    text: data.error,
                    duration: 3000,
                    backgroundColor: "red",
                    close: true,
                    gravity: "top",
                    position: "right"
                }).showToast();
            }
        })
        .catch(error => {
            Toastify({
                text: "An error occurred. Please try again.",
                duration: 3000,
                backgroundColor: "red",
                close: true,
                gravity: "top",
                position: "right"
            }).showToast();
        });
    });

    ///////////////////////Forgot Password///////////////////////////

    document.getElementById("forgot-password-link").addEventListener("click", function(event) {
        event.preventDefault();
        const formContent = document.getElementById("form-content");
  
        formContent.innerHTML = `
          <h2 class="title">Reset Password</h2>
          <p>Please enter your email to get the link, where you can reset the password</p>
          <div class="input-field">
            <i class="fas fa-envelope"></i>
            <input id="email-input" type="email" placeholder="Email" />
          </div>
          <input id="submit-forgot" type="button" value="Submit" class="btn solid" />
          <a href="#" class="back-to-login" id="back-to-login-link">Back to Login</a>
        `;

        document.getElementById("submit-forgot").addEventListener("click", function() {
            const email = document.getElementById("email-input").value;
        
            if (!email) {
                Toastify({
                    text: "Please enter your registered email address",
                    duration: 3000,
                    backgroundColor: "red",
                    close: true,
                    gravity: "top",
                    position: "right"
                }).showToast();
                return;
            }
        
            fetch('/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    Toastify({
                        text: data.message,
                        duration: 3000,
                        backgroundColor: "green",
                        close: true,
                        gravity: "top",
                        position: "right"
                    }).showToast();
                } else {
                    Toastify({
                        text: data.error,
                        duration: 3000,
                        backgroundColor: "red",
                        close: true,
                        gravity: "top",
                        position: "right"
                    }).showToast();
                }
            })
            .catch(error => {
                Toastify({
                    text: "An unexpected error occurred.",
                    duration: 3000,
                    backgroundColor: "red",
                    close: true,
                    gravity: "top",
                    position: "right"
                }).showToast();
            });
        });        
  
        document.getElementById("back-to-login-link").addEventListener("click", function(event) {
          event.preventDefault();
          location.reload();
        });
      });
});  