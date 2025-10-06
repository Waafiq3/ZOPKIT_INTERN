import requests
import json

def test_purchase_order_classification():
    test_messages = [
        'I want to create a purchase order',
        'Create a purchase order', 
        'purchase order',
        'I need to make a purchase order'
    ]
    
    for msg in test_messages:
        try:
            response = requests.post('http://localhost:5001/chat', json={'message': msg}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f'Message: {msg}')
                print(f'Response: {data.get("response", "No response")[:200]}...')
                print(f'Status: {data.get("status", "unknown")}')
                print('---')
            else:
                print(f'HTTP Error {response.status_code} for: {msg}')
        except Exception as e:
            print(f'Error for "{msg}": {e}')
            break

if __name__ == "__main__":
    print("Testing Purchase Order Classification...")
    test_purchase_order_classification()