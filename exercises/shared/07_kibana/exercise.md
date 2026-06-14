# Kibana Exercise: Data Visualization and Analysis

## Overview

This exercise will guide you through using Kibana to analyze and visualize data
from multiple sources. You'll work with web logs, e-commerce transactions,
system metrics, and application logs to create meaningful dashboards and perform
various queries.

Kibana is the visualization and exploration layer that sits on top of
Elasticsearch. Elasticsearch stores and indexes your documents and answers
search and aggregation requests; Kibana turns those answers into tables,
charts, and dashboards without you having to write raw queries by hand. Every
chart you build in Kibana is really just a friendly front end for an
Elasticsearch query running underneath. Understanding that relationship is the
key to this whole exercise: when a visualization looks wrong, the question to
ask is "what query is this actually sending, and what does the data look like?"

A useful detail about this dataset is that four very different record shapes
(web logs, e-commerce transactions, system metrics, and application logs) all
live in a single index called `sample-data`. They are told apart by a
`data_type` field. This mirrors a common real-world pattern and is why almost
every query below starts by filtering on `data_type`: you are first narrowing
down to one kind of record before you analyze it.

## Prerequisites

- Elasticsearch and Kibana running locally
- Python 3.x with `faker` library installed
- Basic understanding of JSON and log formats

## Setup

### 1. Install Dependencies

The data generator uses the `faker` library to invent realistic-looking values
such as IP addresses, country codes, emails, and timestamps. This lets you
practice on data that behaves like production traffic without exposing any real
user information.

```bash
pip install faker
```

### 2. Generate Sample Data

See [`01_generate_sample_data.sh`](./01_generate_sample_data.sh)

This step runs a Python script that creates the four record types and writes
them out already formatted for Elasticsearch's bulk API. A few things worth
knowing about what it produces:

- Each e-commerce record's `total_amount` is computed as `quantity * unit_price`
  rather than stored independently, so the number is always internally
  consistent.
- All records are stamped with timestamps spread across the last 30 days, then
  sorted by time. This is what makes the time-based filtering and date
  histogram exercises later on meaningful.
- Every record carries a `data_type` tag so the four shapes can coexist in one
  index.

### 3. Import Data into Elasticsearch

See [`02_create_index_and_import.sh`](./02_create_index_and_import.sh)

This step does two distinct things, and the order matters. First it creates the
`sample-data` index with an explicit mapping, then it bulk-imports the
documents.

The mapping is the most important part to understand. A mapping is
Elasticsearch's schema: it declares the data type of each field. Here a handful
of fields are pinned deliberately:

- `timestamp` is mapped as `date` so Kibana can use it as the time field and
  build date histograms.
- `ip_address` is mapped as `ip`, a special type that understands address
  ranges and subnets.
- `status_code` and `response_time_ms` are `integer`, and the usage and amount
  fields are `float`, so numeric range queries and math work correctly.
- `data_type` is mapped as `keyword`, meaning it is treated as an exact,
  non-analyzed string. Keyword fields are what you filter and aggregate on;
  this is why grouping by `data_type` works cleanly.

**Why this matters:** if you skip the mapping and let Elasticsearch guess, it
often infers the wrong types. A timestamp imported as plain text cannot drive a
time filter, and a number imported as text cannot be summed or compared with
`>`. Defining the mapping up front, before any data is imported, avoids having
to delete the index and start over. The bulk import that follows sends the
documents in Elasticsearch's bulk format, where each document is preceded by a
line describing the action to take. That paired-line format is exactly what the
generator script wrote out, which is why the two scripts fit together.

## Part 1: Basic Kibana Queries and Filters

Before you can build any chart, Kibana needs to know which index holds your
data and which field represents time. That is the job of an index pattern (also
called a data view). It is a saved pointer that tells Kibana "search the
`sample-data` index, and treat `timestamp` as the time field." Once that
pattern exists, Discover, visualizations, and dashboards all share it.

### Exercise 1.1: Discover Data

