# Kibana Exercise: Data Visualization and Analysis

## Overview
This exercise will guide you through using Kibana to analyze and visualize data from multiple sources. You'll work with web logs, e-commerce transactions, system metrics, and application logs to create meaningful dashboards and perform various queries.

## Prerequisites
- Elasticsearch and Kibana running locally
- Python 3.x with `faker` library installed
- Basic understanding of JSON and log formats

## Setup

### 1. Install Dependencies
```bash
pip install faker
```

### 2. Generate Sample Data
```bash
# Generate all types of sample data (4000 records total)
python generate_sample_data.py --count 1000 --output sample_data.json

# Or generate specific data types
python generate_sample_data.py --type web_logs --count 500 --output web_logs.json
python generate_sample_data.py --type ecommerce --count 500 --output ecommerce.json
```

### 3. Import Data into Elasticsearch
```bash
# Create the index and import data
curl -X PUT "localhost:9200/sample-data" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "ip_address": { "type": "ip" },
      "status_code": { "type": "integer" },
      "response_time_ms": { "type": "integer" },
      "cpu_usage_percent": { "type": "float" },
      "memory_usage_percent": { "type": "float" },
      "total_amount": { "type": "float" },
      "data_type": { "type": "keyword" }
    }
  }
}'

# Import the data
curl -X POST "localhost:9200/sample-data/_bulk" -H 'Content-Type: application/json' --data-binary @sample_data.json
```

## Part 1: Basic Kibana Queries and Filters

