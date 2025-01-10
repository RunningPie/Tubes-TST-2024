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

    // Prepare the request headers with the email and password
    const headers = new Headers();
    headers.append("email", email);
    headers.append("password", password);
    headers.append("API-Key", global_api_key)

    // Send the request using Fetch API
    fetch(backend + '/user-signup', {
        method: 'POST',  // Using POST since you're sending data
        headers: headers
    })
    .then(response => {
        if (response.ok) {
            // Handle successful register, for example, redirect to another page
            window.location.href = 'index.html';  // Replace with your actual URL
        } else {
            alert("Register failed, please try again.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred, please try again later.");
    });
});