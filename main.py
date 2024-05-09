const getToken = async () => {
    const clientId = pm.environment.get("client_id");
    const clientSecret = pm.environment.get("client_secret");
    const url = pm.environment.get("pingFederateURL");

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `grant_type=client_credentials&client_id=${clientId}&client_secret=${clientSecret}`,
        ignoreErrors: true
    };

    return new Promise((resolve, reject) => {
        pm.sendRequest(url, requestOptions, async (err, response) => {
            if (err) {
                console.error("Request failed", err);
                reject(err);
            } else if (!response.ok) {
                console.error("Failed to get token", response.status, await response.text());
                reject(new Error('Failed to get token'));
            } else {
                const jsonResponse = await response.json();
                pm.environment.set("token", jsonResponse.access_token);
                console.log("Token fetched and set successfully:", jsonResponse.access_token);
                resolve(jsonResponse.access_token);
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
