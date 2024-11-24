document.getElementById('normal-signup').addEventListener('click', function() {
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

    // Send the request using Fetch API
    fetch('/user-signup', {
        method: 'POST',  // Using POST since you're sending data
        headers: headers
    })
    .then(response => {
        if (response.ok) {
            // Handle successful login, for example, redirect to another page
            window.location.href = '/';  // Replace with your actual URL
        } else {
            alert("Login failed, please try again.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred, please try again later.");
    });
});