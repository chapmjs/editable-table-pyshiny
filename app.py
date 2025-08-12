from shiny import App, ui, render, reactive
import pandas as pd

# Simple sample data
data_dict = {
    'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'Price': [999.99, 25.50, 75.00, 299.99],
    'Quantity': [10, 50, 25, 15],
    'In_Stock': [True, True, False, True]
}

app_ui = ui.page_fluid(
    ui.h1("Simple Editable Table"),
    ui.p("Click on any cell to select it, then use the input fields below to edit values."),
    
    # Table display
    ui.output_table("data_table"),
    
    ui.hr(),
    
    # Edit controls
    ui.row(
        ui.column(3,
            ui.input_selectize("row_select", "Select Row:", choices=[]),
        ),
        ui.column(3,
            ui.input_selectize("col_select", "Select Column:", choices=[]),
        ),
        ui.column(4,
            ui.input_text("new_value", "New Value:", value=""),
        ),
        ui.column(2,
            ui.input_action_button("update_cell", "Update Cell", class_="btn-primary"),
        )
    ),
    
    ui.hr(),
    
    # Show raw data
    ui.h4("Current Data:"),
    ui.output_text_verbatim("raw_data")
)

def server(input, output, session):
    # Store data in reactive value
    table_data = reactive.Value(pd.DataFrame(data_dict))
    
    @reactive.Effect
    def update_choices():
        df = table_data.get()
        # Update row choices
        ui.update_selectize("row_select", 
            choices={str(i): f"Row {i+1}: {df.iloc[i, 0]}" for i in range(len(df))}
        )
        # Update column choices  
        ui.update_selectize("col_select", choices=list(df.columns))
    
    @output
    @render.table
    def data_table():
        df = table_data.get()
        # Add row numbers for easier identification
        display_df = df.copy()
        display_df.index = [f"Row {i+1}" for i in range(len(df))]
        return display_df
    
    @output
    @render.text
    def raw_data():
        return table_data.get().to_string()
    
    @reactive.Effect
    @reactive.event(input.update_cell)
    def update_cell():
        if input.row_select() and input.col_select() and input.new_value():
            df = table_data.get().copy()
            row_idx = int(input.row_select())
            col_name = input.col_select()
            new_val = input.new_value()
            
            # Type conversion based on column
            if col_name == 'Price':
                try:
                    new_val = float(new_val)
                except ValueError:
                    return
            elif col_name == 'Quantity':
                try:
                    new_val = int(new_val)
                except ValueError:
                    return
            elif col_name == 'In_Stock':
                new_val = new_val.lower() in ['true', '1', 'yes']
            
            # Update the cell
            df.iloc[row_idx, df.columns.get_loc(col_name)] = new_val
            table_data.set(df)
            
            # Clear the input
            ui.update_text("new_value", value="")

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
