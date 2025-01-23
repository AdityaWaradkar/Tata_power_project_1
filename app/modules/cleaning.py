import pandas as pd
import os

def split_date_time(df):
    # Splitting the 'Time' column into 'Date' and 'Time Interval'
    df[['Date', 'Time Interval']] = df['Time'].str.split(' ', n=1, expand=True)
    return df.drop(columns=['Time'])

def clean_dataframe(df):
    # Dropping rows with missing values
    df = df.dropna()
    
    # Filter out negative power values, if present
    if "Power MW" in df.columns:
        df = df[df["Power MW"] >= 0]
    
    # Add the 'Energy MWh' column, calculating it based on 'Power MW'
    df['Energy MWh'] = df['Power MW'] * 0.25  
    return df

def save_cleaned_data(df, file_name='cleaned_data.csv'):
    # Reorder columns before saving the cleaned data
    column_order = ['Date', 'Time Interval', 'Power MW', 'Energy MWh']
    df = df[column_order]
    
    # Get the absolute path to the assets folder (relative path)
    assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
    
    # Ensure the folder exists
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)

    file_path = os.path.join(assets_folder, file_name)
    
    # Save the dataframe to a CSV file
    df.to_csv(file_path, index=False)

if __name__ == "__main__":
    try:
        # Get the absolute path to the assets folder, relative path to 'assets'
        assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets'))
        
        # Check if the 'data.csv' file exists in the assets folder
        file_path = os.path.join(assets_folder, 'data.csv')
        if not os.path.exists(file_path):
            raise FileNotFoundError("CSV file 'data.csv' not found in the assets folder. Run 'excel_to_df.py' first.")
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Split the 'Time' column into 'Date' and 'Time Interval'
        df = split_date_time(df)
        
        # Clean the DataFrame by dropping NaNs and applying other filters
        cleaned_df = clean_dataframe(df)
        
        # Save the cleaned data to the 'assets/cleaned_data.csv' file
        save_cleaned_data(cleaned_df)
        
        print("Cleaned DataFrame:")
        print(cleaned_df.head())
        print("\nCleaned data saved to 'assets/cleaned_data.csv'!")
    
    except Exception as e:
        print(f"An error occurred: {e}")
