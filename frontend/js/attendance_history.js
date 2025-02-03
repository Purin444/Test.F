// ฟังก์ชัน mapStatus สำหรับแปลง Status Code เป็นข้อความ
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


// ฟังก์ชันแสดงข้อมูลเมื่อวันที่เปลี่ยน
function fetchUsersAndAttendanceOnDateChange() {
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;

  if (!startDate || !endDate) {
    return; // หยุดถ้ายังไม่ได้เลือกวันที่
  }

  // เรียก API พร้อม Query Parameters
  fetch(`http://127.0.0.1:5001/api/attendance?start=${startDate}&end=${endDate}`)
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch attendance logs");
      return response.json();
    })
    .then(attendanceLogs => {
      // ตรวจสอบว่าเจอ tbody หรือไม่
      const attendanceTableBody = document.querySelector(".attendance-log-table tbody");
      if (!attendanceTableBody) {
        console.error("Table body not found!");
        return;
      }

      // ล้างข้อมูลเก่า
      attendanceTableBody.innerHTML = "";

      if (attendanceLogs.length > 0) {
        attendanceLogs.forEach(log => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${log.user_id}</td>
            <td>${new Date(log.timestamp).toLocaleString()}</td>
            <td>${log.device_ip}</td>
            <td>${mapStatus(log.status)}</td>
          `;
          attendanceTableBody.appendChild(row);
        });
      } else {
        attendanceTableBody.innerHTML = `
          <tr>
            <td colspan="4" style="text-align: center;">No data available for the selected dates.</td>
          </tr>
        `;
      }
    })
    .catch(error => {
      console.error("Error fetching attendance logs:", error);
      alert("Error fetching attendance data. Please try again later.");
    });
}

// ตั้งค่า event listener
document.getElementById("startDate").addEventListener("change", fetchUsersAndAttendanceOnDateChange);
document.getElementById("endDate").addEventListener("change", fetchUsersAndAttendanceOnDateChange);

document.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  const formattedDate = today.toISOString().split("T")[0];

  document.getElementById("startDate").value = formattedDate;
  document.getElementById("endDate").value = formattedDate;

  // เรียกข้อมูลทันทีเมื่อโหลดหน้า
  fetchUsersAndAttendanceOnDateChange();
});
