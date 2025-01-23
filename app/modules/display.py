import streamlit as st
import subprocess
import pandas as pd
import os
import shutil
import plotly.graph_objects as go

# Enable wide layout and set a custom title for the browser tab
st.set_page_config(page_title="Loss Analyser", layout="wide")

def initialize_session_state():
    if "calculation_done" not in st.session_state:
        st.session_state.calculation_done = False
    if "analyzed_data" not in st.session_state:
        st.session_state.analyzed_data = None
    if "calculated_data" not in st.session_state:
        st.session_state.calculated_data = None

initialize_session_state()

uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        assets_folder = os.path.abspath(os.path.join(os.getcwd(), '../../assets/'))
        
        if os.path.exists(assets_folder):
            shutil.rmtree(assets_folder)
        os.makedirs(assets_folder)

        temp_excel_path = os.path.join(assets_folder, 'project_1_data.xlsx')
        with open(temp_excel_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        from excel_to_csv import convert_excel_to_csv
        csv_file_name = 'data.csv'

        convert_excel_to_csv(uploaded_file, csv_file_name)

        subprocess.run(['python', 'cleaning.py'], check=True)

        increment_value = st.number_input("Enter Increment Value (in MWh):", min_value=0, value=1, step=1)
        start_date = st.date_input("Select Start Date:", value=pd.to_datetime("2023-01-01").date())
        end_date = st.date_input("Select End Date:", value=pd.to_datetime("2023-12-31").date())

        if st.button('Calculate Loss'):
            try:
                subprocess.run(['python', 'calculations.py', 
                                '--increment_value', str(increment_value),
                                '--start_date', start_date.strftime("%d-%m-%Y"),
                                '--end_date', end_date.strftime("%d-%m-%Y")], check=True)

                subprocess.run(['python', 'analysis.py'], check=True)

                results_file_path = os.path.join(assets_folder, 'analysed_data.csv')
                st.session_state.analyzed_data = pd.read_csv(results_file_path)

                calculated_data_path = os.path.join(assets_folder, 'calculated_data.csv')
                st.session_state.calculated_data = pd.read_csv(calculated_data_path)

                st.session_state.calculation_done = True

            except Exception as e:
                st.error(f"An error occurred during the calculations or analysis: {e}")

    except Exception as e:
        st.error(f"An error occurred while processing the Excel file: {e}")


if st.session_state.calculation_done:
    analyzed_data = st.session_state.analyzed_data
    calculated_data = st.session_state.calculated_data

    # Format the 'Day' column to remove time part
    analyzed_data['Day'] = pd.to_datetime(analyzed_data['Day']).dt.strftime('%Y-%m-%d')

    # Add toggle for switching between table and bar graph
    display_option = st.radio(
        "Select display option:",
        ("Table", "Bar Graph"),
        index=0  # Default to "Table"
    )

    # Extract months from the date range if it spans more than one month
    analyzed_data['Month'] = pd.to_datetime(analyzed_data['Day']).dt.strftime('%B %Y')
    unique_months = analyzed_data['Month'].unique()

    selected_month = None
    if len(unique_months) > 1:
        selected_month = st.selectbox("Select a Month:", unique_months)

    # Filter data based on selected month
    if selected_month:
        analyzed_data = analyzed_data[analyzed_data['Month'] == selected_month]

    if display_option == "Table":
        st.subheader("Analyzed Data Overview")
        st.dataframe(analyzed_data.drop(columns=['Month']), use_container_width=True)  # Full-width dataframe
    elif display_option == "Bar Graph":
        # Generate bar graph
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=analyzed_data['Day'],
            y=analyzed_data['Loss_Without_Clipping'],
            name='Loss Without Clipping',
            marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            x=analyzed_data['Day'],
            y=analyzed_data['Loss_With_Clipping'],
            name='Loss With Clipping',
            marker_color='red'
        ))

        # Update layout to show all dates on x-axis
        fig.update_layout(
            barmode='group',
            title='Energy Loss Comparison (With and Without Clipping)',
            xaxis_title='Date',
            yaxis_title='Energy Loss (MWh)',
            xaxis=dict(
                tickmode='array',
                tickvals=analyzed_data['Day'],  # Use every date as a tick
                ticktext=analyzed_data['Day'],  # Use formatted dates for labels
                tickangle=45  # Tilt labels for readability
            ),
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)  # Full-width plot

    selected_day = st.selectbox("Select a Day for Detailed Energy Curve", analyzed_data['Day'])

    # Filter and create a detailed energy curve for the selected day
    selected_day_calculated_data = calculated_data[calculated_data['Date'] == selected_day]

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=selected_day_calculated_data['Energy MWh'],
        mode='lines',
        name='Energy MWh',
        line=dict(color='blue')
    ))
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=selected_day_calculated_data['incremented_energy MWh'],
        mode='lines',
        name='Incremented Energy MWh',
        line=dict(color='green')
    ))
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=[27.5] * len(selected_day_calculated_data),
        mode='lines',
        name='Clipping Line',
        line=dict(color='red', dash='dash')
    ))

    fig_curve.update_layout(
        title=f"Energy Curve for {selected_day}",
        xaxis_title='Time Interval',
        yaxis_title='Energy MWh',
        xaxis=dict(tickangle=45),
        template='plotly_dark'
    )
    st.plotly_chart(fig_curve, use_container_width=True)  # Full-width plot
