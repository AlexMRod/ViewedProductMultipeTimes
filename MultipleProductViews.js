// DEBUG 400 ERROR

import 'dotenv/config';
import express from "express"

const app = express();

app.use(express.json());

const apiKey = process.env.AUTHORIZATION;
const metricId = "USMVZw";

function cleanPayload(payload) {
    return payload.replace(/'/g, "\"");
}

async function getKlaviyoMetric(apiKey, metricId, profileId) {
    const url = `https://a.klaviyo.com/api/events?filter=equals(metric_id,\"${metricId}\"),equals(profile_id,\"${profileId}\")`;
    const headers = {
        "Authorization": apiKey,
        "Accept": "application/vnd.api+json",
        "Revision": "2024-10-15"
    };
    
    try {
        const response = await fetch(url, { headers });
        if (!response.ok) throw new Error(`Error ${response.status}: ${await response.text()}`);
        return await response.json();
    } catch (error) {
        console.error(error);
    }
}

async function createKlaviyoEvent(apiKey, profileId, eventPayload) {
    const url = "https://a.klaviyo.com/api/events";
    const headers = {
        "Authorization": apiKey,
        "Accept": "application/vnd.api+json",
        "Revision": "2024-10-15",
        "Content-Type": "application/vnd.api+json"
    };

    const payload = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": eventPayload,
                "metric": {
                    "data": {
                        "type": "metric",
                        "attributes": {
                            "name": "Viewed Product Multiple Times"
                        }
                    }
                },
                "profile": {
                    "data": {
                        "type": "profile",
                        "attributes": {
                            "properties": {},
                            "meta": {
                                "patch_properties": {
                                    "append": { "newKey": "New Value" },
                                    "unappend": { "newKey": "New Value" }
                                }
                            },
                            "id": profileId
                        }
                    }
                },
                "value": 19.98
            }
        }
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
        if (response.status === 202) {
            console.log('Event created successfully');
        } else {
            throw new Error(`Error ${response.status}: ${await response.text()}`);
        }
    } catch (error) {
        console.error(error);
    }
}

app.post('/process-event', async (req, res) => {
    try {
        const data = req.body;
        const cleanedPayload = cleanPayload(data.payload);
        const eventPayload = JSON.parse(cleanedPayload);
        const profileId = data.id;
        const product = eventPayload.ProductName;

        const metricResponse = await getKlaviyoMetric(apiKey, metricId, profileId);
        let count = 0;

        metricResponse.data.forEach(item => {
            if (item.attributes?.event_properties?.ProductName === product) {
                count++;
                console.log('item added');
            } else {
                console.log('item not added');
            }
        });

        console.log(count);
        eventPayload['Times Seen'] = count;

        if (count >= 2) {
            await createKlaviyoEvent(apiKey, profileId, eventPayload);
        }
        res.json({ message: "Process completed successfully", count });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
