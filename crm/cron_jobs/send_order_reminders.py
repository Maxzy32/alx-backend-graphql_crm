#!/usr/bin/env python3
"""
Script to query recent pending orders via GraphQL and log reminders.
"""

import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Calculate date range (last 7 days)
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # Define GraphQL query
        query = gql(
            """
            query GetRecentOrders($startDate: Date!) {
                orders(orderDate_Gte: $startDate) {
                    id
                    customer {
                        email
                    }
                }
            }
            """
        )

        # Execute query
        result = client.execute(query, variable_values={"startDate": str(week_ago)})

        orders = result.get("orders", [])
        if not orders:
            logging.info("No recent orders found.")
        else:
            for order in orders:
                order_id = order.get("id")
                customer_email = order.get("customer", {}).get("email")
                logging.info(f"Order ID: {order_id}, Customer Email: {customer_email}")

        # Print success message to console
        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error processing order reminders: {e}")
        print("Order reminders failed!", file=sys.stderr)

if __name__ == "__main__":
    main()
