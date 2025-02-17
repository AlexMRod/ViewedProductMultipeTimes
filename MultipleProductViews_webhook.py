from napkin import requests, response, request
import json
import os
import datetime

# Take incoming data and parse it as a JSON Object
data_str = request.data # saves all data in a variable
data = json.loads(data_str) # converts data to a JSON object
payload_str = data.get("payload") # saves event payload in a variable
payload_str = payload_str.replace("'", "\"")# replace single quotes with double quotes
event_payload = json.loads(payload_str) # stores payload JSON object in a variable

profile_id = data.get('id')
product = event_payload.get('ProductName') # value to check in event data
api_key = os.environ.get('API_KEY')
metric_id = os.environ.get('METRIC_ID')

def get_klaviyo_metric(api_key, metric_id, profile_id):
  # Set date for date URL filter (7 days)
    today = datetime.datetime.now(datetime.timezone.utc)
    date_filter = today - datetime.timedelta(days=7)
    date_filter_iso = date_filter.isoformat()


    url = (
        f"https://a.klaviyo.com/api/events?filter=equals(metric_id,\"{metric_id}\"),equals(profile_id,\"{profile_id}\"),greater-or-equal(datetime,{date_filter_iso})"
    )

    headers = {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "Accept": "application/vnd.api+json",
        "Revision": "2024-10-15"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

print(api_key)

metric_response = get_klaviyo_metric(api_key, metric_id, profile_id)

count = 0
for item in metric_response['data']:
    if item.get("attributes",{}).get("event_properties", {}).get("ProductName", {}) == product:
        count += 1
        print('item added')
    else:
        print('item not added')


event_payload['Times Seen'] = count

def create_klaviyo_event(api_key, profile_id):
    
    url = "https://a.klaviyo.com/api/events"
    headers = {
        "Authorization": f"Klaviyo-API-Key {api_key}",
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
                  "patch_properties": {}
                },
                "id": profile_id
              }
            }
          }
        }
      }
    }
    

    response = requests.post(url, headers=headers,data=json.dumps(payload))

    if response.status_code == 202:
        print('Event created successfully')
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


if count >= 3:
    create_klaviyo_event(api_key, profile_id)
