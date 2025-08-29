from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """
    Weekly CRM report:
    - Total customers
    - Total orders
    - Total revenue
    """
    log_file = "/tmp/crm_report_log.txt"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL query
        query = gql(
            """
            query {
                customersCount
                ordersCount
                totalRevenue
            }
            """
        )

        result = client.execute(query)

        customers = result.get("customersCount", 0)
        orders = result.get("ordersCount", 0)
        revenue = result.get("totalRevenue", 0)

        report = f"{now} - Report: {customers} customers, {orders} orders, {revenue} revenue"

        with open(log_file, "a") as f:
            f.write(report + "\n")

        return report

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{now} - Error generating report: {e}\n")
        return str(e)
