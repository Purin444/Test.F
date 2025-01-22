fetch("../component/navbar.html")
.then((response) => response.text())
.then((html) => {
    document.getElementById("navbarContainer").innerHTML = html;

    // ผูก Event Listener ให้ปุ่ม Logout ใน navbar
    const logoutButton = document.getElementById("logoutButton");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            console.log("Navbar Logout button clicked");
            localStorage.removeItem("authToken");
            sessionStorage.clear();
            window.location.href = "../html/auth.html";
        });
    } else {
        console.error("Navbar Logout button not found");
    }
})
.catch((error) => console.error("Error loading navbar:", error));


fetch("../component/sidebar.html")
    .then((response) => response.text())
    .then((html) => {
        const sidebar = document.getElementById("sidebar");
        if (sidebar) {
            sidebar.innerHTML = html;
            console.log("Sidebar loaded successfully");

            // ดึง loggedInUserId และเรียกใช้ฟังก์ชัน loadUserProfile
            const loggedInUserId = localStorage.getItem("loggedInUserId");
            if (loggedInUserId) {
                loadUserProfile(loggedInUserId);
            } else {
                console.error("No loggedInUserId found in localStorage");
            }
        } else {
            console.error("Sidebar container not found");
        }
    })
    .catch((error) => console.error("Error loading sidebar:", error));

// ฟังก์ชัน loadUserProfile (ย้ายมาจาก auth.js หรือประกาศใน logout.js)
function loadUserProfile(userId) {
    fetch(`http://127.0.0.1:5001/api/auth_users/${userId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to fetch user data: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            const profilePic = document.querySelector(".profile-pic");
            const profileName = document.querySelector(".profile h1");

            if (data && data.username) {
                profileName.textContent = data.username;
            } else {
                profileName.textContent = "Guest";
            }

            if (profilePic) {
                profilePic.src = data.profile_picture || "../assets/image/user_2.png";
            }
        })
        .catch((error) => {
            console.error("Error loading user profile:", error);
        });
}

// เริ่มการทำงานเมื่อโหลดหน้า
document.addEventListener("DOMContentLoaded", () => {
  const authToken = localStorage.getItem("authToken");

  // ถ้าไม่มี Token ให้ Redirect ไปหน้า Login
  if (!authToken) {
    window.location.href = "http://127.0.0.1:5500/frontend/html/auth.html";
    return; // หยุดการโหลดข้อมูล
  }


  
});