#!/bin/bash

echo "================================================"
echo "Elasticsearch Bulk Insert Exercise Test"
echo "================================================"

# Configuration
ES_HOST="localhost"
ES_PORT="9200"
ES_USER="elastic"
ES_PASSWORD="changeme"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "\n${YELLOW}Step 1: Checking Elasticsearch connection...${NC}"
curl -s -X GET "http://${ES_HOST}:${ES_PORT}" -u ${ES_USER}:${ES_PASSWORD} > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Elasticsearch is running${NC}"
else
    echo -e "${RED}✗ Cannot connect to Elasticsearch${NC}"
    echo "Please ensure Elasticsearch is running and accessible"
    exit 1
fi

echo -e "\n${YELLOW}Step 2: Generating test data...${NC}"
python generate_data.py --products 1000 --customers 500 --orders 2000 --format ndjson
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test data generated successfully${NC}"
else
    echo -e "${RED}✗ Failed to generate test data${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 3: Running bulk insert comparison test...${NC}"
python bulk_insert.py \
    --host ${ES_HOST} \
    --port ${ES_PORT} \
    --user ${ES_USER} \
    --password ${ES_PASSWORD} \
    --data-file ./data/products.ndjson \
    --test-type compare

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Bulk insert test completed${NC}"
else
    echo -e "${RED}✗ Bulk insert test failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 4: Running comprehensive performance test...${NC}"
python run_performance_test.py \
    --host ${ES_HOST} \
    --port ${ES_PORT} \
    --user ${ES_USER} \
    --password ${ES_PASSWORD} \
    --data-file ./data/products.ndjson \
    --test-sizes 500 1000 \
    --output-dir ./results

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Performance test completed${NC}"
else
    echo -e "${RED}✗ Performance test failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 5: Displaying results...${NC}"
if [ -f ./results/performance_report.txt ]; then
    echo -e "${GREEN}Performance Report Summary:${NC}"
    tail -n 20 ./results/performance_report.txt
else
    echo -e "${RED}✗ Performance report not found${NC}"
fi

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Exercise completed successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Results have been saved to:"
echo "  - ./results/performance_report.txt    (detailed report)"
echo "  - ./results/performance_analysis.png   (visualization)"
echo "  - ./results/raw_results.json          (raw data)"
echo ""
echo "To view the full report, run:"
echo "  cat ./results/performance_report.txt"
echo ""