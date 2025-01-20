document.addEventListener('DOMContentLoaded', () => {
    const saveButton = document.getElementById("saveButton");
    const otRequestTable = document.getElementById("otRequestTable");
    const employeeNameSelect = document.getElementById("employeeName");
    const deleteButton = document.getElementById("deleteButton");
    const selectAllCheckbox = document.getElementById("selectAll");
    const acceptedTable = document.getElementById("acceptedOtRequestTable");

    // ฟังก์ชัน Fetch Users ไปใส่ใน List Box
    function fetchUsers() {
        fetch('http://127.0.0.1:5001/api/users')
            .then(response => response.json())
            .then(users => {
                employeeNameSelect.innerHTML = '<option value="">-- Select Employee --</option>';
                users.forEach(user => {
                    const option = document.createElement("option");
                    option.value = user.user_id;
                    option.textContent = user.name;
                    employeeNameSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching users:', error));
    }

    // ฟังก์ชันดึงข้อมูล OT Requests และแสดงในตาราง
    function fetchOTRequests() {
        fetch('http://127.0.0.1:5001/api/ot-requests/')
            .then(response => response.json())
            .then(otRequests => {
                otRequestTable.innerHTML = ""; // ล้างตารางก่อนเติมข้อมูลใหม่

                if (otRequests.length === 0) {
                    otRequestTable.innerHTML = `<tr><td colspan="4">No OT Requests found</td></tr>`;
                    return;
                }

                otRequests.forEach(ot => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${ot.employee_name}</td>
                        <td>${ot.date}</td>
                        <td>${ot.reason}</td>
                        <td>
                            <button class="accept-btn" data-id="${ot.employee_id}">Accept</button>
                        </td>
                    `;
                    otRequestTable.appendChild(row);
                });

                document.querySelectorAll('.accept-btn').forEach(button => {
                    button.addEventListener('click', () => showAcceptPopup(button));
                });
            })
            .catch(error => console.error('Error fetching OT requests:', error));
    }

    // ฟังก์ชัน Fetch Accepted OT Requests
    function fetchAcceptedOTRequests() {
        fetch('http://127.0.0.1:5001/api/accepted_ot_requests/')
            .then(response => response.json())
            .then(acceptedRequests => {
                acceptedTable.innerHTML = ""; // ล้างตารางก่อนแสดงผลใหม่

                if (acceptedRequests.length === 0) {
                    acceptedTable.innerHTML = `<tr><td colspan="4">No accepted OT requests found</td></tr>`;
                    return;
                }

                acceptedRequests.forEach(ot => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td><input type="checkbox" class="rowCheckbox" data-id="${ot._id}"></td>
                        <td>${ot.employee_name}</td>
                        <td>${ot.date}</td>
                        <td>${ot.reason}</td>
                    `;
                    acceptedTable.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching accepted OT requests:', error));
    }

    // ฟังก์ชัน Select All
    selectAllCheckbox.addEventListener("change", function () {
        const checkboxes = document.querySelectorAll(".rowCheckbox");
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
    });

    deleteButton.addEventListener("click", () => {
        const selectedCheckboxes = Array.from(document.querySelectorAll(".rowCheckbox:checked"));
        const selectedIds = selectedCheckboxes.map(checkbox => checkbox.dataset.id);
    
        if (selectedIds.length === 0) {
            alert("Please select at least one record to delete.");
            return;
        }
    
        if (confirm("Are you sure you want to delete the selected records?")) {
            fetch('http://127.0.0.1:5001/api/accepted_ot_requests/', { // เปลี่ยน URL
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: selectedIds })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        fetchAcceptedOTRequests(); // โหลดข้อมูลใหม่
                    } else {
                        alert("Error: " + data.error);
                    }
                })
                .catch(error => console.error('Error deleting records:', error));
        }
    });
    

    // ฟังก์ชันบันทึกข้อมูล OT Request ไปยัง Backend
    function saveOTRequest() {
        const employeeId = employeeNameSelect.value;
        const employeeName = employeeNameSelect.options[employeeNameSelect.selectedIndex].text;
        const date = document.getElementById("date").value;
        const reason = document.getElementById("reason").value;

        if (!employeeId || !date || !reason) {
            alert("Please fill in all fields.");
            return;
        }

        const otRequestData = {
            employee_id: employeeId,
            employee_name: employeeName,
            date: date,
            reason: reason
        };

        fetch('http://127.0.0.1:5001/api/ot-requests/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(otRequestData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert("OT Request saved successfully!");
                    fetchOTRequests(); // โหลดตารางใหม่
                    document.getElementById("otRequestForm").reset();
                } else {
                    alert("Failed to save OT Request: " + data.error);
                }
            })
            .catch(error => console.error('Error saving OT request:', error));
    }

    function showAcceptPopup(button) {
        const masterKey = prompt("Please enter the Master Key:");
    
        if (masterKey === "123456") { // ตรวจสอบ Master Key
            const row = button.closest("tr");
            const employeeName = row.cells[0].innerText.trim();
            const date = row.cells[1].innerText.trim();
            const reason = row.cells[2].innerText.trim();
    
            const acceptedData = {
                employee_name: employeeName,
                date: date,
                reason: reason
            };
    
            fetch('http://127.0.0.1:5001/api/ot-requests/accept', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(acceptedData)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert("OT Request accepted successfully!");
                        fetchOTRequests();         // โหลดข้อมูล OT Requests ใหม่
                        fetchAcceptedOTRequests(); // โหลดข้อมูล Accepted ใหม่
                    } else {
                        alert("Failed to accept OT Request: " + data.error);
                    }
                })
                .catch(error => console.error('Error accepting OT request:', error));
        } else {
            alert("Invalid Master Key. Access denied.");
        }
    }
    // Event Listener
    saveButton.addEventListener("click", saveOTRequest);
    // โหลดข้อมูลเมื่อหน้าเว็บเสร็จ
    fetchUsers();
    fetchOTRequests();
    fetchAcceptedOTRequests();
});
