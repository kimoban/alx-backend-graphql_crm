import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = '/tmp/crm_heartbeat_log.txt'
    message = f"{now} CRM is alive"
    try:
        # Query GraphQL hello field using gql
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql('{ hello }')
        result = client.execute(query)
        hello_value = result.get('hello', 'No response')
        message += f" | GraphQL: {hello_value}"
    except Exception as e:
        message += f" | GraphQL: Error {e}"
    with open(log_file, 'a') as f:
        f.write(message + '\n')


def update_low_stock():
    now = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = '/tmp/low_stock_updates_log.txt'
    message = f"{now} Low stock update: "
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        mutation = gql('''
            mutation {
                updateLowStockProducts {
                    updatedProducts { name stock }
                    message
                }
            }
        ''')
        result = client.execute(mutation)
        data = result.get('updateLowStockProducts', {})
        updated = data.get('updatedProducts', [])
        msg = data.get('message', '')
        if updated:
            for prod in updated:
                message += f"{prod['name']} (stock: {prod['stock']}), "
        else:
            message += "No products updated. "
        message += msg
    except Exception as e:
        message += f"Error: {e}"
    with open(log_file, 'a') as f:
        f.write(message + '\n')
