import base64
import io
import dash
# Import dash-bootstrap-components
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, Patch, no_update
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import pandas.api.types as ptypes

# --- Initialize the app with a Bootstrap theme ---
# You can try other themes like dbc.themes.FLATLY, dbc.themes.LITERA, etc.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# --- Define Column Names (Keep these updated) ---
# (Column name definitions remain the same)
PURCHASED_COL = "In the past 24 months, have you purchased a portable power bank?"
FREQUENCY_COL = "How frequently do you leave your home for leisure, social, or work-related activities?"
RELY_SMARTPHONE_COL = "I rely on my smartphone for a variety of tasks when I’m away from home. (1= Strong Disagree, 5= Strong Agree)"
FEEL_EASE_COL = "I feel more at ease when I have a way to charge my phone on the go."
INTEREST_COL = "How interested are you in this power bank concept? Scale of 1–5 (1 = Not at all interested, 5 = Very interested) (https://1moretime.co.za/products/one-more-night-blue-1)"
SATISFACTION_COL = "How satisfied are you with your current power bank(s)? (1 = Very dissatisfied, 5 = Very satisfied)"
AGE_COL = "Age"
DISCOVERY_COL = "Where do you typically learn about (or discover) new accessories or gadgets? (Select all that apply)"
OWNERSHIP_COUNT_COL = "How many power banks do you currently own?"
KNOWLEDGE_COL = "What is your current knowledge level regarding Fast Charging"
IMPORTANCE_COL = "How Important is Fast Charging in your decision to purchase a charger/Power Bank"
APPEALING_COL = "Which of the following aspects do you find most appealing?"
CONCERN_COL = "Which aspects concern you?"
PRICE_VALUE_COL = "At what price (in Rand) would you consider it a good value?"
PURCHASE_DRIVER_COL = "What would make you more likely to purchase this product? (Select all that apply)"
SUSTAINABILITY_FREQ_COL = "How often do you purchase sustainable/eco-friendly products?"
RESIDENCE_COL = "Primary Residence"
BETA_TESTER_COL = "Would you like to be a beta tester for Project Sepanya. You will recieve a free sample unit to test and a free final unit once the product development is completed."

# --- Column Lists (Remain the same) ---
UNIVARIATE_ANALYSIS_COLUMNS = [
    PURCHASED_COL, FREQUENCY_COL, RELY_SMARTPHONE_COL, FEEL_EASE_COL,
    INTEREST_COL, SATISFACTION_COL, AGE_COL, OWNERSHIP_COUNT_COL,
    KNOWLEDGE_COL, IMPORTANCE_COL, APPEALING_COL, CONCERN_COL,
    PRICE_VALUE_COL, SUSTAINABILITY_FREQ_COL, RESIDENCE_COL, BETA_TESTER_COL,
    DISCOVERY_COL, PURCHASE_DRIVER_COL
]
MULTIVARIATE_ANALYSIS_COLUMNS = [
    PURCHASED_COL, FREQUENCY_COL, RELY_SMARTPHONE_COL, FEEL_EASE_COL,
    INTEREST_COL, SATISFACTION_COL, AGE_COL, OWNERSHIP_COUNT_COL,
    KNOWLEDGE_COL, IMPORTANCE_COL, APPEALING_COL, CONCERN_COL,
    PRICE_VALUE_COL, SUSTAINABILITY_FREQ_COL, RESIDENCE_COL, BETA_TESTER_COL
]
MULTI_SELECT_COLUMNS = [
    DISCOVERY_COL, PURCHASE_DRIVER_COL
]

