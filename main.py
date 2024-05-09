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
                console.error("Request failed with error:", err);
                reject(err);
            } else if (!response.ok) {
                const errorText = await response.text();
                console.error("Failed to get token, status:", response.status, "Response:", errorText);
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
