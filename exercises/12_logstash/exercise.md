# Logstash Setup and Data Flow Exercise

## Understanding Logstash

**Logstash** is a data processing pipeline that ingests data from multiple sources, transforms it, and sends it to Elasticsearch. It's part of the ELK Stack (Elasticsearch, Logstash, Kibana).

**Key Components:**
- **Input**: Where data comes from (files, databases, APIs, etc.)
- **Filter**: How data is processed and transformed
- **Output**: Where data goes (usually Elasticsearch)

---

## Exercise: Monitor System Logs with Logstash

In this exercise, we'll set up Logstash to read system log files and send them to Elasticsearch, then view them in Kibana.

### Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601`
- Linux/macOS system (for log files)

### Step 1: Install Logstash

**Download and Install Logstash:**

```bash
# Download Logstash (adjust version as needed)
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.11.0-linux-x86_64.tar.gz

# Extract
tar -xzf logstash-8.11.0-linux-x86_64.tar.gz

# Move to a convenient location
sudo mv logstash-8.11.0 /opt/logstash

# Create symlink for easier access
sudo ln -s /opt/logstash/bin/logstash /usr/local/bin/logstash
```

**Alternative - Using Package Manager (Ubuntu/Debian):**
```bash
# Add Elastic repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# Install
sudo apt update
sudo apt install logstash
```

### Step 2: Verify Elasticsearch is Running

```bash
# Check Elasticsearch status
curl -X GET "localhost:9200/_cluster/health?pretty"

# Should return cluster status
```

### Step 3: Create a Simple Logstash Configuration

Create a configuration file that will read log files and send them to Elasticsearch:

```bash
# Create config directory
mkdir -p ~/logstash-exercise
cd ~/logstash-exercise

# Create the configuration file
cat > simple-logs.conf << 'EOF'
input {
  file {
    path => "/var/log/syslog"
    start_position => "beginning"
    type => "syslog"
  }
  
  file {
    path => "/var/log/auth.log"
    start_position => "beginning"
    type => "auth"
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:timestamp} %{IPORHOST:host} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:log_message}" }
    }
    
    date {
      match => [ "timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }
  }
  
  if [type] == "auth" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:timestamp} %{IPORHOST:host} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:log_message}" }
    }
    
    date {
      match => [ "timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }
  }
  
  # Add hostname field
  mutate {
    add_field => { "hostname" => "%{host}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "system-logs-%{+YYYY.MM.dd}"
  }
  
  # Also output to console for debugging
  stdout {
    codec => rubydebug
  }
}
EOF
```

### Step 4: Test the Configuration

```bash
# Test the configuration syntax
/opt/logstash/bin/logstash --config.test_and_exit -f simple-logs.conf

# Should output "Configuration OK"
```

### Step 5: Generate Some Log Data (Optional)

If your system doesn't have much log activity, generate some test data:

```bash
# Generate some syslog entries
logger "Test message from logstash exercise - $(date)"
logger "Another test message with some data: user=testuser action=login"
logger "Error simulation: failed to connect to database"

# Generate auth log entries (if you have sudo access)
sudo logger -t sshd "Test auth message: authentication failure"
```

### Step 6: Run Logstash

**Start Logstash with our configuration:**

```bash
# Run Logstash (this will run in foreground)
/opt/logstash/bin/logstash -f simple-logs.conf

# You should see:
# - Logstash starting up
# - Pipeline being created
# - Log entries being processed (in console output)
# - Data being sent to Elasticsearch
```

**Alternative - Run in Background:**
```bash
# Run in background
nohup /opt/logstash/bin/logstash -f simple-logs.conf > logstash.log 2>&1 &

# Check if it's running
ps aux | grep logstash

# View logs
tail -f logstash.log
```

### Step 7: Verify Data in Elasticsearch

**Check if indices are being created:**
```bash
# List indices
curl -X GET "localhost:9200/_cat/indices?v&pretty"

# Should see indices like: system-logs-2024.01.XX
```

**Search for log data:**
```bash
# Get some log entries
curl -X GET "localhost:9200/system-logs-*/_search?pretty&size=5" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  },
  "sort": [
    { "@timestamp": { "order": "desc" } }
  ]
}'
```