# --- Define the layout using Dash Bootstrap Components ---
app.layout = dbc.Container([
    # Header Row
    dbc.Row(dbc.Col(html.H1("Survey Data Visualizer", className="text-center my-4"))), # my-4 adds margin top/bottom

    # Upload Row
    dbc.Row(dbc.Col(
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]),
            style={ # Basic style for the upload box itself
                'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center'
            },
            className="mb-4" # Margin bottom using Bootstrap class
        ), width=10, lg=8, xl=6 # Limit width on larger screens
    ), justify="center"), # Center the column within the row

    # Message Row
    dbc.Row(dbc.Col(
        html.Div(id='output-message', className="text-center text-muted mb-4") # Muted text, margin bottom
    )),

    dcc.Store(id='stored-data'),

    # Analysis Sections Row (using Cards)
    dbc.Row([
        # Univariate Card
        dbc.Col(lg=12, className="mb-4", children=[ # On large screens, take up half width. Margin bottom.
            dbc.Card([
                # Use CardHeader for a distinct header section
                dbc.CardHeader(html.H4("Univariate Analysis", className="mb-0")), # Remove default margin from H4
                dbc.CardBody([
                    html.P("Select a variable to see its distribution:", className="card-text text-muted"), # Use muted text
                    dcc.Dropdown(
                        id='dropdown-univariate', options=[], placeholder="Select Variable...",
                        clearable=False, className="mb-3" # Margin bottom
                    ),
                    # Wrap graph in a div for potential loading state later
                    html.Div(dcc.Graph(id='graph-univariate', figure={})),
                    html.Div(id='univariate-message', className="text-muted small mt-2") # Small, muted text below graph
                ])
            ], className="h-100") # Make card fill column height if needed
        ]),

        # Multivariate Card
        dbc.Col(lg=12, className="mb-4", children=[
             dbc.Card([
                dbc.CardHeader(html.H4("Multivariate Analysis", className="mb-0")),
                dbc.CardBody([
                    html.P("Select two variables to see how they interact:", className="card-text text-muted"),
                    # Use dbc Row/Col for better alignment of dropdowns
                    dbc.Row([
                        dbc.Col(md=6, children=[
                            dbc.Label("Variable 1:", html_for='dropdown-var1', className="fw-bold"), # Bold label
                            dcc.Dropdown(
                                id='dropdown-var1', options=[], placeholder="Select...",
                                clearable=False, className="mb-2 mb-md-0" # Responsive margin
                            )
                        ]),
                        dbc.Col(md=6, children=[
                            dbc.Label("Variable 2:", html_for='dropdown-var2', className="fw-bold"),
                            dcc.Dropdown(
                                id='dropdown-var2', options=[], placeholder="Select...",
                                clearable=False
                            )
                        ]),
                    ], className="mb-3"), # Margin below dropdown row
                    html.Div(dcc.Graph(id='graph-multivariate', figure={})),
                    html.Div(id='multivariate-message', className="text-muted small mt-2")
                ])
            ], className="h-100")
        ]),
    ]), # End of main analysis row

], fluid=False) # fluid=False gives standard container width, fluid=True uses full width

# --- Helper function for processing multi-select columns (Unchanged) ---
def process_multi_select(df, column_name, separator=','):
    # ... (function definition remains the same) ...
    if column_name not in df.columns: return None
    try:
        s = df[column_name].dropna()
        counts = s.astype(str).str.split(separator).explode().str.strip().value_counts()
        counts = counts[counts.index != ''] # Remove empty strings
        return counts
    except Exception as e:
        print(f"Error processing multi-select column '{column_name}': {e}")
        return None

# --- Callback to parse uploaded CSV and store data (Unchanged) ---
@callback(
    Output('stored-data', 'data'),
    Output('output-message', 'children', allow_duplicate=True),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def parse_upload_store_data(contents, filename):
    # ... (Parsing and type conversion logic remains the same) ...
    if contents is None: return None, "Upload component cleared."
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), low_memory=False)
            # --- Basic Data Type Conversion ---
            cols_to_try_numeric = [
                RELY_SMARTPHONE_COL, FEEL_EASE_COL, INTEREST_COL, SATISFACTION_COL,
                AGE_COL, OWNERSHIP_COUNT_COL, IMPORTANCE_COL, PRICE_VALUE_COL
            ]
            for col in cols_to_try_numeric:
                if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
            cols_to_try_category = [
                PURCHASED_COL, FREQUENCY_COL, KNOWLEDGE_COL, APPEALING_COL, CONCERN_COL,
                SUSTAINABILITY_FREQ_COL, RESIDENCE_COL, BETA_TESTER_COL
            ]
            for col in cols_to_try_category:
                 if col in df.columns: df[col] = df[col].fillna('Unknown').astype('category')
        else:
            return None, html.Div(['Invalid file type. Please upload a CSV file.'])
        data_json = df.to_dict('records')
        message = html.Div([f"Processing '{filename}' ({len(df)} rows)..."]) # Simpler message
        return data_json, message
    except Exception as e:
        print(f"Error processing file: {e}")
        return None, dbc.Alert(f'Error processing file: {e}. Ensure valid CSV (UTF-8 recommended).', color="danger") # Use dbc.Alert

