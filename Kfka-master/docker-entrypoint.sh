#!/bin/bash

echo "Starting Yumeko Bot..."

# Check if a main module for Yumeko exists and run it.
# Replace 'Yumeko' with the correct main module if it's different.
if [ -d "Yumeko" ]; then
    python3 -m Yumeko &
fi

echo "Starting Yumeko Music Bot..."
# This will keep the container running
python3 -m Yumeko_Music