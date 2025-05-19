let firebaseApp = null;

document.addEventListener("DOMContentLoaded", async function () {
    // ----------------- Firebase Init ------------------
    
                    // Bring your Firebase Credentials Here

    // ----------------- LOGIN ------------------
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const email = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            clearErrors();
            let isValid = true;

            if (email === '') {
                displayError('username', 'Email is required');
                isValid = false;
            }

            if (password === '') {
                displayError('password', 'Password is required');
                isValid = false;
            }

            if (!isValid) return;

            try {
                const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
                const token = await userCredential.user.getIdToken();
                localStorage.setItem("token", token);
                alert("Login successful!");
                window.location.href = "/index.html";
            } catch (error) {
                alert("Login failed: " + error.message);
            }
        });
    }

    // ----------------- SIGNUP ------------------
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();
            const confirmPassword = document.getElementById("confirm_password").value.trim();

            clearErrors();
            let isValid = true;

            if (username === '') {
                displayError('username', 'Username is required');
                isValid = false;
            } else if (username.length < 3) {
                displayError('username', 'Username must be at least 3 characters');
                isValid = false;
            }

            if (email === '') {
                displayError('email', 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email)) {
                displayError('email', 'Please enter a valid email address');
                isValid = false;
            }

            if (password === '') {
                displayError('password', 'Password is required');
                isValid = false;
            } else if (password.length < 6) {
                displayError('password', 'Password must be at least 6 characters');
                isValid = false;
            }

            if (confirmPassword === '') {
                displayError('confirm_password', 'Please confirm your password');
                isValid = false;
            } else if (password !== confirmPassword) {
                displayError('confirm_password', 'Passwords do not match');
                isValid = false;
            }

            if (!isValid) return;

            try {
                const userCredential = await firebase.auth().createUserWithEmailAndPassword(email, password);
                console.log(userCredential.user);
                
                await userCredential.user.updateProfile({ displayName: username });
                alert("Signup successful!");
                window.location.href = "/login.html";
            } catch (error) {
                displayError('email', error.message);
            }
        });
    }

    // ----------------- Helpers ------------------
    function displayError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.textContent = message;

        field.classList.add('error');
        field.style.borderColor = '#e74c3c';
        field.parentNode.appendChild(errorDiv);
    }

    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
            field.style.borderColor = '';
        });
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ----------------- Password Visibility ------------------
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function () {
            const passwordField = document.getElementById(this.getAttribute('data-toggle'));
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
});




















































































