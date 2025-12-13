#!/bin/bash

# Import Grafana dashboards via API
# Usage: ./import_dashboards.sh

GRAFANA_URL="http://grogu:3333"
GRAFANA_USER="admin"
GRAFANA_PASSWORD="admin"
DASHBOARD_DIR="/Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app/grafana/dashboards"

echo "Importing Grafana dashboards..."
echo "Grafana URL: $GRAFANA_URL"
echo "Dashboard directory: $DASHBOARD_DIR"
echo ""

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -o /dev/null -w "%{http_code}" "$GRAFANA_URL/api/health" | grep -q "200"; then
        echo "Grafana is ready!"
        break
    fi
    echo "Attempt $((attempt+1))/$max_attempts - Grafana not ready yet..."
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Grafana did not become ready in time"
    exit 1
fi

echo ""
echo "Importing dashboards..."
echo ""

# Import each dashboard
for dashboard_file in "$DASHBOARD_DIR"/*.json; do
    dashboard_name=$(basename "$dashboard_file")
    echo "Importing: $dashboard_name"

    # Read the dashboard JSON and wrap it in the import format
    dashboard_json=$(cat "$dashboard_file")

    # Create import payload
    import_payload=$(cat <<EOF
{
  "dashboard": $(echo "$dashboard_json" | jq '.dashboard'),
  "overwrite": true,
  "inputs": [],
  "folderId": 0
}
EOF
)

    # Import via API
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
        -d "$import_payload" \
        "$GRAFANA_URL/api/dashboards/db")

    # Check if successful
    if echo "$response" | jq -e '.status == "success"' > /dev/null 2>&1; then
        dashboard_url=$(echo "$response" | jq -r '.url')
        echo "  ✅ SUCCESS - Dashboard URL: $GRAFANA_URL$dashboard_url"
    else
        echo "  ❌ FAILED - Response: $response"
    fi

    echo ""
done

echo "Dashboard import complete!"
echo ""
echo "Access Grafana at: $GRAFANA_URL"
echo "  Username: $GRAFANA_USER"
echo "  Password: $GRAFANA_PASSWORD"
