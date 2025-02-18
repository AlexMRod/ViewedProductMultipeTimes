import requests
import json
import os
import datetime

def handler(event, profile, context):
    
    event_properties = event["data"]["attributes"]["event_properties"]
    profile_id = profile["data"]["id"]
    product_name = event_properties.get('ProductName')
    api_key = os.getenv('API_KEY')
    metric_id = os.getenv('METRIC_ID')

    def get_klaviyo_metric(api_key, metric_id, profile_id):
        today = datetime.datetime.now(datetime.timezone.utc)
        date_filter = today - datetime.timedelta(days=7)
        date_filter_iso = date_filter.isoformat()
        
        url = f"https://a.klaviyo.com/api/events?filter=equals(metric_id,\"{metric_id}\"),equals(profile_id,\"{profile_id}\"),greater-or-equal(datetime,{date_filter_iso})"
        
        headers = {
            "Authorization": api_key,
            "Accept": "application/vnd.api+json",
            "Revision": "2024-10-15"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    metric_response = get_klaviyo_metric(api_key, metric_id, profile_id)
    count = 0
    for item in metric_response['data']:
        if item.get("attributes", {}).get("event_properties", {}).get("ProductName", {}) == product_name:
            count += 1
            print('item added')
        else:
            print('item not added')

    print(count)
    event_payload = {'Times Seen': count}

    def create_klaviyo_event(api_key, profile_id):
        url = "https://a.klaviyo.com/api/events"
        headers = {
            "Authorization": api_key,
            "Accept": "application/vnd.api+json",
            "Revision": "2024-10-15",
            "Content-Type": "application/vnd.api+json"
        }

        payload = {
            "data": {
                "type": "event",
                "attributes": {
                    "properties": event_properties,
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
                                    "patch_properties": {}
                                },
                                "id": profile_id
                            }
                        }
                    },
                    "value": 19.98
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 202:
            print('Event created successfully')
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    if count >= 3:
        create_klaviyo_event(api_key, profile_id)
