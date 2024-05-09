function getToken(clientId, clientSecret, url) {
    const headers = {
        'x-agw-client_id': clientId,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'PF=qNshxyONTlOl0D6uEsTDHw' // Update as necessary
    };

    const body = {
        'client_id': clientId,
        'client_secret': clientSecret
    };

    pm.sendRequest({
        url: url + '?grant_type=client_credentials',
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
            if (res.code === 200 && jsonResponse.access_token) {
                pm.environment.set("access_token", jsonResponse.access_token);
                console.log("Token successfully fetched and set.");
            } else {
                console.error("Failed to fetch token:", jsonResponse);
            }
        }
    });
}

// Check the region set in the environment
const region = pm.environment.get("region");

let clientId, clientSecret, tokenUrl;

if (region === 'amer') {
    clientId = pm.environment.get("client_id_amer");
    clientSecret = pm.environment.get("client_secret_amer");
    tokenUrl = pm.environment.get("amerpingfedrate");
} else if (region === 'eu') {
    clientId = pm.environment.get("client_id_eu");
    clientSecret = pm.environment.get("client_secret_eu");
    tokenUrl = pm.environment.get("eupingfedrate");
}

console.log("Fetching new access token...");
getToken(clientId, clientSecret, tokenUrl);
