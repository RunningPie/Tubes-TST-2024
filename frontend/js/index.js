const global_api_key = "426343da-fa63-4f8c-b288-badbdca5f74f"
const backend = "https://tubes-tst-2024-production.up.railway.app"

document.getElementById("normal-signin").addEventListener("click", () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    fetch(backend + "/user-signin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "API-Key": global_api_key
        },
        body: JSON.stringify({ email, password }),
        credentials: "include"
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                console.log("Login successful!");
                window.location.href = "home.html";
            } else {
                console.log("Login failed: " + data.message);
            }
        })
        .catch((error) => console.error("Error:", error));
});
