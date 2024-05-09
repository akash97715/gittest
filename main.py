const getToken = async () => {
    const clientId = pm.environment.get("client_id");
    const clientSecret = pm.environment.get("client_secret");
    const url = 'https://devfederate.pfizer.com/as/token.oauth2?grant_type=client_credentials';

    const requestOptions = {
        method: 'POST',
        headers: {
            'x-agw-client_id': clientId, // Assuming the API expects this custom header
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'PF=qNshxyONTlOl0D6uEsTDHw'  // Ensure this cookie is still valid and required
        },
        body: `client_id=${encodeURIComponent(clientId)}&client_secret=${encodeURIComponent(clientSecret)}`,
        ignoreErrors: true
    };

    return new Promise((resolve, reject) => {
        pm.sendRequest(url, requestOptions, async (err, response) => {
            if (err) {
                console.error("Request failed with error:", err);
                reject(err);
            } else if (!response.ok) {
                const responseBody = await response.text();  // Get the full response body
                console.error("Failed to get token, status:", response.status, "Response body:", responseBody);
                reject(new Error('Failed to get token'));
            } else {
                try {
                    const jsonResponse = await response.json();
                    pm.environment.set("token", jsonResponse.access_token);
                    console.log("Token fetched and set successfully:", jsonResponse.access_token);
                    resolve(jsonResponse.access_token);
                } catch (jsonError) {
                    console.error("Failed to parse JSON response:", jsonError);
                    reject(jsonError);
                }
            }
        });
    });
};

const checkAndFetchToken = async () => {
    if (!pm.environment.get("token")) {
        console.log("Fetching new token...");
        try {
            const token = await getToken();
            console.log("Token received:", token);
        } catch (error) {
            console.error("Error fetching token:", error);
        }
    } else {
        console.log("Using existing token:", pm.environment.get("token"));
    }
};

checkAndFetchToken();
