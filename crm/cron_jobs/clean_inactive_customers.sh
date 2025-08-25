#!/bin/bash
# Script to delete inactive customers (no orders in the past year) and log the result

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$(dirname "$0")/../.."

DELETED=$(python3 manage.py shell -c "import datetime; from crm.models import Customer, Order; cutoff = datetime.datetime.now() - datetime.timedelta(days=365); to_delete = Customer.objects.exclude(order__date__gte=cutoff).distinct(); count = to_delete.count(); to_delete.delete(); print(count)")

if [ $? -eq 0 ]; then
    echo "$TIMESTAMP - Deleted $DELETED inactive customers" >> "$LOG_FILE"
else
    echo "$TIMESTAMP - Cleanup failed" >> "$LOG_FILE"
fi
