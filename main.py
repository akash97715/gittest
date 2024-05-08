const getToken = async () => {
    const clientId = pm.environment.get("client_id");
    const clientSecret = pm.environment.get("client_secret");
    const url = pm.environment.get("pingFederateURL");

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-agw-client_id': clientId  // Adjusted based on your cURL command
        },
        body: `grant_type=client_credentials&client_id=${clientId}&client_secret=${clientSecret}`,
        ignoreErrors: true
    };

    pm.sendRequest(url, requestOptions, function(err, response) {
        if (err) {
            console.error("Request failed", err);
        } else if (!response.ok) {
            console.error("Failed to get token", response.status, response.text());
        } else {
            const jsonResponse = response.json();
            pm.environment.set("token", jsonResponse.access_token);
            console.log("Token fetched and set successfully:", jsonResponse.access_token);
        }
    });
};

if (!pm.environment.get("token")) {
    console.log("Fetching new token...");
    getToken();
} else {
    console.log("Using existing token:", pm.environment.get("token"));
}
