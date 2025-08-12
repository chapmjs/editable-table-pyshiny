from shiny import App, ui, render, reactive
from shiny.types import ImgData
import pandas as pd
from shinywidgets import output_widget, render_widget
import ipywidgets as widgets
from IPython.display import display
import numpy as np

# Create sample data
sample_data = pd.DataFrame({
    'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince'],
    'Age': [25, 30, 35, 28],
    'Department': ['Engineering', 'Marketing', 'Sales', 'HR'],
    'Salary': [75000, 65000, 70000, 60000],
    'Active': [True, True, False, True]
})

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Editable Data Table Example"),
    ui.p("Double-click any cell to edit its value. Changes will be reflected in real-time."),
    
    # Display the editable table
    ui.div(
        ui.h4("Employee Data"),
        ui.output_data_frame("editable_table"),
        style="margin: 20px;"
    ),
    
    # Show current data state
    ui.div(
        ui.h4("Current Data State"),
        ui.output_text_verbatim("data_state"),
        style="margin: 20px; background-color: #f8f9fa; padding: 15px; border-radius: 5px;"
    ),
    
    # Action buttons
    ui.div(
        ui.input_action_button("reset_data", "Reset Data", class_="btn-warning"),
        ui.input_action_button("add_row", "Add Row", class_="btn-success"),
        style="margin: 20px;"
    )
)

def server(input, output, session):
    # Reactive value to store the dataframe
    data = reactive.Value(sample_data.copy())
    
    @output
    @render.data_frame
    def editable_table():
        return render.DataGrid(
            data.get(),
            editable=True,  # Enable editing
            filters=True,   # Add column filters
            summary=True    # Show summary row
        )
    
    @output
    @render.text
    def data_state():
        df = data.get()
        return f"Current data shape: {df.shape}\n\nData preview:\n{df.to_string()}"
    
    # Handle data editing
    @reactive.Effect
    @reactive.event(input.editable_table_cell_edit)
    def handle_edit():
        edit_info = input.editable_table_cell_edit()
        if edit_info is not None:
            # Get current data
            current_data = data.get().copy()
            
            # Update the specific cell
            row_idx = edit_info['row_index']
            col_name = edit_info['column_name'] 
            new_value = edit_info['value']
            
            # Handle type conversion based on column
            if col_name in ['Age', 'Salary']:
                try:
                    new_value = int(new_value) if col_name == 'Age' else float(new_value)
                except ValueError:
                    return  # Invalid input, ignore
            elif col_name == 'Active':
                new_value = str(new_value).lower() in ['true', '1', 'yes', 'on']
            
            # Update the dataframe
            current_data.iloc[row_idx, current_data.columns.get_loc(col_name)] = new_value
            data.set(current_data)
    
    # Reset data button
    @reactive.Effect
    @reactive.event(input.reset_data)
    def reset_data():
        data.set(sample_data.copy())
    
    # Add new row button
    @reactive.Effect
    @reactive.event(input.add_row)
    def add_row():
        current_data = data.get().copy()
        new_row = pd.DataFrame({
            'Name': ['New Employee'],
            'Age': [25],
            'Department': ['TBD'],
            'Salary': [50000],
            'Active': [True]
        })
        updated_data = pd.concat([current_data, new_row], ignore_index=True)
        data.set(updated_data)

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