# --- Callback to Populate ALL Dropdowns (Unchanged logic, maybe update message) ---
@callback(
    Output('dropdown-univariate', 'options'),
    Output('dropdown-var1', 'options'),
    Output('dropdown-var2', 'options'),
    Output('dropdown-univariate', 'value'),
    Output('dropdown-var1', 'value'),
    Output('dropdown-var2', 'value'),
    Output('output-message', 'children', allow_duplicate=True),
    Input('stored-data', 'data'),
    prevent_initial_call=True
)
def update_all_dropdowns(data_json):
    # ... (Dropdown population logic remains the same) ...
    if data_json is None: return [], [], [], None, None, None, "Upload data to populate dropdowns."
    try:
        df = pd.DataFrame(data_json)
        if df.empty: return [], [], [], None, None, None, "Uploaded CSV is empty."
        available_uni_cols = [col for col in UNIVARIATE_ANALYSIS_COLUMNS if col in df.columns]
        available_multi_cols = [col for col in MULTIVARIATE_ANALYSIS_COLUMNS if col in df.columns]
        uni_options = [{'label': col, 'value': col} for col in available_uni_cols]
        multi_options = [{'label': col, 'value': col} for col in available_multi_cols]
        uni_val = available_uni_cols[0] if available_uni_cols else None
        multi_val1 = available_multi_cols[0] if available_multi_cols else None
        multi_val2 = available_multi_cols[1] if len(available_multi_cols) > 1 else None
        msg = f"Data loaded ({len(df)} responses). Select variables below for analysis." # Updated message
        return uni_options, multi_options, multi_options, uni_val, multi_val1, multi_val2, msg
    except Exception as e:
        print(f"Error updating dropdowns: {e}")
        return [], [], [], None, None, None, dbc.Alert(f"Error populating dropdowns: {e}", color="warning")

