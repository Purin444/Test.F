// ฟังก์ชันดึงข้อมูลจาก API
function fetchData(url) {
  return fetch(url)
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      alert('There was an issue fetching data, please try again later.');
    });
}

// แปลง Status Code เป็นข้อความ
function mapStatus(statusCode) {
  const statusMap = {
    0: "Check-In",
    1: "Check-Out",
    2: "Break Out",
    3: "Break In",
    4: "OT In",
    5: "OT Out"
  };
  return statusMap[statusCode] || "Unknown";
}

// ฟังก์ชันจัดการวันที่
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toISOString().split('T')[0];
}

// ดึงเวลา (นาที) จาก Timestamp
function getTimeFromTimestamp(dateStr) {
  const date = new Date(dateStr);
  return date.getHours() * 60 + date.getMinutes();
}

// ดึงข้อมูล Dashboard
function fetchDashboardData() {
  // ใช้ Promise.all เพื่อดึงข้อมูลหลายๆ ตัวพร้อมกัน
  Promise.all([
    fetchData('http://127.0.0.1:5001/api/users'),
    fetchData('http://127.0.0.1:5001/api/attendance')
  ])
  .then(([userData, attendanceData]) => {
    if (!userData || userData.length === 0) {
      console.error('No users found');
      return;
    }

    if (!attendanceData || attendanceData.length === 0) {
      console.error('No attendance data found');
      return;
    }

    // Map User ID เป็นชื่อ
    const userMap = {};
    userData.forEach(user => {
      userMap[user.user_id] = user.name || "No Name";
    });

    const totalEmployees = userData.length;

    // กรองข้อมูลวันนี้จาก attendanceData
    const today = new Date().toISOString().split('T')[0];
    const todaysLogs = attendanceData.filter(log => formatDate(log.timestamp) === today);

    const tableBody = document.getElementById("attendance-log-table");
    tableBody.innerHTML = ""; // เคลียร์ตาราง

    let onTimeCount = 0;
    let lateCount = 0;
    let absentCount = totalEmployees;

    const checkedOutUsers = new Set(); // เก็บ User ID ที่ Check-Out แล้ว
    const checkedInUsers = new Set(); // เก็บ User ID ที่ Check-In แล้ว

    todaysLogs.forEach(log => {
      const checkInTime = getTimeFromTimestamp(log.timestamp);

      if (log.status === 0) { // Check-In
        if (!checkedInUsers.has(log.user_id)) {
          checkedInUsers.add(log.user_id);
          absentCount--; // ลดจำนวน Absent
          onTimeCount++;
          if (checkInTime <= 9 * 60) {
            onTimeCount++; // เช็คอินก่อน 9:00 AM
          } else {
            lateCount++;
          }
        }
      }

      if (log.status === 1) { // Check-Out
        if (!checkedOutUsers.has(log.user_id) && checkedInUsers.has(log.user_id)) {
          checkedOutUsers.add(log.user_id);
          if (onTimeCount > 0) {
            onTimeCount--;
          }
        }
      }

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${log.user_id}</td>
        <td>${userMap[log.user_id] || "No Name"}</td>
        <td>${log.timestamp}</td>
        <td>${mapStatus(log.status)}</td>
      `;
      tableBody.appendChild(row);
    });

    document.getElementById("total-employees").innerHTML = `${totalEmployees}<br><span>Total Employee</span>`;
    document.getElementById("on-time").innerHTML = `${onTimeCount}<br><span>On Time</span>`;
    document.getElementById("late").innerHTML = `${lateCount}<br><span>Late</span>`;
    document.getElementById("absent").innerHTML = `${absentCount}<br><span>Absent</span>`;
  })
  .catch(error => {
    console.error('Error fetching data:', error);
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

  // ดึงข้อมูล Dashboard
  fetchDashboardData();

  // อัปเดตข้อมูลทุก 5 วินาที
  setInterval(fetchDashboardData, 10000);
});

function fetchDashboardOTRequests() {
  fetch('http://127.0.0.1:5001/api/ot-requests/')
      .then(response => response.json())
      .then(otRequests => {
          const otRequestTableBody = document.getElementById("otRequestTableSmall").querySelector("tbody");
          otRequestTableBody.innerHTML = ""; // ล้างตารางก่อนเติมข้อมูลใหม่

          // กรองเฉพาะรายการที่ตรงกับวันปัจจุบัน
          const todaysRequests = otRequests.filter(ot => isToday(ot.date));

          todaysRequests.forEach(ot => {
              const row = document.createElement("tr");
              row.innerHTML = `
                  <td>${ot.employee_name}</td>
                  <td>${ot.date}</td>
                  <td>${ot.reason}</td>
              `;
              otRequestTableBody.appendChild(row);
          });
      })
      .catch(error => console.error('Error fetching OT requests:', error));
}
function fetchDashboardAcceptedOTRequests() {
  fetch('http://127.0.0.1:5001/api/accepted_ot_requests')
      .then(response => response.json())
      .then(acceptedRequests => {
          const acceptedTableBody = document.getElementById("acceptedOtRequestTableSmall").querySelector("tbody");
          acceptedTableBody.innerHTML = ""; // ล้างตารางก่อนแสดงผลใหม่

          // กรองเฉพาะรายการที่ตรงกับวันปัจจุบัน
          const todaysAcceptedRequests = acceptedRequests.filter(ot => isToday(ot.date));

          todaysAcceptedRequests.forEach(ot => {
              const row = document.createElement("tr");
              row.innerHTML = `
                  <td>${ot.employee_name}</td>
                  <td>${ot.date}</td>
                  <td>${ot.reason}</td>
              `;
              acceptedTableBody.appendChild(row);
          });
      })
      .catch(error => console.error('Error fetching accepted OT requests:', error));
}

document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardOTRequests();
  fetchDashboardAcceptedOTRequests();

  // ตั้งเวลาโหลดข้อมูลใหม่ทุก 5 นาที
  setInterval(() => {
      fetchDashboardOTRequests();
      fetchDashboardAcceptedOTRequests();
  }, 300000); // 300,000 ms = 5 นาที
});

function isToday(dateString) {
    const today = new Date().toISOString().split('T')[0]; // วันที่ปัจจุบันในรูปแบบ YYYY-MM-DD
    return dateString === today;
}


 //โช์วัน
 document.addEventListener('DOMContentLoaded', () => {
  // ฟังก์ชันที่ใช้แสดงวันที่ปัจจุบัน
  function updateCurrentDay() {
    const currentDayElement = document.getElementById('currentDay');
    const today = new Date();
    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const todayDayName = daysOfWeek[today.getDay()]; // ใช้ getDay() เพื่อรับเลขวัน (0-6)
    
    currentDayElement.textContent = `Today is: ${todayDayName}`;
    
    // ลบคลาสเก่าออกก่อน
    currentDayElement.classList.remove("monday-to-friday", "saturday", "sunday");
    
    // เพิ่มคลาสตามวันในสัปดาห์
    if (today.getDay() >= 1 && today.getDay() <= 5) {
      currentDayElement.classList.add("monday-to-friday"); // วันจันทร์ - ศุกร์
    } else if (today.getDay() === 6) {
      currentDayElement.classList.add("saturday"); // วันเสาร์
    } else if (today.getDay() === 0) {
      currentDayElement.classList.add("sunday"); // วันอาทิตย์
    }
  }

  // อัพเดทวันเมื่อโหลดหน้า
  updateCurrentDay();
});