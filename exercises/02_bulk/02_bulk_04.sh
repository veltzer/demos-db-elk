#!/bin/bash
# Run full performance suite with visualizations
python run_performance_test.py

# Test with custom sizes
python run_performance_test.py --test-sizes 1000 5000 10000 25000
