import requests
import json

# Replace this string variable with your copied Google Apps Script URL endpoint
TARGET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwk1jWYyo7Lz2fXkh2QQcfLQB__X2BbRoB4wUzIQTgO6KTLeGd-xsHPp9n0rc-Zt-RG/exec"

def test_pipeline_transmission():
    print("📡 Initializing cloud gateway transmission check...")
    
    # Mock data packet simulating a tool inventory ingestion transaction
    mock_payload = {
        "serial_number": "SN-PC210-HYD-9982",
        "item_name": "Premium Hydraulic Pressure Seal Kit",
        "category": "Heavy Machinery Parts",
        "transaction_type": "RESTOCK_INFLOW",
        "quantity": 5,
        "operator": "Azicio: Codespaces Console"
    }
    
    try:
        response_packet = requests.post(
            TARGET_WEBHOOK_URL, 
            data=json.dumps(mock_payload),
            headers={"Content-Type": "application/json"},
            timeout=7.0
        )
        
        print(f"📊 Transmission Response Status Code: {response_packet.status_code}")
        print(f"📥 Server Response Payload: {response_packet.text}")
        
    except Exception as network_error:
        print(f"🛑 Critical Transmission Anomaly: {str(network_error)}")

if __name__ == "__main__":
    test_pipeline_transmission()
