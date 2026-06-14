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

**What's happening in this config:** The `file` input tails `/var/log`
files much like `tail -f`. The `start_position => "beginning"` setting
tells Logstash to read the file from the top the first time it sees it
(otherwise it would only pick up lines added after it starts). The `type`
field tags each event so the filters can treat syslog and auth events
differently.

The `grok` filter is the heart of the parsing. Grok matches a line against
named patterns (such as `%{SYSLOGTIMESTAMP:timestamp}` or
`%{IPORHOST:host}`) and captures each match into a field. Think of it as
regular expressions with a library of reusable, human-readable building
blocks. The `date` filter then takes the captured `timestamp` text and
parses it into `@timestamp`, the special time field Elasticsearch and
Kibana use to place each event on a time line. Without it, every event
would be stamped with the moment Logstash read the line, not when the event
actually occurred. Finally the `mutate` filter copies `host` into a
`hostname` field, showing how you can reshape events after parsing.

The output sends events to Elasticsearch and *also* prints them to the
console with the `rubydebug` codec. That console echo is invaluable while
learning: you can see exactly what fields each event ended up with.

### Step 4: Test the Configuration

See [`05_test_config_syntax.sh`](./05_test_config_syntax.sh)

**Why this matters:** `--config.test_and_exit` parses the configuration and
reports `Configuration OK` without actually starting the pipeline. Catching
a typo or an unbalanced brace here is far cheaper than discovering it after
Logstash has spun up its full pipeline. Note that this only checks syntax,
not whether your grok patterns will actually match real log lines.

### Step 5: Generate Some Log Data (Optional)

If your system doesn't have much log activity, generate some test data:

See [`06_generate_test_logs.sh`](./06_generate_test_logs.sh)

The `logger` command writes a line into the system log through the standard
syslog facility, which is exactly what Logstash is watching. This gives you
a controlled way to produce events on demand so you can confirm the
pipeline end to end instead of waiting for the system to log something on
its own.

### Step 6: Run Logstash

**Start Logstash with our configuration:**

See [`07_run_logstash_foreground.sh`](./07_run_logstash_foreground.sh)

Running in the foreground is the right choice while you are learning,
because the `rubydebug` console output streams past in real time and you can
watch events being parsed. Logstash takes several seconds to start: it boots
the JVM, compiles the pipeline, and only then begins reading. Be patient and
wait for the "Pipeline started" message before expecting any output.

**Alternative - Run in Background:**

See [`08_run_logstash_background.sh`](./08_run_logstash_background.sh)

`nohup ... &` detaches Logstash from your terminal so it keeps running after
you log out, redirecting its output to a log file you can `tail`. This is
closer to how Logstash runs in production (usually as a managed service),
but in the background you lose the live console feed, so you watch the log
file instead.

**Where does Logstash remember its place?** Each `file` input keeps a
"sincedb" record of how far it has read in every file. That is why
restarting Logstash does *not* re-send everything from the beginning: it
resumes where it left off. This is also why deleting the sincedb (or pointing
at a fresh file) makes `start_position => "beginning"` take effect again.

### Step 7: Verify Data in Elasticsearch

**Check if indices are being created:**

See [`09_list_indices.sh`](./09_list_indices.sh)

**What to look for:** The first time an event arrives with a new daily
index name (`system-logs-YYYY.MM.dd`), Elasticsearch creates that index
automatically and infers a mapping (the data type of each field) from the
first documents it sees. Seeing the index appear is the clearest sign that
data is actually landing, not just being read by Logstash.

**Search for log data:**

See [`10_search_recent_logs.sh`](./10_search_recent_logs.sh)

This query asks Elasticsearch to return the most recent documents by
sorting on `@timestamp` in descending order. Because that field was set by
the `date` filter, the newest *events* come first rather than the most
recently *indexed* documents, which is what you usually want for logs.

**Search for specific log types:**

See [`11_search_auth_logs.sh`](./11_search_auth_logs.sh)

This is where the `type` tag pays off: a single field lets you carve out
just the authentication events from everything else flowing through the
same pipeline and indices.

### Step 8: View Data in Kibana

Kibana never stores data of its own; it is a window onto Elasticsearch. To
show you anything, it first needs to know *which* indices to read, which is
the job of the index pattern below.

1. **Open Kibana:** Go to `http://localhost:5601`

1. **Create Index Pattern:**
   - Go to "Stack Management" → "Index Patterns"
   - Click "Create index pattern"
   - Enter pattern: `system-logs-*`
   - Select `@timestamp` as time field
   - Click "Create index pattern"

   The trailing `*` is what lets one pattern span every daily index at
   once, so you never have to recreate it as new days roll over. Choosing
   `@timestamp` as the time field is what powers Kibana's time picker and
   the time-based histograms in Discover.

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

**Why this is interesting:** Web access logs follow well-known formats, so
Logstash ships ready-made grok patterns for them: `%{COMMONAPACHELOG}` and
`%{NGINXACCESS}` unpack a request line into fields like client IP, request
path, response code, and bytes sent in one step. Notice the extra `mutate`
that converts `response` and `bytes` to integers. By default every grok
capture is a string, and Elasticsearch would map them as text. Converting
them to numbers lets you do numeric work later, such as averaging response
sizes or counting how many `500` errors occurred. This config writes to its
own `web-logs-*` indices, keeping web traffic separate from system logs.

### Step 10: Monitor Multiple Pipelines

**Run multiple Logstash instances:**

See [`13_run_multiple_pipelines.sh`](./13_run_multiple_pipelines.sh)

Here each config runs as a separate Logstash process in its own terminal,
which is the simplest way to keep two unrelated data flows isolated. In a
real deployment you would more often run a single Logstash with the
`pipelines.yml` file defining several named pipelines inside one process,
which shares the JVM and uses less memory. Running separate processes is
fine for learning and makes it obvious which pipeline produced which output.

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
