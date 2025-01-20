document.addEventListener('DOMContentLoaded', () => {
    const departmentTable = document.querySelector('#employee-table'); // ตารางที่จะแสดงข้อมูล
    const saveDepartmentButton = document.querySelector('#saveDepartmentButton'); // ปุ่ม Save
    const openPopupButton = document.getElementById('openAddDepartmentPopup');
    const closePopupButton = document.getElementById('closeAddDepartmentPopup');
    const popup = document.getElementById('addDepartmentPopup');

    // ฟังก์ชันดึงข้อมูล Department
    function fetchDepartments() {
        fetch('http://127.0.0.1:5001/api/departments') // ดึงข้อมูลพนักงานพร้อมแผนก
            .then(response => response.json())
            .then(data => {
                fetch('http://127.0.0.1:5001/api/departments-list') // ดึงรายการแผนก
                    .then(response => response.json())
                    .then(departments => {
                        departmentTable.innerHTML = ''; // ล้างข้อมูลเก่าในตาราง

                        data.forEach(user => {
                            const row = document.createElement('tr');
                            const departmentOptions = departments.map(dept => `
                                <option value="${dept.name}" ${dept.name === user.department ? 'selected' : ''}>
                                    ${dept.name}
                                </option>
                            `).join('');

                            row.innerHTML = `
                                <td>${user.user_id}</td>
                                <td>${user.name}</td>
                                <td>
                                    <select class="department-dropdown" data-id="${user.user_id}">
                                        ${departmentOptions}
                                    </select>
                                </td>
                            `;
                            departmentTable.appendChild(row);
                        });
                    })
                    .catch(error => console.error('Error fetching department list:', error));
            })
            .catch(error => console.error('Error fetching employees:', error));
    }

    // ฟังก์ชันบันทึกข้อมูล Department
    function saveDepartments() {
        const departmentDropdowns = document.querySelectorAll('.department-dropdown');
        const updates = Array.from(departmentDropdowns).map(dropdown => ({
            user_id: dropdown.dataset.id,
            department: dropdown.value
        }));

        fetch('http://127.0.0.1:5001/api/updateDepartment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ departments: updates })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert('Failed to save departments.');
                }
            })
            .catch(error => console.error('Error saving departments:', error));
    }

    // ฟังก์ชันเพิ่ม Department ใหม่
    function addDepartment() {
        const departmentName = document.getElementById('newDepartmentName').value;

        if (!departmentName) {
            alert('Please enter a department name.');
            return;
        }

        fetch('http://127.0.0.1:5001/api/addDepartment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: departmentName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message || 'Department added successfully!');
                    document.getElementById('newDepartmentName').value = ''; // ล้างค่า input
                    popup.classList.add('hidden'); // ซ่อน Popup หลังเพิ่มเสร็จ
                    fetchDepartments(); // อัปเดตข้อมูล
                } else {
                    alert('Failed to add department.');
                }
            })
            .catch(error => console.error('Error adding department:', error));
    }

    // เปิดและปิด Popup
    openPopupButton.addEventListener('click', () => {
        popup.classList.remove('hidden'); // แสดง Popup
    });

    closePopupButton.addEventListener('click', () => {
        popup.classList.add('hidden'); // ซ่อน Popup
    });

    // ผูก Event กับฟังก์ชัน
    saveDepartmentButton.addEventListener('click', saveDepartments);
    document.getElementById('addDepartmentButton').addEventListener('click', addDepartment);

    // ดึงข้อมูลเมื่อโหลดหน้า
    fetchDepartments();
});

function fetchDepartmentList() {
    fetch('http://127.0.0.1:5001/api/departments-list')
        .then(response => response.json())
        .then(departments => {
            const departmentFilter = document.getElementById('departmentFilter');
            departmentFilter.innerHTML = '<option value="all">All Departments</option>'; // ล้างค่าเดิมและเพิ่มค่า "All"

            departments.forEach(department => {
                if (department.name) { // ตรวจสอบว่ามีชื่อ
                    const option = document.createElement('option');
                    option.value = department.name;
                    option.textContent = department.name;
                    departmentFilter.appendChild(option);
                }
            });
        })
        .catch(error => console.error('Error fetching department list:', error));
}