document.addEventListener("DOMContentLoaded", () => {
    const authForm = document.getElementById("authForm");
    const alertBox = document.getElementById("alert");
    const formTitle = document.getElementById("formTitle");
    const submitButton = document.getElementById("submitButton");
    const toggleForm = document.getElementById("toggleForm");

    if (!authForm || !alertBox || !formTitle || !submitButton || !toggleForm) {
        console.error("One or more required elements are missing from the HTML!");
        return;
    }

    let isLogin = true;

    toggleForm.addEventListener("click", () => {
        isLogin = !isLogin;
        formTitle.innerText = isLogin ? "Login" : "Register";
        submitButton.innerText = isLogin ? "Login" : "Register";
        toggleForm.innerText = isLogin ? "Register" : "Login";

        const masterKeyWrapper = document.getElementById("masterKeyWrapper");
        if (isLogin) {
            masterKeyWrapper.classList.add("hidden");
        } else {
            masterKeyWrapper.classList.remove("hidden");
        }

        alertBox.classList.add("hidden");
    });

    authForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const masterKey = document.getElementById("masterKey")?.value;

        if (!username || !password || (!isLogin && !masterKey)) {
            showAlert("Please fill in all fields.");
            return;
        }

        const url = isLogin
            ? "http://127.0.0.1:5001/api/login"
            : "http://127.0.0.1:5001/api/register";

        const payload = isLogin
            ? { username, password }
            : { username, password, master_key: masterKey };

        fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    showAlert(data.message, "success");
                    if (!isLogin) {
                        alert("Registration Successful! Please Login.");
                        toggleForm.click();
                    } else {
                        alert("Login Successful!");
                        // บันทึก Token และ User ID ลงใน localStorage
                        localStorage.setItem("authToken", data.token); // Save Token
                        localStorage.setItem("loggedInUserId", data.userId); // Save User ID
                        window.location.href = "http://127.0.0.1:5500/frontend/html/dashboard.html";
                    }
                } else {
                    showAlert(data.error || "An error occurred.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                showAlert("Failed to connect to the server.");
            });
    });

    function showAlert(message, type = "error") {
        alertBox.innerText = message;
        alertBox.classList.remove("hidden", "text-red-500", "text-green-500");
        alertBox.classList.add(type === "success" ? "text-green-500" : "text-red-500");
    }

    // เคลียร์ History
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {
        window.history.pushState(null, "", window.location.href);
    };

    // ถ้ามี Token ให้ Redirect ไปหน้า Dashboard
    const authToken = localStorage.getItem("authToken");
    if (authToken) {
        window.location.href = "http://127.0.0.1:5500/frontend/html/dashboard.html";
    }
});
