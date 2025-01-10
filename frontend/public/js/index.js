document.getElementById("normal-signin").addEventListener("click", () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    fetch(backend + "/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "API-Key": global_api_key
        },
        body: JSON.stringify({ email, password }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert("Login successful!");
                window.location.href = "home.html";
            } else {
                alert("Login failed: " + data.message);
            }
        })
        .catch((error) => console.error("Error:", error));
});
