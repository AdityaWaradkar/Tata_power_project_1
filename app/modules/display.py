import streamlit as st
import subprocess
import pandas as pd
import os
import shutil
import plotly.graph_objects as go

st.set_page_config(page_title="Loss Analyzer", layout="wide")

# Custom CSS for larger font size and cleaner look
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .css-18e3th9 {
            font-size: 24px !important;
        }
        .css-1lcbmhc {
            font-size: 20px !important;
        }
        .css-1v0mbdj {
            font-size: 18px !important;
        }
        .stButton>button {
            font-size: 18px;
        }
        .stTextInput>div>div>input {
            font-size: 16px;
        }
        .stSelectbox>div>div>div>div>input {
            font-size: 16px;
        }
        .stRadio>div>div>label {
            font-size: 16px;
        }
        .stSlider>div>div>div>div>input {
            font-size: 16px;
        }
        .stDataFrame {
            font-size: 16px !important;
        }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if "calculation_done" not in st.session_state:
        st.session_state.calculation_done = False
    if "analyzed_data" not in st.session_state:
        st.session_state.analyzed_data = None
    if "calculated_data" not in st.session_state:
        st.session_state.calculated_data = None

initialize_session_state()

st.title("Loss Analyzer")

# Upload section
with st.container():
    st.subheader("Upload Data")
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

        # Input values in a row
        col1, col2, col3 = st.columns(3)
        with col1:
            increment_value = st.number_input("Enter Increment Value (in MWh)", min_value=0, value=1, step=1)
        with col2:
            start_date = st.date_input("Select Start Date", value=pd.to_datetime("2023-01-01").date())
        with col3:
            end_date = st.date_input("Select End Date", value=pd.to_datetime("2023-12-31").date())

        # Center the button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button('Calculate Loss', use_container_width=True):
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

    # Format 'Day' column
    analyzed_data['Day'] = pd.to_datetime(analyzed_data['Day']).dt.strftime('%Y-%m-%d')

    # Calculate total losses
    total_loss_without_clipping = analyzed_data['Loss_Without_Clipping'].sum()
    total_loss_with_clipping = analyzed_data['Loss_With_Clipping'].sum()
    total_loss = total_loss_without_clipping - total_loss_with_clipping  # Calculated total loss

    # Display Total Loss in a single row with equal width columns
    st.markdown("## **Total Energy Loss Summary**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Loss", value=f"{total_loss:.2f} MWh")
    with col2:
        st.metric(label="Total Loss Without Clipping", value=f"{total_loss_without_clipping:.2f} MWh")
    with col3:
        st.metric(label="Total Loss With Clipping", value=f"{total_loss_with_clipping:.2f} MWh")


    # Add month selection
    analyzed_data['Month'] = pd.to_datetime(analyzed_data['Day']).dt.strftime('%B %Y')
    unique_months = analyzed_data['Month'].unique()

    col1, col2 = st.columns([2, 1])
    with col1:
        display_option = st.radio("Display Option:", ("Table", "Bar Graph", "Explicit Bar Graph"), horizontal=True)
    with col2:
        if len(unique_months) > 1:
            selected_month = st.selectbox("Select a Month:", unique_months)
            analyzed_data = analyzed_data[analyzed_data['Month'] == selected_month]

    # Show Data Table or Graph
    if display_option == "Table":
        # Highlight whole row where 'Loss_With_Clipping' is non-zero
        def highlight_row(row):
            return ['background-color: red; color: white' if row['Loss_With_Clipping'] != 0 else '' for _ in row]

        st.dataframe(
            analyzed_data.drop(columns=['Month']).style.apply(highlight_row, axis=1),
            use_container_width=True
        )
    elif display_option == "Bar Graph":
        analyzed_data['Loss_Difference'] = analyzed_data['Loss_Without_Clipping'] - analyzed_data['Loss_With_Clipping']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=analyzed_data['Day'],
            y=analyzed_data['Loss_Difference'],
            name='Total Loss',
            marker_color='yellow'
        ))
        fig.add_trace(go.Bar(
            x=analyzed_data['Day'],
            y=analyzed_data['Loss_Without_Clipping'],
            name='Loss Without Clipping',
            marker_color='cornflowerblue'
        ))
        fig.add_trace(go.Bar(
            x=analyzed_data['Day'],
            y=analyzed_data['Loss_With_Clipping'],
            name='Loss With Clipping',
            marker_color='lightcoral'
        ))

        fig.update_layout(
            barmode='group',
            title='Energy Loss Comparison (With and Without Clipping)',
            xaxis_title='Date',
            yaxis_title='Energy Loss (MWh)',
            xaxis=dict(
                tickangle=-45,  # Negative angle for opposite slant
                tickmode='array', 
                tickvals=analyzed_data['Day'], 
                ticktext=analyzed_data['Day']
            ),
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif display_option == "Explicit Bar Graph":
        # Filter data where Loss_With_Clipping is non-zero
        filtered_data = analyzed_data[analyzed_data['Loss_With_Clipping'] != 0]

        # If there is data to display
        if not filtered_data.empty:
            filtered_data['Loss_Difference'] = filtered_data['Loss_Without_Clipping'] - filtered_data['Loss_With_Clipping']

            fig_explicit = go.Figure()
            fig_explicit.add_trace(go.Bar(
                x=filtered_data['Day'],
                y=filtered_data['Loss_Difference'],
                name='Total Loss',
                marker_color='yellow'
            ))
            fig_explicit.add_trace(go.Bar(
                x=filtered_data['Day'],
                y=filtered_data['Loss_Without_Clipping'],
                name='Loss Without Clipping',
                marker_color='cornflowerblue'
            ))
            fig_explicit.add_trace(go.Bar(
                x=filtered_data['Day'],
                y=filtered_data['Loss_With_Clipping'],
                name='Loss With Clipping',
                marker_color='lightcoral'
            ))

            fig_explicit.update_layout(
                barmode='group',
                title='Explicit Energy Loss Comparison (With and Without Clipping) - Non-zero Loss_With_Clipping',
                xaxis_title='Date',
                yaxis_title='Energy Loss (MWh)',
                xaxis=dict(
                    tickangle=-45,  # Negative angle for opposite slant
                    tickmode='array', 
                    tickvals=filtered_data['Day'], 
                    ticktext=filtered_data['Day']
                ),
                template='plotly_white'
            )
            st.plotly_chart(fig_explicit, use_container_width=True)
        else:
            st.warning("No data available for the selected criteria (Loss_With_Clipping > 0).")

    # Select a specific day for detailed energy curve
    selected_day = st.selectbox("Select a Day for Energy Curve", analyzed_data['Day'])
    selected_day_calculated_data = calculated_data[calculated_data['Date'] == selected_day]

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=selected_day_calculated_data['Energy MWh'],
        mode='lines+markers',
        name='Energy MWh',
        line=dict(color='blue', width=3),  # Increased thickness
        marker=dict(size=6)
    ))
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=selected_day_calculated_data['incremented_energy MWh'],
        mode='lines+markers',
        name='Incremented Energy MWh',
        line=dict(color='green', width=3),  # Increased thickness
        marker=dict(size=6)
    ))
    fig_curve.add_trace(go.Scatter(
        x=selected_day_calculated_data['Time Interval'],
        y=[27.5] * len(selected_day_calculated_data),  # Red dotted line at 27.5 MWh
        mode='lines',
        name='Threshold (27.5 MWh)',
        line=dict(color='red', dash='dot', width=2)
    ))

    # Adding vertical lines for each x-axis point
    vertical_lines = []
    for x_value in selected_day_calculated_data['Time Interval']:
        vertical_lines.append(
            go.layout.Shape(
                type="line",
                x0=x_value,
                y0=0,
                x1=x_value,
                y1=max(selected_day_calculated_data['Energy MWh'].max(), selected_day_calculated_data['incremented_energy MWh'].max()),
                line=dict(color="gray", width=1, dash="dot")
            )
        )

    fig_curve.update_layout(
        title=f"Energy Curve for {selected_day}",
        xaxis_title='Time Interval',
        yaxis_title='Energy MWh',
        xaxis=dict(
            tickangle=-45,  # Negative angle for opposite slant in curve plot
            tickmode='array',
            tickvals=selected_day_calculated_data['Time Interval'],
            ticktext=selected_day_calculated_data['Time Interval']
        ),
        shapes=vertical_lines,  # Adding the vertical lines
        template='plotly_white'
    )
    st.plotly_chart(fig_curve, use_container_width=True)
