// Function to fetch the token
function getToken() {
    const url = 'https://devfederate.pfizer.com/as/token.oauth2?grant_type=client_credentials';
    const clientId = pm.environment.get("client_id");
    const clientSecret = pm.environment.get("client_secret");

    const headers = {
        'x-agw-client_id': clientId,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'PF=qNshxyONTlOl0D6uEsTDHw'
    };

    const body = {
        'client_id': clientId,
        'client_secret': clientSecret
    };

    pm.sendRequest({
        url: url,
        method: 'POST',
        header: headers,
        body: {
            mode: 'urlencoded',
            urlencoded: Object.keys(body).map(key => ({key, value: body[key]}))
        }
    }, (err, res) => {
        if (err) {
            console.error("Error fetching token:", err);
        } else {
            const jsonResponse = res.json();
            if (res.code === 200) {
                pm.environment.set("access_token", jsonResponse.access_token);
            } else {
                console.error("Failed to fetch token:", jsonResponse);
            }
        }
    });
}

// Check if the access_token is already available and not expired
if (!pm.environment.get("access_token")) {
    console.log("Fetching new access token...");
    getToken();
} else {
    console.log("Using stored access token.");
}
