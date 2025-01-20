document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    const saveButton = document.getElementById('saveButton'); // ปุ่ม Save

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'en',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth'
        },
        editable: true,
        droppable: true,
        events: function (fetchInfo, successCallback, failureCallback) {
            fetch('http://127.0.0.1:5001/api/holidays') // โหลดข้อมูลจาก Backend
                .then(response => response.json())
                .then(data => {
                    if (!Array.isArray(data)) {
                        throw new Error("Unexpected response format: data is not an array");
                    }
                    const holidays = data.map(holiday => ({
                        title: holiday.title, // ชื่อ Event
                        start: holiday.start, // วันที่ Event
                        backgroundColor: holiday.backgroundColor || '#f39c12',
                        textColor: holiday.textColor || '#fff'
                    }));
                    console.log("Loaded holidays:", holidays);
                    successCallback(holidays);
                })
                .catch(error => {
                    console.error('Error loading holidays:', error);
                    failureCallback(error);
                });
        },
        dateClick: function (info) {
            const title = prompt('Enter holiday name:');
            if (title) {
                const newEvent = {
                    title: title,
                    start: info.dateStr,
                    backgroundColor: '#2ecc71',
                    textColor: '#fff'
                };
                calendar.addEvent(newEvent);
            }
        },
        eventClick: function (info) {
            if (confirm(`Do you want to delete the event: ${info.event.title}?`)) {
                info.event.remove();
            }
        }
    });

    calendar.render();

    // ฟังก์ชันสำหรับบันทึก Events ทั้งหมด
    function saveAllEvents() {
        const events = calendar.getEvents(); // ดึง Events ทั้งหมดจาก Calendar
        const eventsData = events.map(event => ({
            name: event.title, // เปลี่ยนจาก title เป็น name
            date: event.start ? event.start.toISOString() : null, // เปลี่ยนจาก start เป็น date
            backgroundColor: event.backgroundColor || '#f39c12',
            textColor: event.textColor || '#fff'
        }));

        console.log("Events to be saved:", eventsData); // ตรวจสอบข้อมูลก่อนส่ง

        const validEvents = eventsData.filter(event => event.name && event.date);

        if (validEvents.length === 0) {
            console.error('No valid events to save!');
            return;
        }

        fetch('http://127.0.0.1:5001/api/saveAllHolidays', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(validEvents)
        })
        .then(response => response.json())
        .then(data => console.log('All holidays saved:', data))
        .catch(error => console.error('Error saving all holidays:', error));
    }

    // Event Listener สำหรับปุ่ม Save
    saveButton.addEventListener('click', saveAllEvents);
});
