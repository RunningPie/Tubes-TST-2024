const global_api_key = "426343da-fa63-4f8c-b288-badbdca5f74f"
const backend = "https://tubes-tst-2024-production.up.railway.app"

document.getElementById("team-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Mencegah form dikirim secara default
    
    const teamName = document.getElementById("team-name").value; // Ambil nilai input
    const requestBody = { team_name: teamName }; // Buat objek JSON
    
    try {
        const response = await fetch(backend + "/create-team", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "API-Key": global_api_key
            },
            body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert("Team created successfully: " + JSON.stringify(result));
        } else {
            const error = await response.json();
            alert("Failed to create team: " + JSON.stringify(error));
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
});

document.getElementById("team-member-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Mencegah form dikirim secara default
    
    const memberName = document.getElementById("member-name").value; // Ambil nilai input
    const teamID = document.getElementById("member-team-id").value; // Ambil nilai input
    const requestBody = {
        member_name: memberName,
        team_id: teamID
    }; // Buat objek JSON
    
    try {
        const response = await fetch(backend + "/add-team-member", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "API-Key": global_api_key
            },
            body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert("Team member added successfully: " + JSON.stringify(result));
        } else {
            const error = await response.json();
            alert("Failed to add member: " + JSON.stringify(error));
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
});

document.getElementById("team-task-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Mencegah form dikirim secara default
    
    const teamID = document.getElementById("task-team-id").value; // Ambil nilai input
    const taskName = document.getElementById("task-name").value; // Ambil nilai input
    const priority = document.getElementById("priority").value; // Ambil nilai input
    const requestBody = {
        task_name: taskName,
        team_id: teamID,
        priority: priority
    }; // Buat objek JSON
    
    try {
        const response = await fetch(backend + "/add-team-task", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "API-Key": global_api_key
            },
            body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert("Team task added successfully: " + JSON.stringify(result));
        } else {
            const error = await response.json();
            alert("Failed to add task: " + JSON.stringify(error));
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
});

// Fungsi untuk mengambil cookie berdasarkan nama
function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Fungsi untuk menunggu cookies dan menjalankan kode setelah cookies ada
function waitForCookieAndSave() {
    // Ambil fullname dari cookies
    const userFullname = getCookie('user_fullname');

    // Tampilkan fullname di halaman
    if (userFullname) {
        document.getElementById('userFullname').textContent = userFullname;
        clearInterval(cookieCheckInterval);  // Hentikan pengecekan cookies setelah ditemukan
    }
}

// Cek cookies setiap 100ms
const cookieCheckInterval = setInterval(waitForCookieAndSave, 100);

// Fungsi untuk menampilkan data tim di halaman
async function fetchAndDisplayTeams() {
    try {
        // Kirim request ke backend untuk mengambil data tim
        const response = await fetch(backend + "/show-teams", {
            method: 'GET',
            credentials: 'include',
            headers: {
                "Content-Type": "application/json",
                "API-Key": global_api_key
            },
        });

        // Cek apakah respons berhasil
        if (response.ok) {
            const result = await response.json();

            // Ambil elemen daftar tim
            const teamList = document.getElementById("team-list");

            // Bersihkan daftar sebelumnya
            teamList.innerHTML = "";

            // Iterasi melalui data tim dan tambahkan ke HTML
            result.data.forEach(team => {
                const listItem = document.createElement("li");
                listItem.textContent = `${team.team_name} (ID: ${team.team_id})`;
                teamList.appendChild(listItem);
            });

            console.log("Team data displayed successfully");
        } else {
            const error = await response.json();
            console.error("Failed to fetch team data:", error);
            alert("Failed to fetch team data: " + error.message);
        }
    } catch (err) {
        console.error("Error:", err.message);
        alert("Error: " + err.message);
    }
}

// Panggil fungsi untuk menampilkan data tim
fetchAndDisplayTeams();

// Add this to your home.js file

// Handle API Key form submission
document.getElementById('api-key-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const domain = document.getElementById('service-domain').value;
    
    try {
        const response = await fetch(backend + '/request-api-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: domain }),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to generate API key');
        }

        const data = await response.json();
        
        // Show the API key
        document.getElementById('generated-api-key').value = data.key;
        document.getElementById('api-key-result').style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate API key. Please try again.');
    }
});

// Handle copy button click
document.getElementById('copy-api-key').addEventListener('click', function() {
    const apiKeyInput = document.getElementById('generated-api-key');
    apiKeyInput.select();
    document.execCommand('copy');
    
    // Optional: Show feedback
    const originalText = this.innerHTML;
    this.innerHTML = '<i class="fas fa-check"></i>';
    setTimeout(() => {
        this.innerHTML = originalText;
    }, 2000);
});