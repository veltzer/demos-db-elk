# Logstash Setup and Data Flow Exercise

## Understanding Logstash

**Logstash** is a data processing pipeline that ingests data from multiple
sources, transforms it, and sends it to Elasticsearch. It's part of the ELK
Stack (Elasticsearch, Logstash, Kibana).

**Key Components:**

- **Input**: Where data comes from (files, databases, APIs, etc.)
- **Filter**: How data is processed and transformed
- **Output**: Where data goes (usually Elasticsearch)

---

## Exercise: Monitor System Logs with Logstash

In this exercise, we'll set up Logstash to read system log files and send them
to Elasticsearch, then view them in Kibana.

### Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601`
- Linux/macOS system (for log files)

### Step 1: Install Logstash

**Download and Install Logstash:**

See [`12_logstash_01.sh`](./12_logstash_01.sh)

**Alternative - Using Package Manager (Ubuntu/Debian):**

See [`12_logstash_02.sh`](./12_logstash_02.sh)

### Step 2: Verify Elasticsearch is Running

See [`12_logstash_03.sh`](./12_logstash_03.sh)

### Step 3: Create a Simple Logstash Configuration

Create a configuration file that will read log files and send them to
Elasticsearch:

See [`12_logstash_04.sh`](./12_logstash_04.sh)

### Step 4: Test the Configuration

See [`12_logstash_05.sh`](./12_logstash_05.sh)

### Step 5: Generate Some Log Data (Optional)

If your system doesn't have much log activity, generate some test data:

See [`12_logstash_06.sh`](./12_logstash_06.sh)

### Step 6: Run Logstash

**Start Logstash with our configuration:**

See [`12_logstash_07.sh`](./12_logstash_07.sh)

**Alternative - Run in Background:**

See [`12_logstash_08.sh`](./12_logstash_08.sh)

### Step 7: Verify Data in Elasticsearch

**Check if indices are being created:**

See [`12_logstash_09.sh`](./12_logstash_09.sh)

**Search for log data:**

See [`12_logstash_10.sh`](./12_logstash_10.sh)

**Search for specific log types:**

See [`12_logstash_11.sh`](./12_logstash_11.sh)

### Step 8: View Data in Kibana

1. **Open Kibana:** Go to `http://localhost:5601`

1. **Create Index Pattern:**
   - Go to "Stack Management" → "Index Patterns"
   - Click "Create index pattern"
   - Enter pattern: `system-logs-*`
   - Select `@timestamp` as time field
   - Click "Create index pattern"

1. **View Logs in Discover:**
   - Go to "Discover"
   - Select your `system-logs-*` index pattern
   - You should see your log entries flowing in real-time
   - Filter by `type:syslog` or `type:auth` to see different log types

1. **Create Simple Visualizations:**
   - Go to "Visualize Library"
   - Create a "Vertical Bar" chart
   - Show log count over time
   - Group by `type` field to see different log types

### Step 9: Add More Interesting Data

**Create a more complex configuration for web server logs:**

See [`12_logstash_12.sh`](./12_logstash_12.sh)

### Step 10: Monitor Multiple Pipelines

**Run multiple Logstash instances:**

See [`12_logstash_13.sh`](./12_logstash_13.sh)

### Step 11: Verify Data Flow

**Check data is flowing:**

See [`12_logstash_14.sh`](./12_logstash_14.sh)

### Expected Results

After completing this exercise, you should see:

1. **Logstash Processing:** Console output showing log entries being processed
1. **Elasticsearch Indices:** New daily indices being created
   (`system-logs-YYYY.MM.dd`)
1. **Kibana Visualization:** Real-time log data flowing into Kibana
1. **Structured Data:** Raw log lines parsed into structured fields

### Troubleshooting

**Common Issues:**

1. **Permission Denied on Log Files:**

   ```bash
   # Add user to appropriate groups
   sudo usermod -a -G adm $USER

   # Or run Logstash with appropriate permissions
   sudo /opt/logstash/bin/logstash -f simple-logs.conf
   ```

1. **Elasticsearch Connection Issues:**

   ```bash
   # Check Elasticsearch is running
   curl localhost:9200

   # Check Logstash logs for connection errors
   tail -f logstash.log
   ```

1. **No Log Files Found:**

   ```bash
   # Check log file paths exist
   ls -la /var/log/syslog
   ls -la /var/log/auth.log

   # Adjust paths in config file as needed
   ```

### Exercise Questions

1. How can you tell if Logstash is successfully sending data to Elasticsearch?
1. What happens if you stop Logstash and then restart it?
1. How would you modify the configuration to exclude certain types of log
   messages?
1. What's the difference between the `file` input and other input types?

### Clean Up

See [`12_logstash_15.sh`](./12_logstash_15.sh)

This exercise demonstrates the complete ELK pipeline: Logstash collecting and
processing data, Elasticsearch storing it, and Kibana visualizing it!
