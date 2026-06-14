# Logstash Setup and Data Flow Exercise

## Understanding Logstash

**Logstash** is a data processing pipeline that ingests data from multiple
sources, transforms it, and sends it to Elasticsearch. It's part of the ELK
Stack (Elasticsearch, Logstash, Kibana).

**Key Components:**

- **Input**: Where data comes from (files, databases, APIs, etc.)
- **Filter**: How data is processed and transformed
- **Output**: Where data goes (usually Elasticsearch)

These three stages form a *pipeline*: an event enters through an input,
flows through any filters, and leaves through an output. Each event is a
small structured document (a set of fields), so Logstash is really a tool
for turning raw, unstructured text (like a log line) into structured data
that Elasticsearch can index and search.

**Why use Logstash at all?** Elasticsearch stores and searches documents,
but it does not know how to read a `/var/log` file or split a messy log
line into fields. Logstash bridges that gap. The filter stage is where the
real value is added: a plain line such as
`Jun 14 10:42:01 host sshd[123]: failed login` becomes fields like
`timestamp`, `host`, `program`, `pid`, and `log_message`. Once data is
structured, you can filter, aggregate, and visualize it in Kibana.

---

## Exercise: Monitor System Logs with Logstash

In this exercise, we'll set up Logstash to read system log files and send them
to Elasticsearch, then view them in Kibana. This walks through the full ELK
loop end to end: Logstash collects and parses, Elasticsearch stores and
indexes, and Kibana lets you explore the result visually.

### Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601`
- Linux/macOS system (for log files)

### Step 1: Install Logstash

**Download and Install Logstash:**

See [`01_download_install_logstash.sh`](./01_download_install_logstash.sh)

**Alternative - Using Package Manager (Ubuntu/Debian):**

See [`02_install_logstash_apt.sh`](./02_install_logstash_apt.sh)

Logstash runs on the Java Virtual Machine and ships with its own bundled
Java, so you do not need to install Java separately. Keep the Logstash
version aligned with your Elasticsearch version: the same major version on
both sides avoids subtle compatibility problems when Logstash talks to the
Elasticsearch API.

### Step 2: Verify Elasticsearch is Running

See [`03_check_elasticsearch_health.sh`](./03_check_elasticsearch_health.sh)

**Why this matters:** Logstash's Elasticsearch output simply gives up and
buffers (or drops) events if it cannot reach the cluster. Confirming that
Elasticsearch answers on `localhost:9200` *before* starting the pipeline
saves you from chasing phantom problems later. A healthy cluster reports a
`green` or `yellow` status; a single-node setup is normally `yellow`
because replica shards have nowhere to go, and that is expected, not an
error.

### Step 3: Create a Simple Logstash Configuration

Create a configuration file that will read log files and send them to
Elasticsearch:

See [`04_create_syslog_config.sh`](./04_create_syslog_config.sh)

### Step 4: Test the Configuration

See [`05_test_config_syntax.sh`](./05_test_config_syntax.sh)

### Step 5: Generate Some Log Data (Optional)

If your system doesn't have much log activity, generate some test data:

See [`06_generate_test_logs.sh`](./06_generate_test_logs.sh)

### Step 6: Run Logstash

**Start Logstash with our configuration:**

See [`07_run_logstash_foreground.sh`](./07_run_logstash_foreground.sh)

**Alternative - Run in Background:**

See [`08_run_logstash_background.sh`](./08_run_logstash_background.sh)

### Step 7: Verify Data in Elasticsearch

**Check if indices are being created:**

See [`09_list_indices.sh`](./09_list_indices.sh)

**Search for log data:**

See [`10_search_recent_logs.sh`](./10_search_recent_logs.sh)

**Search for specific log types:**

See [`11_search_auth_logs.sh`](./11_search_auth_logs.sh)

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

See [`12_create_weblog_config.sh`](./12_create_weblog_config.sh)

### Step 10: Monitor Multiple Pipelines

**Run multiple Logstash instances:**

See [`13_run_multiple_pipelines.sh`](./13_run_multiple_pipelines.sh)

### Step 11: Verify Data Flow

**Check data is flowing:**

See [`14_monitor_data_flow.sh`](./14_monitor_data_flow.sh)

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

See [`15_cleanup_indices.sh`](./15_cleanup_indices.sh)

This exercise demonstrates the complete ELK pipeline: Logstash collecting and
processing data, Elasticsearch storing it, and Kibana visualizing it!
