import pandas as pd
import os
import argparse

# Function to add incremented energy
def add_incremented_energy(df, increment_value):
    df['incremented_energy MWh'] = ((140 + increment_value) * df['Energy MWh']) / 140
    return df

# Function to save calculated data
def save_calculated_data(df, file_name='calculated_data.csv'):
    column_order = ['Date', 'Time Interval', 'Power MW', 'Energy MWh', 'incremented_energy MWh']
    df = df[column_order]
    
    # Get the absolute path to the 'assets' folder (relative path)
    assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
    
    # Ensure the folder exists
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    
    file_path = os.path.join(assets_folder, file_name)
    
    # Save the dataframe as a CSV file
    df.to_csv(file_path, index=False)

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Energy loss calculation")
    parser.add_argument('--increment_value', type=int, required=True, help="Increment value in MWh")
    parser.add_argument('--start_date', type=str, required=True, help="Start date in format dd-mm-yyyy")
    parser.add_argument('--end_date', type=str, required=True, help="End date in format dd-mm-yyyy")
    
    args = parser.parse_args()

    try:
        increment_value = args.increment_value
        start_date = args.start_date
        end_date = args.end_date

        # Load the cleaned data from the correct path
        assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
        file_path = os.path.join(assets_folder, 'cleaned_data.csv')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("CSV file 'cleaned_data.csv' not found in the assets folder. Run 'cleaning.py' first.")

        df = pd.read_csv(file_path)
        
        # Filter the data based on the date range (start_date and end_date)
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        mask = (df['Date'] >= pd.to_datetime(start_date, format='%d-%m-%Y')) & (df['Date'] <= pd.to_datetime(end_date, format='%d-%m-%Y'))
        filtered_df = df[mask]

        # Perform calculation to add the incremented energy column
        calculated_df = add_incremented_energy(filtered_df, increment_value)
        
        # Save the final dataframe
        save_calculated_data(calculated_df)

        print("Calculated DataFrame:")
        print(calculated_df.head())
        print(f"\nCalculated data saved to '{os.path.join(assets_folder, 'calculated_data.csv')}'!")

    except Exception as e:
        print(f"An error occurred: {e}")
