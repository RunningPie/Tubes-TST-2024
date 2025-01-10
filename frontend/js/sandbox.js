document.getElementById("try-endpoint").addEventListener("click", () => {
    const endpoint = document.getElementById("endpoint").value;
    const method = document.getElementById("http-method").value;
    const requestBody = document.getElementById("request-body").value;

    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json",
            "API-Key": global_api_key,
            "Sandbox": true
        },
    };

    if (method === "POST" && requestBody) {
        options.body = requestBody;
    }

    fetch(backend + `${endpoint}`, options)
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("response-output").textContent = JSON.stringify(data, null, 2);
        })
        .catch((error) => {
            document.getElementById("response-output").textContent = `Error: ${error.message}`;
        });
});
