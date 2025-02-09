from napkin import requests, response, request
import json
import os

# Take incoming data and parse it as a JSON Object
data_str = request.data #saves data in a variable
data = json.loads(data_str) #converts data in a JSON object
payload_str = data.get("payload") #saves event payload in a variable
payload_str = payload_str.replace("'", "\"")# replace single quotes with double quotes
event_payload = json.loads(payload_str) # variable with JSON object

profile_id = data.get('id')
product = event_payload.get('ProductName')


api_key = os.environ.get('API_KEY')
metric_id = os.environ.get('METRIC_ID')


def get_klaviyo_metric(api_key, metric_id, profile_id):
    
    url = f"https://a.klaviyo.com/api/events?filter=equals(metric_id,\"{metric_id}\"),equals(profile_id,\"{profile_id}\")"
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
    if item.get("attributes",{}).get("event_properties", {}).get("ProductName", {}) == product:
        count += 1
        print('item added')
    else:
        print('item not added')

print(count)

event_payload['Times Seen'] = count

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
          "properties": event_payload,
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
                    "append": {
                      "newKey": "New Value"
                    },
                    "unappend": {
                      "newKey": "New Value"
                    }
                  }
                },
                "id": profile_id
              }
            }
          },
          "value": 19.98
        }
      }
    }
    

    response = requests.post(url, headers=headers,data=json.dumps(payload))

    if response.status_code == 202:
        print('Event created successfully')
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


if count >= 2:
    create_klaviyo_event(api_key, profile_id)