**Search for specific log types:**
```bash
# Search for auth logs
curl -X GET "localhost:9200/system-logs-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "type": "auth"
    }
  }
}'
```

### Step 8: View Data in Kibana

1. **Open Kibana:** Go to `http://localhost:5601`

2. **Create Index Pattern:**
   - Go to "Stack Management" → "Index Patterns"
   - Click "Create index pattern"
   - Enter pattern: `system-logs-*`
   - Select `@timestamp` as time field
   - Click "Create index pattern"

3. **View Logs in Discover:**
   - Go to "Discover"
   - Select your `system-logs-*` index pattern
   - You should see your log entries flowing in real-time
   - Filter by `type:syslog` or `type:auth` to see different log types

4. **Create Simple Visualizations:**
   - Go to "Visualize Library"
   - Create a "Vertical Bar" chart
   - Show log count over time
   - Group by `type` field to see different log types

### Step 9: Add More Interesting Data

**Create a more complex configuration for web server logs:**

```bash
# If you have nginx/apache logs, create another config
cat > web-logs.conf << 'EOF'
input {
  file {
    path => "/var/log/nginx/access.log"
    start_position => "beginning"
    type => "nginx_access"
  }
  
  file {
    path => "/var/log/apache2/access.log"
    start_position => "beginning"
    type => "apache_access"
  }
}

filter {
  if [type] == "nginx_access" {
    grok {
      match => { "message" => "%{NGINXACCESS}" }
    }
  }
  
  if [type] == "apache_access" {
    grok {
      match => { "message" => "%{COMMONAPACHELOG}" }
    }
  }
  
  # Parse timestamp
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  }
  
  # Convert response code to number
  mutate {
    convert => { "response" => "integer" }
    convert => { "bytes" => "integer" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "web-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
EOF
```

### Step 10: Monitor Multiple Pipelines

**Run multiple Logstash instances:**
```bash
# Terminal 1: System logs
/opt/logstash/bin/logstash -f simple-logs.conf

# Terminal 2: Web logs (if available)
/opt/logstash/bin/logstash -f web-logs.conf
```

### Step 11: Verify Data Flow

**Check data is flowing:**
```bash
# Monitor index growth
watch -n 5 'curl -s "localhost:9200/_cat/indices?v" | grep system-logs'

# Count documents
curl -X GET "localhost:9200/system-logs-*/_count?pretty"

# Get latest entries
curl -X GET "localhost:9200/system-logs-*/_search?pretty&size=1" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "sort": [{ "@timestamp": { "order": "desc" }}]
}'
```

### Expected Results

After completing this exercise, you should see:

1. **Logstash Processing:** Console output showing log entries being processed
2. **Elasticsearch Indices:** New daily indices being created (`system-logs-YYYY.MM.dd`)
3. **Kibana Visualization:** Real-time log data flowing into Kibana
4. **Structured Data:** Raw log lines parsed into structured fields

### Troubleshooting

**Common Issues:**

1. **Permission Denied on Log Files:**
   ```bash
   # Add user to appropriate groups
   sudo usermod -a -G adm $USER
   
   # Or run Logstash with appropriate permissions
   sudo /opt/logstash/bin/logstash -f simple-logs.conf
   ```

2. **Elasticsearch Connection Issues:**
   ```bash
   # Check Elasticsearch is running
   curl localhost:9200
   
   # Check Logstash logs for connection errors
   tail -f logstash.log
   ```

3. **No Log Files Found:**
   ```bash
   # Check log file paths exist
   ls -la /var/log/syslog
   ls -la /var/log/auth.log
   
   # Adjust paths in config file as needed
   ```

### Exercise Questions

1. How can you tell if Logstash is successfully sending data to Elasticsearch?
2. What happens if you stop Logstash and then restart it?
3. How would you modify the configuration to exclude certain types of log messages?
4. What's the difference between the `file` input and other input types?

### Clean Up

```bash
# Stop Logstash (Ctrl+C if running in foreground)
# Or kill background process:
pkill -f logstash

# Remove test indices
curl -X DELETE "localhost:9200/system-logs-*"
curl -X DELETE "localhost:9200/web-logs-*"
```

This exercise demonstrates the complete ELK pipeline: Logstash collecting and processing data, Elasticsearch storing it, and Kibana visualizing it!
