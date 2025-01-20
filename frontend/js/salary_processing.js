
async function fetchUsersAndAttendanceAndSalaries() {
  const startDate = new Date(document.getElementById("startDate").value);
  const endDate = new Date(document.getElementById("endDate").value);
  endDate.setHours(23, 59, 59, 999); // ขยายช่วงเวลาให้ถึงสิ้นสุดวัน

  const hourlyRate = 10; // ค่าแรงต่อชั่วโมง
  const weekdayOTMultiplier = 1.5; // อัตราค่า OT วันธรรมดา
  const weekendOTMultiplier = 2; // อัตราค่า OT วันเสาร์อาทิตย์

  try {
    // ดึงข้อมูล Users และ Salaries
    const usersResponse = await fetch('http://127.0.0.1:5001/api/salaries');
    if (!usersResponse.ok) throw new Error('Failed to fetch users with salaries');
    const usersWithSalaries = await usersResponse.json();

    // ดึงข้อมูล Attendance Logs
    const attendanceResponse = await fetch('http://127.0.0.1:5001/api/attendance');
    if (!attendanceResponse.ok) throw new Error('Failed to fetch attendance logs');
    const attendanceLogs = await attendanceResponse.json();

    // กรองข้อมูลการเข้างานตามวันที่
    const filteredLogs = attendanceLogs.filter(log => {
      const logDate = new Date(log.timestamp);
      return logDate >= startDate && logDate <= endDate;
    });

    // เตรียมตาราง
    const employeeTableBody = document.querySelector("#employee-table");
    employeeTableBody.innerHTML = ""; // ล้างข้อมูลเก่าในตาราง

    if (usersWithSalaries.length === 0) {
      employeeTableBody.innerHTML = "<tr><td colspan='7'>No data available for the selected dates.</td></tr>";
      return;
    }

    usersWithSalaries.forEach(user => {
      const userLogs = filteredLogs.filter(log => log.user_id === user.user_id);
      userLogs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      let totalWorkMinutes = 0;
      let totalOTMinutes = 0;

      for (let i = 0; i < userLogs.length; i++) {
        const log = userLogs[i];

        // การทำงานปกติ
        if (log.status === 0 && i + 1 < userLogs.length && userLogs[i + 1].status === 1) {
          const checkInTime = new Date(log.timestamp);
          const checkOutTime = new Date(userLogs[i + 1].timestamp);
          totalWorkMinutes += (checkOutTime - checkInTime) / (1000 * 60);
          i++;
        }

        // การทำ OT
        if (log.status === 4 && i + 1 < userLogs.length && userLogs[i + 1].status === 5) {
          const otInTime = new Date(log.timestamp);
          const otOutTime = new Date(userLogs[i + 1].timestamp);
          const otDuration = (otOutTime - otInTime) / (1000 * 60);
          const otMultiplier = [0, 6].includes(otInTime.getDay()) ? weekendOTMultiplier : weekdayOTMultiplier;
          totalOTMinutes += otDuration * otMultiplier;
          i++;
        }
      }

      const totalWorkHours = (totalWorkMinutes / 60).toFixed(2);
      const totalOTHours = (totalOTMinutes / 60).toFixed(2);
      const otSalary = (totalOTHours * hourlyRate).toFixed(2);

      // เพิ่มข้อมูลลงในตาราง
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${user.user_id}</td>
        <td>${user.name}</td>
        <td>${totalWorkHours} hours</td>
        <td>${totalOTHours} hours</td>
        <td>$${otSalary}</td>
        <td><input type="number" class="salary-input" data-user-id="${user.user_id}" value="${user.salary}" /></td>
        <td class="total-salary">$${(parseFloat(user.salary) + parseFloat(otSalary)).toFixed(2)}</td>
      `;

      const salaryInput = row.querySelector(".salary-input");
      salaryInput.addEventListener("input", (e) => {
        const salary = parseFloat(e.target.value) || 0;
        const totalSalary = (salary + parseFloat(otSalary)).toFixed(2);
        row.querySelector(".total-salary").textContent = `$${totalSalary}`;
      });

      employeeTableBody.appendChild(row);
    });
  } catch (error) {
    console.error('Error fetching data:', error);
    alert('An error occurred while fetching data. Please try again later.');
  }
}




function saveSalaries() {
  const salaryInputs = document.querySelectorAll(".salary-input");
  const salaries = Array.from(salaryInputs).map(input => ({
    user_id: input.dataset.userId.toString(),
    salary: parseFloat(input.value) || 0
  }));

  if (salaries.length === 0) {
    alert("No salaries to save.");
    return;
  }

  console.log("Sending data to API:", salaries);

  fetch('http://127.0.0.1:5001/api/updateSalary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ salaries })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log("API Response:", data);
      alert("Salaries updated successfully!");
    })
    .catch(error => {
      console.error("Error updating salaries:", error);
      alert("An error occurred while saving salaries. Please try again.");
    });
}



document.addEventListener("DOMContentLoaded", () => {
  const saveButton = document.getElementById("save-salaries-btn");
  if (saveButton) {
    saveButton.addEventListener("click", saveSalaries);
  } else {
    console.error("Save button not found in DOM.");
  }

  document.getElementById("startDate").addEventListener("change", fetchUsersAndAttendanceAndSalaries);
  document.getElementById("endDate").addEventListener("change", fetchUsersAndAttendanceAndSalaries);
});



/////////////////////////////////////////////////////////////////
 // ฟังก์ชันการพิมพ์
 document.addEventListener('DOMContentLoaded', () => {
  const printButton = document.getElementById("print-table-btn");

  // ตรวจสอบว่า printButton มีอยู่ใน DOM หรือไม่
  if (printButton) {
      printButton.addEventListener("click", function () {
          const dashboardContainer = document.querySelector(".dashboard-container");
          const aside = dashboardContainer.querySelector("aside");
          const saveBtn = document.getElementById("save-salaries-btn");

          // ซ่อนองค์ประกอบที่ไม่ต้องการพิมพ์
          aside.style.display = "none";
          printButton.style.display = "none";
          saveBtn.style.display = "none";

          // เปิด dialog การพิมพ์
          window.print();

          // แสดงองค์ประกอบกลับหลังพิมพ์
          aside.style.display = "block";
          printButton.style.display = "block";
          saveBtn.style.display = "block";
      });
  } else {
      console.error("Print button not found in DOM.");
  }
});

// ฟังก์ชันดาวน์โหลด Excel
document.addEventListener('DOMContentLoaded', () => {
  // เพิ่ม event listener สำหรับปุ่ม "Download Excel"
  const downloadButton = document.getElementById('download-excel-btn');
  
  if (downloadButton) {
      downloadButton.addEventListener('click', function () {
          const table = document.querySelector('.attendance-table');
          if (!table) {
              alert('Table not found!');
              return;
          }

          const workbook = XLSX.utils.table_to_book(table, {sheet: "Sheet1"});
          const fileName = `Attendance_${new Date().toISOString().slice(0, 10)}.xlsx`;
          XLSX.writeFile(workbook, fileName);
      });
  } else {
      console.error("Download button not found in DOM.");
  }

  // เพิ่ม event listener สำหรับปุ่ม "Print Table"
  const printButton = document.getElementById("print-table-btn");
  if (printButton) {
      printButton.addEventListener("click", function () {
          const dashboardContainer = document.querySelector(".dashboard-container");
          const aside = dashboardContainer.querySelector("aside");
          const saveBtn = document.getElementById("save-salaries-btn");

          // ซ่อนองค์ประกอบที่ไม่ต้องการพิมพ์
          aside.style.display = "none";
          printButton.style.display = "none";
          saveBtn.style.display = "none";

          // เปิด dialog การพิมพ์
          window.print();

          // แสดงองค์ประกอบกลับหลังพิมพ์
          aside.style.display = "block";
          printButton.style.display = "block";
          saveBtn.style.display = "block";
      });
  } else {
      console.error("Print button not found in DOM.");
  }
});


//////////////////////////
// เลือกวันล่าสุด
document.addEventListener('DOMContentLoaded', () => {
  const today = new Date(); // วันที่ปัจจุบัน
  const formattedDate = today.toISOString().split("T")[0]; // แปลงวันที่เป็นรูปแบบ YYYY-MM-DD

  // ตั้งค่า default ให้ startDate และ endDate
  const startDateInput = document.getElementById("startDate");
  const endDateInput = document.getElementById("endDate");

  if (startDateInput && endDateInput) {
    startDateInput.value = formattedDate;
    endDateInput.value = formattedDate;
  }

  // เรียกฟังก์ชัน fetchUsersAndAttendanceAndSalaries หลังตั้งค่า default
  fetchUsersAndAttendanceAndSalaries();
});