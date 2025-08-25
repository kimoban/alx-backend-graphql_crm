import datetime
import requests

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = '/tmp/crm_heartbeat_log.txt'
    message = f"{now} CRM is alive"
    try:
        # Optional: Query GraphQL hello field
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'}
        )
        if response.ok:
            message += f" | GraphQL: {response.json().get('data', {}).get('hello', 'No response')}"
        else:
            message += " | GraphQL: No response"
    except Exception as e:
        message += f" | GraphQL: Error {e}"
    with open(log_file, 'a') as f:
        f.write(message + '\n')