### Exercise 1.1: Discover Data
1. Open Kibana (http://localhost:5601)
2. Go to **Discover** and create an index pattern for `sample-data`
3. Set the time field to `timestamp`

**Tasks:**
- Explore the different data types by filtering on `data_type`
- Find all HTTP 404 errors in web logs
- Locate e-commerce transactions over $100
- Identify system metrics where CPU usage > 80%

### Exercise 1.2: KQL (Kibana Query Language) Practice

Write KQL queries for the following:

1. **Web Traffic Analysis:**
   ```KQL
   data_type: "web_log" AND status_code: 404
   ```

   ```KQL
   data_type: "web_log" AND response_time_ms > 1000
   ```

   This is in Lucene syntax (can be toggled to instead of KQL syntax)
   ```LUCENE
   data_type: "web_log" AND method: "POST" AND status_code: [200 TO 299]
   ```

2. **E-commerce Insights:**
   ```KQL
   data_type: "ecommerce" AND total_amount > 100
   ```

   ```KQL
   data_type: "ecommerce" AND product_category: "Electronics" AND payment_method: "credit_card"
   ```

   ```LUCENE
   data_type: "ecommerce" AND customer_age: [25 TO 35] AND is_mobile: true
   ```

3. **System Monitoring:**
   ```
   data_type: "system_metrics" AND cpu_usage_percent > 80
   data_type: "system_metrics" AND memory_usage_percent > 70 AND cpu_usage_percent > 70
   server_name: "server-01" AND load_average > 2.0
   ```

4. **Application Logs:**
   ```
   data_type: "application_log" AND level: "ERROR"
   service: "payment-service" AND duration_ms > 500
   level: ("ERROR" OR "FATAL") AND service: "auth-service"
   ```

### Exercise 1.3: Time-based Filtering
1. Filter data for the last 7 days
2. Create a custom time range for specific dates
3. Use relative time filters (e.g., "Last 4 hours", "Yesterday")

## Part 2: Visualizations

### Exercise 2.1: Web Analytics Dashboard

Create the following visualizations:

1. **Response Time Distribution**
   - Chart type: Histogram
   - Field: `response_time_ms`
   - Filter: `data_type: "web_log"`

2. **HTTP Status Codes**
   - Chart type: Pie chart
   - Field: `status_code`
   - Filter: `data_type: "web_log"`

3. **Traffic by Country**
   - Chart type: Data table or World map
   - Field: `country`
   - Metric: Count of requests

4. **Requests Over Time**
   - Chart type: Line chart
   - X-axis: `timestamp` (Date histogram)
   - Y-axis: Count of documents

### Exercise 2.2: E-commerce Analytics

1. **Sales by Category**
   - Chart type: Vertical bar chart
   - X-axis: `product_category`
   - Y-axis: Sum of `total_amount`

2. **Payment Method Distribution**
   - Chart type: Donut chart
   - Field: `payment_method`

3. **Mobile vs Desktop Sales**
   - Chart type: Metric visualization
   - Split by `is_mobile`
   - Metric: Average `total_amount`

4. **Customer Demographics**
   - Chart type: Heat map
   - X-axis: `customer_age` (ranges: 18-25, 26-35, 36-50, 51+)
   - Y-axis: `customer_gender`
   - Metric: Count

### Exercise 2.3: System Monitoring Dashboard

1. **CPU Usage Gauge**
   - Chart type: Gauge
   - Field: Average of `cpu_usage_percent`
   - Ranges: Green (0-70), Yellow (70-85), Red (85-100)

2. **Memory vs CPU Scatter Plot**
   - Chart type: Line chart (with dots)
   - X-axis: `cpu_usage_percent`
   - Y-axis: `memory_usage_percent`

3. **Server Performance Comparison**
   - Chart type: Horizontal bar chart
   - X-axis: `server_name`
   - Y-axis: Average `load_average`

4. **Network Traffic Time Series**
   - Chart type: Area chart
   - X-axis: `timestamp`
   - Y-axis: Sum of `network_in_mbps` and `network_out_mbps`

## Part 3: Advanced Analytics

### Exercise 3.1: Creating Calculated Fields

1. **Response Time Categories**
   - Create a runtime field to categorize response times:
     - Fast: < 200ms
     - Medium: 200-1000ms
     - Slow: > 1000ms

2. **Revenue Brackets**
   - Create a runtime field for transaction amounts:
     - Small: $0-$50
     - Medium: $50-$200
     - Large: > $200

### Exercise 3.2: Aggregations and Bucket Analysis

1. **Peak Hours Analysis**
   - Use date histogram with hourly buckets
   - Find the busiest hours for web traffic
   - Identify peak shopping hours for e-commerce

2. **Error Rate Calculation**
   - Calculate percentage of HTTP errors (4xx, 5xx) vs total requests
   - Create a metric showing error rate trend over time

3. **Customer Lifetime Value**
   - Group by `customer_email`
   - Calculate total purchase amount per customer
   - Find top 10 customers by spending

### Exercise 3.3: Alerting and Monitoring

1. **High Error Rate Alert**
   - Create a watcher/alert for when error rate exceeds 5%
   - Trigger: HTTP status codes 4xx or 5xx

2. **System Resource Alert**
   - Alert when CPU usage > 90% for more than 5 minutes
   - Alert when memory usage > 85%

3. **Revenue Drop Alert**
   - Alert when hourly revenue drops below average by 30%

## Part 4: Dashboard Creation

### Exercise 4.1: Executive Dashboard

Create a comprehensive dashboard with:

1. **Key Performance Indicators (KPIs)**
   - Total requests (last 24h)
   - Average response time
   - Error rate percentage
   - Total revenue (last 24h)

2. **Traffic Overview**
   - Requests timeline (last 7 days)
   - Top 10 URLs by traffic
   - Geographic distribution

3. **System Health**
   - Average CPU/Memory usage by server
   - Response time percentiles (50th, 90th, 95th)

### Exercise 4.2: Operational Dashboard

1. **Real-time Monitoring**
   - Current system metrics (last 5 minutes)
   - Active alerts count
   - Recent error logs

2. **Performance Trends**
   - Response time trends (last 24h)
   - Error rate trends
   - Resource utilization trends

## Part 5: Data Exploration Challenges

### Challenge 1: Anomaly Detection
Find unusual patterns in the data:
- Identify IP addresses making unusually high requests
- Detect servers with abnormal resource usage
- Find customers with suspicious transaction patterns

### Challenge 2: Correlation Analysis
Explore relationships between different metrics:
- Does response time correlate with server load?
- Are mobile users more likely to use certain payment methods?
- Do certain countries have higher error rates?

### Challenge 3: Seasonality and Trends
- Identify patterns in web traffic throughout the day
- Find peak shopping periods
- Analyze system resource usage patterns

## Bonus Exercises

### Machine Learning Integration
1. Use Kibana's ML features to detect anomalies in:
   - Web traffic patterns
   - Transaction amounts
   - System resource usage

### Custom Visualizations
1. Create a custom visualization plugin for:
   - Network topology view
   - Customer journey mapping
   - Performance correlation matrix

### Data Transformation
1. Use Elasticsearch ingest pipelines to:
   - Enrich IP addresses with geolocation data
   - Parse user agents for browser/OS information
   - Calculate derived metrics at index time

## Expected Deliverables

1. Screenshots of your dashboards
2. Saved searches for complex queries
3. Documentation of interesting findings
4. Export of your dashboard configurations

## Tips for Success

- Use filters effectively to focus on relevant data
- Experiment with different visualization types
- Pay attention to time ranges when analyzing trends
- Use aggregations to summarize large datasets
- Save your work frequently
- Document your queries for future reference

## Troubleshooting

- **No data visible**: Check your time range and index pattern
- **Slow queries**: Add appropriate filters to reduce dataset size
- **Visualization errors**: Verify field mappings and data types
- **Memory issues**: Use date ranges to limit data scope

## Further Reading

- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [KQL Query Language Reference](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)
- [Elasticsearch Aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html)
