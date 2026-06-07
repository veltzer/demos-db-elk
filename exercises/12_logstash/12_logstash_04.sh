#!/bin/bash
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
