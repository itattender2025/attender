const forms = document.querySelector(".forms");
const pwShowHide = document.querySelectorAll(".eye-icon");
const links = document.querySelectorAll(".link");
const forgotPasswordLink = document.querySelector(".forgotpassword-link"); // Updated selector name
const forgotPasswordBox = document.querySelector(".forgotpasswordform");
const loginBox = document.querySelector(".login");
const registerBox = document.querySelector(".signup");
const backBtn = document.querySelector(".backbtn");

// Password show/hide functionality
pwShowHide.forEach(eyeIcon => {
    eyeIcon.addEventListener("click", () => {
        let pwFields = eyeIcon.parentElement.parentElement.querySelectorAll(".password");
        
        pwFields.forEach(password => {
            if (password.type === "password") {
                password.type = "text";
                eyeIcon.classList.replace("bx-hide", "bx-show");
            } else {
                password.type = "password";
                eyeIcon.classList.replace("bx-show", "bx-hide");
            }
        });
    });
});

// Toggle between login and signup forms
links.forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault(); // Preventing default link behavior
        forms.classList.toggle("show-signup"); // Toggle between forms
    });
});

// Show Forgot Password form and hide others
if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent default behavior
        console.log("Forgot Password link clicked"); // Debugging log
        forgotPasswordBox.style.display = "block";
        registerBox.style.display = "none";
        loginBox.style.display = "none";
    });
}

// Back button in Forgot Password form
if (backBtn) {
    backBtn.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent default behavior
        console.log("Back button clicked"); // Debugging log
        forgotPasswordBox.style.display = "none";
        loginBox.style.display = "block";
        registerBox.style.display = "block"; // Reset both login and signup to be visible again
    });
}