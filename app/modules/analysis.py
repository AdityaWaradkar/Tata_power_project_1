import pandas as pd
import numpy as np
import os

def calculate_daily_losses(df, clipping_line=27.5):
    # Ensure 'Date' column is treated as string before splitting
    try:
        print("Processing 'Date' column...")
        df['Date'] = df['Date'].astype(str).str.split(' ').str[0]  # Extract date part as string
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        print("Successfully processed 'Date' column.")
    except Exception as e:
        print(f"Error processing 'Date' column: {e}")
        return None
    
    # Extract only the date part for grouping
    print("Extracting 'Day' from 'Date' column...")
    df['Day'] = df['Date'].dt.date  # Assign the date part to a new column
    
    # Strip whitespace from column names to avoid issues with extra spaces
    df.columns = df.columns.str.strip()

    # Check if the necessary columns exist
    required_columns = ['incremented_energy MWh', 'Energy MWh']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return None

    # Calculate Losses for each row
    print("Calculating losses for each row...")
    df['Loss Without Clipping'] = (df['incremented_energy MWh'] - df['Energy MWh'])
    df['Loss With Clipping'] = np.maximum(df['incremented_energy MWh'] - clipping_line, 0)
    df['Loss Difference'] = df['Loss Without Clipping'] - df['Loss With Clipping']
    
    # Group by day and calculate total losses for the day
    print("Aggregating daily losses...")
    daily_losses = df.groupby('Day').agg(
        Loss_Without_Clipping=('Loss Without Clipping', 'sum'),
        Loss_With_Clipping=('Loss With Clipping', 'sum'),
        Loss_Difference=('Loss Difference', 'sum')
    ).reset_index()

    print("Daily losses calculated successfully.")
    
    return daily_losses

# Load the calculated data from 'calculated_data.csv'
try:
    # Get the absolute path to the 'assets' folder
    assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
    file_path = os.path.join(assets_folder, 'calculated_data.csv')
    
    df_calculated = pd.read_csv(file_path)
    print("Data loaded successfully from 'calculated_data.csv'.")
except Exception as e:
    print(f"Error loading data: {e}")
    df_calculated = None

# If the data was loaded successfully, calculate daily losses
if df_calculated is not None:
    results = calculate_daily_losses(df_calculated)

    if results is not None:
        print("\nFinal Results:")
        print(results)
        # Save the results to 'analysed_data.csv' inside the assets folder
        results_file_path = os.path.join(assets_folder, 'analysed_data.csv')
        results.to_csv(results_file_path, index=False)
        print(f"Results saved to '{results_file_path}'")
