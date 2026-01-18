#!/bin/bash

echo "Starting Mock GPUaaS Server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python mock_gpuas_simulator.py
