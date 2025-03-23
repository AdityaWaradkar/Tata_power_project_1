#!/bin/bash

# Function to check if a Python package is installed
check_and_install() {
    package_name=$1
    if python3 -c "import $package_name" &> /dev/null; then
        echo "$package_name is already installed."
    else
        echo "$package_name is not installed. Installing..."
        pip install $package_name
    fi
}

echo "Checking required dependencies..."

# List of required packages
REQUIRED_PACKAGES=("streamlit" "pandas" "plotly" "numpy")

# Check and install each package
for package in "${REQUIRED_PACKAGES[@]}"; do
    check_and_install $package
done

echo "All dependencies are installed. Running the application..."

# Navigate to the target directory
cd app/modules || { echo "Directory not found!"; exit 1; }

# Run the Streamlit application
streamlit run display.py