1. Open Kibana (<http://localhost:5601>)
1. Go to **Discover** and create an index pattern for `sample-data`
1. Set the time field to `timestamp`

Discover is your raw exploration view. It shows individual matching documents
plus a small bar chart of how many documents fall in each time bucket. It is
the best place to confirm your data actually arrived and to learn what fields
exist before you commit to a chart. If Discover is empty, the cause is almost
always the time range (top right) rather than a missing import.

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

   ```KQL
   data_type: "web_log" AND method: "POST"
     AND status_code >= 200 AND status_code <= 299
   ```

   This is in Lucene syntax (can be toggled to instead of KQL syntax)

   ```LUCENE
   data_type: "web_log" AND method: "POST" AND status_code: [200 TO 299]
   ```

1. **E-commerce Insights:**

   ```KQL
   data_type: "ecommerce" AND total_amount > 100
   ```

   ```KQL
   data_type: "ecommerce" AND product_category: "Electronics"
     AND payment_method: "credit_card"
   ```

   ```LUCENE
   data_type: "ecommerce" AND customer_age: [25 TO 35] AND is_mobile: true
   ```

1. **System Monitoring:**

   ```
   data_type: "system_metrics" AND cpu_usage_percent > 80
   data_type: "system_metrics"
     AND memory_usage_percent > 70 AND cpu_usage_percent > 70
   server_name: "server-01" AND load_average > 2.0
   ```

1. **Application Logs:**

   ```
   data_type: "application_log" AND level: "ERROR"
   service: "payment-service" AND duration_ms > 500
   level: ("ERROR" OR "FATAL") AND service: "auth-service"
   ```

### Exercise 1.3: Time-based Filtering

1. Filter data for the last 7 days
1. Create a custom time range for specific dates
1. Use relative time filters (e.g., "Last 4 hours", "Yesterday")

## Part 2: Visualizations

### Exercise 2.1: Web Analytics Dashboard

Create the following visualizations:

1. **Response Time Distribution**
   - Chart type: Histogram
   - Field: `response_time_ms`
   - Filter: `data_type: "web_log"`

1. **HTTP Status Codes**
   - Chart type: Pie chart
   - Field: `status_code`
   - Filter: `data_type: "web_log"`

1. **Traffic by Country**
   - Chart type: Data table or World map
   - Field: `country`
   - Metric: Count of requests

1. **Requests Over Time**
   - Chart type: Line chart
   - X-axis: `timestamp` (Date histogram)
   - Y-axis: Count of documents

### Exercise 2.2: E-commerce Analytics

1. **Sales by Category**
   - Chart type: Vertical bar chart
   - X-axis: `product_category`
   - Y-axis: Sum of `total_amount`

1. **Payment Method Distribution**
   - Chart type: Donut chart
   - Field: `payment_method`

1. **Mobile vs Desktop Sales**
   - Chart type: Metric visualization
   - Split by `is_mobile`
   - Metric: Average `total_amount`

1. **Customer Demographics**
   - Chart type: Heat map
   - X-axis: `customer_age` (ranges: 18-25, 26-35, 36-50, 51+)
   - Y-axis: `customer_gender`
   - Metric: Count

### Exercise 2.3: System Monitoring Dashboard

1. **CPU Usage Gauge**
   - Chart type: Gauge
   - Field: Average of `cpu_usage_percent`
   - Ranges: Green (0-70), Yellow (70-85), Red (85-100)

1. **Memory vs CPU Scatter Plot**
   - Chart type: Line chart (with dots)
   - X-axis: `cpu_usage_percent`
   - Y-axis: `memory_usage_percent`

1. **Server Performance Comparison**
   - Chart type: Horizontal bar chart
   - X-axis: `server_name`
   - Y-axis: Average `load_average`

1. **Network Traffic Time Series**
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

1. **Revenue Brackets**
   - Create a runtime field for transaction amounts:
      - Small: $0-$50
      - Medium: $50-$200
      - Large: > $200

### Exercise 3.2: Aggregations and Bucket Analysis

1. **Peak Hours Analysis**
   - Use date histogram with hourly buckets
   - Find the busiest hours for web traffic
   - Identify peak shopping hours for e-commerce

1. **Error Rate Calculation**
   - Calculate percentage of HTTP errors (4xx, 5xx) vs total requests
   - Create a metric showing error rate trend over time

1. **Customer Lifetime Value**
   - Group by `customer_email`
   - Calculate total purchase amount per customer
   - Find top 10 customers by spending

### Exercise 3.3: Alerting and Monitoring

1. **High Error Rate Alert**
   - Create a watcher/alert for when error rate exceeds 5%
   - Trigger: HTTP status codes 4xx or 5xx

1. **System Resource Alert**
   - Alert when CPU usage > 90% for more than 5 minutes
   - Alert when memory usage > 85%

1. **Revenue Drop Alert**
   - Alert when hourly revenue drops below average by 30%

## Part 4: Dashboard Creation

### Exercise 4.1: Executive Dashboard

Create a comprehensive dashboard with:

1. **Key Performance Indicators (KPIs)**
   - Total requests (last 24h)
   - Average response time
   - Error rate percentage
   - Total revenue (last 24h)

1. **Traffic Overview**
   - Requests timeline (last 7 days)
   - Top 10 URLs by traffic
   - Geographic distribution

1. **System Health**
   - Average CPU/Memory usage by server
   - Response time percentiles (50th, 90th, 95th)

### Exercise 4.2: Operational Dashboard

1. **Real-time Monitoring**
   - Current system metrics (last 5 minutes)
   - Active alerts count
   - Recent error logs

1. **Performance Trends**
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
1. Saved searches for complex queries
1. Documentation of interesting findings
1. Export of your dashboard configurations

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
