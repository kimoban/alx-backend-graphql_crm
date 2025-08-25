
from datetime import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from celery import shared_task

@shared_task
def generate_crm_report():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = '/tmp/crm_report_log.txt'
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql('''
            query {
                allCustomers { totalCount }
                allOrders { totalCount edges { node { totalAmount } } }
            }
        ''')
        result = client.execute(query)
        num_customers = result.get('allCustomers', {}).get('totalCount', 0)
        orders_data = result.get('allOrders', {})
        num_orders = orders_data.get('totalCount', 0)
        total_revenue = 0
        for edge in orders_data.get('edges', []):
            node = edge.get('node', {})
            amt = node.get('totalAmount')
            if amt:
                try:
                    total_revenue += float(amt)
                except Exception:
                    pass
        message = f"{now} - Report: {num_customers} customers, {num_orders} orders, {total_revenue} revenue"
    except Exception as e:
        message = f"{now} - Error generating report: {e}"
    with open(log_file, 'a') as f:
        f.write(message + '\n')
