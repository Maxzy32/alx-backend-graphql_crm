# import os
# from datetime import datetime
# import requests

# def log_crm_heartbeat():
#     """
#     Logs a heartbeat message every 5 minutes.
#     Format: DD/MM/YYYY-HH:MM:SS CRM is alive
#     """
#     log_file = "/tmp/crm_heartbeat_log.txt"
#     now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
#     message = f"{now} CRM is alive"

#     # Append to the log file
#     with open(log_file, "a") as f:
#         f.write(message + "\n")

#     # Optional: check GraphQL hello endpoint
#     try:
#         response = requests.post(
#             "http://localhost:8000/graphql",
#             json={"query": "{ hello }"},
#             timeout=5,
#         )
#         if response.ok:
#             with open(log_file, "a") as f:
#                 f.write(f"{now} GraphQL responded: {response.json()}\n")
#         else:
#             with open(log_file, "a") as f:
#                 f.write(f"{now} GraphQL did not respond correctly\n")
#     except Exception as e:
#         with open(log_file, "a") as f:
#             f.write(f"{now} Error querying GraphQL: {e}\n")


from datetime import datetime
import os

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Also optionally queries GraphQL hello field.
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    # Append to heartbeat log
    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Optional: GraphQL hello query
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
            query {
                hello
            }
            """
        )
        result = client.execute(query)
        with open(log_file, "a") as f:
            f.write(f"{now} GraphQL hello response: {result}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{now} Error querying GraphQL: {e}\n")
