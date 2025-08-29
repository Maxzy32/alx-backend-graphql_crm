#!/bin/bash
# Script to delete inactive customers (no orders in the past year)

# Navigate to the project root (adjust path if needed)
cd "$(dirname "$0")/../.."

# Run the Django cleanup command using manage.py shell
deleted_count=$(python3 manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $deleted_count\" >> /tmp/customer_cleanup_log.txt
