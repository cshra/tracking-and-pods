import requests
import base64
import json


def authenticate():
    url = "https://apis.fedex.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Authentication failed")


def get_tracking_details(tracking_numbers, access_token):
    url = "https://apis.fedex.com/track/v1/trackingnumbers"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "trackingInfo": [
            {
                "trackingNumberInfo": {
                    "trackingNumber": tracking_number
                }
            }],
        "includeDetailedScans": True
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve tracking details")


def request_proof_of_delivery(tracking_number, access_token):
    url = "https://apis.fedex.com/track/v1/trackingdocuments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "trackDocumentDetail": {
            "documentType": "SIGNATURE_PROOF_OF_DELIVERY",
            "documentFormat": "PDF"
        },
        "trackDocumentSpecification": [
            {
                "trackingNumberInfo": {
                    "trackingNumber": tracking_number,

                }
            }
        ],

    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to request proof of delivery")


def save_proof_of_delivery(tracking_number, proof_of_delivery):
    if "documents" in proof_of_delivery["output"]:
        document_data = proof_of_delivery["output"]["documents"]
        decoded_data = base64.b64decode(str(document_data))
        file_path = f"{tracking_number}_proof_of_delivery.pdf"
        with open(file_path, "wb") as file:
            file.write(decoded_data)
        print(f"Proof of delivery saved as: {file_path}")
    else:
        print(
            f"No proof of delivery available for tracking number: {tracking_number}")


# Main script
tracking_numbers = input(
    "Enter tracking number(s) (comma-separated for multiple): ").split(",")
tracking_numbers = [number.strip() for number in tracking_numbers]

access_token = authenticate()

for tracking_number in tracking_numbers:
    tracking_details = get_tracking_details([tracking_number], access_token)
    latest_status = tracking_details["output"]["completeTrackResults"][0]["trackResults"][0]["latestStatusDetail"]
    print(
        f"\nLatest status for {tracking_number}: {latest_status['description']}")

    if latest_status["code"] == "DL":
        proof_of_delivery = request_proof_of_delivery(
            tracking_number, access_token)
        save_proof_of_delivery(tracking_number, proof_of_delivery)