# --- Callback to Update Univariate Graph (Unchanged logic) ---
@callback(
    Output('graph-univariate', 'figure'),
    Output('univariate-message', 'children'),
    Input('dropdown-univariate', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call=True
)
def update_univariate_graph(selected_column, data_json):
    # ... (Univariate plot generation logic remains the same) ...
    if not selected_column or not data_json: return go.Figure(), "Select a variable from the dropdown."
    try:
        df = pd.DataFrame(data_json); series = df[selected_column].dropna()
        if selected_column not in df.columns: return go.Figure(), f"Error: Column '{selected_column}' not found."
        if series.empty: return go.Figure(), f"No valid data found for '{selected_column}'."
        n_responses = len(series); n_total = len(df)
        msg = f"Plotting {n_responses} of {n_total} responses."
        fig = go.Figure()
        if selected_column in MULTI_SELECT_COLUMNS:
            counts = process_multi_select(df, selected_column)
            if counts is not None and not counts.empty:
                fig = px.bar(x=counts.index, y=counts.values, title=f"{selected_column}", labels={'x': 'Option', 'y': 'Mentions'})
                fig.update_layout(xaxis={'categoryorder':'total descending'}, title_x=0.5)
            else: msg += f" No multi-select data."
        elif ptypes.is_numeric_dtype(series.dtype):
            fig = px.histogram(x=series, nbins=20, title=f"{selected_column}")
            fig.update_layout(xaxis_title=selected_column, yaxis_title="Count", title_x=0.5)
        elif ptypes.is_categorical_dtype(series.dtype) or ptypes.is_object_dtype(series.dtype):
             counts = series.astype('category').value_counts()
             fig = px.bar(x=counts.index, y=counts.values, title=f"{selected_column}")
             fig.update_layout(xaxis_title=selected_column, yaxis_title="Count", xaxis={'categoryorder':'total descending'}, title_x=0.5)
        else: msg += f" Cannot plot dtype {series.dtype}."
        # Make figure titles less prominent if desired
        fig.update_layout(margin=dict(t=40, b=10), title_font_size=16) # Adjust top margin, title size
        return fig, msg
    except Exception as e:
         print(f"Error updating univariate graph for {selected_column}: {e}")
         return go.Figure(), dbc.Alert(f"Plotting Error: {e}", color="warning")


# --- Callback to Update Multivariate Graph (Unchanged logic) ---
@callback(
    Output('graph-multivariate', 'figure'),
    Output('multivariate-message', 'children'),
    Input('dropdown-var1', 'value'),
    Input('dropdown-var2', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call=True
)
def update_multivariate_graph(var1, var2, data_json):
    # ... (Multivariate plot generation logic remains the same) ...
    if not var1 or not var2 or not data_json: return go.Figure(), "Select two variables."
    try:
        df = pd.DataFrame(data_json).copy(); msg = ""
        if var1 not in df.columns or var2 not in df.columns: return go.Figure(), f"Column not found."
        df_filtered = df[[var1, var2]].dropna()
        if len(df_filtered) != len(df): msg = f"Plotting {len(df_filtered)} of {len(df)} responses (NaNs excluded). "
        dtype1 = df_filtered[var1].dtype; dtype2 = df_filtered[var2].dtype
        is_numeric1 = ptypes.is_numeric_dtype(dtype1); is_numeric2 = ptypes.is_numeric_dtype(dtype2)
        is_categorical1 = ptypes.is_categorical_dtype(dtype1) or ptypes.is_object_dtype(dtype1)
        is_categorical2 = ptypes.is_categorical_dtype(dtype2) or ptypes.is_object_dtype(dtype2)
        fig = go.Figure()
        title = f"{var1} vs. {var2}" # Default title
        try:
            if var1 == var2:
                title=f"Distribution of {var1}"
                if is_numeric1: fig = px.histogram(df_filtered, x=var1)
                else: counts = df_filtered[var1].value_counts(); fig = px.bar(x=counts.index, y=counts.values, labels={'x': var1, 'y': 'Count'})
            elif is_numeric1 and is_numeric2: fig = px.scatter(df_filtered, x=var1, y=var2, trendline="ols")
            elif is_numeric1 and is_categorical2: title=f"{var1} by {var2}"; fig = px.box(df_filtered, x=var2, y=var1, points="all"); fig.update_layout(xaxis_title=var2, yaxis_title=var1)
            elif is_categorical1 and is_numeric2: title=f"{var2} by {var1}"; fig = px.box(df_filtered, x=var1, y=var2, points="all"); fig.update_layout(xaxis_title=var1, yaxis_title=var2)
            elif is_categorical1 and is_categorical2: title=f"{var1} by {var2}"; fig = px.histogram(df_filtered, x=var1, color=var2, barmode='group'); fig.update_layout(xaxis_title=var1, yaxis_title="Count")
            else: msg += f"Cannot plot {dtype1} vs {dtype2}."
            fig.update_layout(title=title, title_x=0.5) # Center title
        except Exception as plot_err: msg += f" Plot Error: {plot_err}"; fig = go.Figure()
        fig.update_layout(margin=dict(t=40, b=10), title_font_size=16) # Adjust margins/title size
        return fig, msg
    except Exception as e:
        print(f"Error in multivariate callback: {e}"); return go.Figure(), dbc.Alert(f"Error: {e}", color="danger")

# Run the app
if __name__ == '__main__':
    app.run()#debug=True