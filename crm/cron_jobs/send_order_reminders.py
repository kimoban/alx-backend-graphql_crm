import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"
TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range for last 7 days
now = datetime.datetime.now()
week_ago = now - datetime.timedelta(days=7)

query = gql('''
query GetRecentOrders($from: DateTime!, $to: DateTime!) {
  orders(orderDate_Gte: $from, orderDate_Lte: $to, status: "pending") {
    id
    customer {
      email
    }
    orderDate
  }
}
''')

params = {"from": week_ago.isoformat(), "to": now.isoformat()}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])
    with open(LOG_FILE, "a") as f:
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            f.write(f"{TIMESTAMP} - Order ID: {order_id}, Customer Email: {email}\n")
    print("Order reminders processed!")
except Exception as e:
    with open(LOG_FILE, "a") as f:
        f.write(f"{TIMESTAMP} - Error: {e}\n")
    print("Order reminders processed!")
