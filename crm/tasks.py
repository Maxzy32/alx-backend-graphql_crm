import requests
import logging
from datetime import datetime
from celery import shared_task

logger = logging.getLogger(__name__)

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql/"

@shared_task
def generate_crm_report():
    query = """
    query {
        customers {
            id
        }
        orders {
            id
            totalAmount
        }
    }
    """

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        response.raise_for_status()
        data = response.json().get("data", {})

        customers = data.get("customers", [])
        orders = data.get("orders", [])

        total_customers = len(customers)
        total_orders = len(orders)
        total_revenue = sum(order.get("totalAmount", 0) for order in orders)

        # Format log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"

        # Write to log file
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(report + "\n")

        logger.info("CRM Report generated successfully: %s", report)

    except Exception as e:
        logger.error("Failed to generate CRM report: %s", str(e))
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()} - ERROR: {str(e)}\n")
