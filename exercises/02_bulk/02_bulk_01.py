#!/usr/bin/env python
# 1. Create index with bulk-optimized settings
PUT /products
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 0,
    "refresh_interval": "-1"
  }
}

# 2. Perform bulk insert
# ... bulk insert operations ...

# 3. Re-enable normal settings after loading
PUT /products/_settings
{
  "number_of_replicas": 1,
  "refresh_interval": "1s"
}
