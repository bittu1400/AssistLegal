let firebaseApp = null;

document.addEventListener("DOMContentLoaded", async function () {
    try {
        // 1️⃣ Fetch Firebase config from backend (FastAPI)
        const response = await fetch("http://127.0.0.1:8000/firebase-config");
        if (!response.ok) throw new Error("Failed to fetch Firebase config");
        const config = await response.json();

        // 2️⃣ Initialize Firebase (v8 style)
        firebase.initializeApp(config);
        // firebaseApp = firebase.app();  // Optional: Get the default app instance

    } catch (error) {
        console.error("Firebase initialization failed:", error);
        alert("Error initializing Firebase. Please try again later.");
        return;
    }

    // Get Auth instance after initialization
    const auth = firebase.auth();

    // 🔒 Sign Up logic
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();
            const pattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
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
                displayError('email', 'Please enter a valid email');
                isValid = false;
            }

            if (password === '') {
                displayError('password', 'Password is required');
                isValid = false;
            } else if (!pattern.test(password)) {
                displayError('password','Password must be at least 8 characters long, with at least one uppercase letter, one number, and one special character.');
                isValid = false;
            }

            if (confirmPassword === '' || password !== confirmPassword) {
                displayError('confirm_password', 'Passwords do not match');
                isValid = false;
            }

            if (!isValid) return;

            try {
                const userCredential = await auth.createUserWithEmailAndPassword(email, password);
                await userCredential.user.updateProfile({ displayName: username });
                await userCredential.user.sendEmailVerification();
                showModal("Signup successful! Verification email sent.");
                // window.location.href = "/login.html";
            } catch (error) {
                displayError('email', error.message);
            }
        });
    

    }
    function showModal(message) {
        document.getElementById("modal-message").innerText = message;
        document.getElementById("custom-modal").classList.remove("hidden");
    }

    function closeModal() {
        document.getElementById("custom-modal").classList.add("hidden");
        window.location.href = "/login.html";
    }

    // 🔑 Login logic
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const email = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            clearErrors();
            if (!email || !password) {
                if (!email) displayError('username', 'Email is required');
                if (!password) displayError('password', 'Password is required');
                return;
            }

            try {
                const userCredential = await auth.signInWithEmailAndPassword(email, password);
                const token = await userCredential.user.getIdToken();
                localStorage.setItem("token", token);
                loginSuccess("Login successful!");
                // window.location.href = "/index.html";
            } catch (error) {
                loginFailed("Login failed\nEmail or Password doesn't match");
            }
        });
    }

    function loginSuccess() {
        document.getElementById("modal-message").innerText = "Login successful!";
        document.getElementById("custom-modal").classList.remove("hidden");

  // Redirect after clicking OK
    window.closeModal = function () {
    document.getElementById("custom-modal").classList.add("hidden");
    window.location.href = "/index.html"; 
  };
}

function loginFailed(message) {
    document.getElementById("modal-message").innerText = message;
    document.getElementById("custom-modal").classList.remove("hidden");

    // Close modal on OK
    window.closeModal = function () {
        document.getElementById("custom-modal").classList.add("hidden");
    };
}

    // 🔑 Forgot Password logic
    const forgotPasswordLink = document.getElementById("forgot-password-link");
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", async function (event) {
            event.preventDefault();
            const email = prompt("Please enter your email to reset password:");
            if (email) {
                try {
                    await auth.sendPasswordResetEmail(email);
                    forget("Password reset email sent. Please check your inbox.");
                } catch (error) {
                    alert("Error sending reset email: " + error.message);
                }
            }
        });
    }


function forget(message) {
    document.getElementById("modal-message").innerText = message;
    document.getElementById("custom-modal").classList.remove("hidden");

    // Reset closeModal behavior
    window.closeModal = function () {
        document.getElementById("custom-modal").classList.add("hidden");
    };
}

    // 🔒 Token updates and auth state monitoring
    auth.onIdTokenChanged(async (user) => {
        if (user) {
            const token = await user.getIdToken();
            localStorage.setItem("token", token);
        }
    });

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

    auth.onAuthStateChanged(user => {
        if (!user) {
            localStorage.removeItem("token");
        }
    });

    // Utility functions
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
});














































































