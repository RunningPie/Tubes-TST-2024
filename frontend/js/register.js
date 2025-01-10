const global_api_key = "426343da-fa63-4f8c-b288-badbdca5f74f"
const backend = "https://tubes-tst-2024-production.up.railway.app"

document.getElementById('register').addEventListener('click', function() {
    // Get the email and password values from the form
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Perform input validation (optional)
    if (!email || !password) {
        alert("Please enter both email and password.");
        return;
    }

    // Send the request using Fetch API
    fetch(backend + '/user-signup', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "API-Key": global_api_key
        },
        body: JSON.stringify({ email, password }),
    })
    .then(response => {
        if (response.ok) {
            // Handle successful register, for example, redirect to another page
            window.location.href = 'index.html';
        } else {
            response.json().then(data => {
                if (data.detail) {
                    // Show the specific error message from the response
                    alert(data.detail);
                } else {
                    alert("Register failed, please try again.");
                }
            }).catch(() => {
                alert("Unable to parse the response. Please try again.");
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred, please try again later.");
    });
    
});