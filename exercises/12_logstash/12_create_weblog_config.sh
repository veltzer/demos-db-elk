#!/bin/bash -eu
# Use the same config directory as 04_create_syslog_config.sh
mkdir -p ~/logstash-exercise
cd ~/logstash-exercise

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
