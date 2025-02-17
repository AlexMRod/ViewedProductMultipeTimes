# Viewed Product Multiple Time Generator Script

## Overview

This script is triggered by the Viewed Product events and uses the Klaviyo Get Event API to check how many times a specific product has been viewed. If the product has been viewed multiple times, it triggers a new event called "Viewed Event Multiple Times" using Klaviyo's Create Event API. This allows Klaviyo users to trigger Abandoned Cart flows only if a customer has viewed a specific product more than one time and help them target customer with more relevant content.

## Prerequisites

1. **A Klaviyo Account with Flow Custom Actions**:
See [Add a custom action to a flow](https://developers.klaviyo.com/en/docs/add_a_custom_action_to_a_flow) for elegiblity and documentation.
2. **If not elegible for Custom Actions, open a free account on [Napkin.io](https://napkin.io)**: This alternative solution requires a middleware like Napkin.io to receive data from Klaviyo and process it.
3. **Set up your Klaviyo Private API key and the Viewed Product metric ID as environment variables**. For more details, see [Custom Actions - Environmentable Variables](https://developers.klaviyo.com/en/docs/add_a_custom_action_to_a_flow#environment-variables) or [Python Environment Variables - Napkin.io](https://docs.napkin.io/python/environment-variables).

## NOTE

Use **MultipleProductViews_CustomAction.py** if using Custom Actions and **Multiple Product Views_webhook.py** for implementation through Napkin.io

## How It Works

### Step 1: Parsing Incoming Data

The script expects incoming data in JSON format. It parses the data to extract the following details:

- `profile_id`: The unique ID of the customer profile.
- `product`: The name of the product that triggered the event.

### Step 2: Fetch Event Data from Klaviyo

The script uses the `profile_id` and `metric_id` in the `get_event_data` function to query the Klaviyo API. A variable called `date_filter_iso` is used to limit the response to a specific timeframe.

### Step 3: Count Views

The script counts how many times the specified product has been viewed by checking the event data. If the product has been viewed multiple times, the script increments the count.

### Step 4: Trigger New Event

If the product has been viewed more than 3 times, the script triggers a new event in Klaviyo using the `create_klaviyo_event` function. The new event includes the following details:

- **Metric Name**: "Viewed Product Multiple Times"
- **Profile ID**: The profile ID of the user who viewed the product.
- **Event Payload**: Includes all data from the Viewed Product event, along with a `Times Viewed` property indicating how many times the product has been viewed.

## How to Customize the Script

### 1. Adjust Event Tracking

To track different events or event properties, simply change the `metric_id` or the `product` variables in the script. For example:

- Update the `metric_id` to track different event types. This script was originally written for the Viewed Product event but can be adapted to track other events like Order Product.
- You can also include additional filters to the URL endpoint in the `get_klaviyo_metric` function. For more information, check out [Get Events API](https://developers.klaviyo.com/en/reference/get_events).

### 2. Modify Event Trigger Conditions

The script is currently set to trigger the new event if the product is viewed more than once (`count >= 3`). You can modify this threshold to suit your requirements:

```python
if count >= YOUR_THRESHOLD:
    create_klaviyo_event(api_key, profile_id)
```

## Implementing the solution

1. In your Klaviyo account, set up a Flow triggered by the Viewed Product event.
2. If using Custom Actions, set up the Custom Action following our documentation and include the script in MultipleProcutViews_CustomAction.py (skip to step 7)
3. If you are using napkin.io, add a [Flow Webhook Action](https://developers.klaviyo.com/en/docs/how_to_add_a_webhook_action_to_a_flow).
4. In Napkin.io, [create a new function](https://docs.napkin.io/guides/quick-start), add the script in MultipleProductViews_webhook.py and deploy the function.
5. Enter the function URL provided by Napkin.io as the Flow Webhook endpoint.
6. Enter the following payload in JSON Body:

```json
{
    "id": "{{ person.KlaviyoID }}",
    "payload":"{{ event }}"
}
```

7. Create a a Browse Abandonment Flow triggered off the new Viewed Product Multiple times event and use the same logic you would use in your standard Browse Abandonment event.
