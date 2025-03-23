#!/bin/bash

# Navigate to the target directory
cd app/modules || { echo "Directory not found!"; exit 1; }

# Run the Streamlit application
streamlit run display.py
