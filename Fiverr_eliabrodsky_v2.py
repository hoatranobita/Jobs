from jupyter_dash import JupyterDash
import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table
from dash.exceptions import PreventUpdate
import dash_bio

# Create database
datalink = 'https://raw.githubusercontent.com/PineBiotech/omicslogic/master/HepG_vs_control_DESeq2_input2_new_DeSeq2_All.txt'
df = pd.read_table(datalink, sep='\t', header=0)
# keep only the fields needed for the plot
lst = ['GENENAME', 'SYMBOL', 'GENENAME.1', 'log2FoldChange', 'padj']
diff_df = df[lst]
diff_df['ANOT'] = diff_df['SYMBOL'] + ' , ' + diff_df['GENENAME.1']

# Determine the min max value of log2
max_log = df['log2FoldChange'].max()
min_log = df['log2FoldChange'].min()

# Create dashboard
app = JupyterDash(__name__,external_stylesheets=[dbc.themes.LUX]) # You can change external_stylesheets
colorscales = px.colors.named_colorscales()
app.layout = html.Div([dbc.Tabs(
            [dbc.Tab(label="Dashboard", tab_id="dashboard"),
            dbc.Tab(label="Table", tab_id="table"),
            ],
            id="tabs",
            active_tab="dashboard",
        ),
    html.Div(id="tab-content", className="p-4"),
    ])

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    if active_tab == "dashboard":
        return html.Div([
        dbc.Row([
        dbc.Col([
        html.H4('Differental Gene Expression Result',className='text-left',style={'padding-left' : 25,"text-decoration": "underline"}),
        ],width={'size':6,'offset':0,'order':1},style={'padding-top' : 25}),
        dbc.Col([
        html.H5('Adjust Colors',className='text-left'),
        ],width={'size':2,'offset':0,'order':1},style={'padding-top' : 25}),                    
        dbc.Col([
        dcc.Dropdown(id='color_range',placeholder="Please select color", # Dropdown for heatmap color
                            options=colorscales, 
                            value='aggrnyl',
                            multi=False,
                            disabled=False,
                            clearable=True,
                            searchable=True)
        ],width={'size':4,'offset':0,'order':1},style={'padding-top' : 25}), 
        ]),            
        dbc.Row([
        dbc.Col([
        html.H5('Volcano Plot',className='text-left',style={'padding-left' : 25})
        ],width={'size':6,'offset':0,'order':1},style={'padding-top' : 25}),        
        dbc.Col([
        html.H5('Top Genes Heatmap',className='text-left'),
        ],width={'size':2,'offset':0,'order':1},style={'padding-top' : 25}),        
        dbc.Col([
        html.H6('Number of Genes to select',className='text-left'),
        ],width={'size':2,'offset':0,'order':1},style={'padding-top' : 25}),
        dbc.Col([
        dcc.Input(
        id="input_range_2", type="number", placeholder="Input number", #Input of genre numbers
        min=1, max=100, step=1,value=20,className='text-center'),
        ],width={'size':1,'offset':0,'order':1},style={'padding-top' : 22})        
        ]),
            
        dbc.Row([
            dbc.Col([
            dcc.Graph(id='volcano',figure={},style={'height':600,'width':'auto'}), #Volcano plot
            ],width={'size':6,'offset':0,'order':2},style={'padding-top' : 25}),
            dbc.Col([
            dcc.Graph(id='heatmap',figure={},style={'height':600,'width':'auto'}), #Heatmap plot
            ],width={'size':6,'offset':0,'order':2}),
            
        ]),
            
        dbc.Row([
            dbc.Col([
            html.H6('log2FC',className='text-left')],width={'size':1,'offset':0,'order':2},style={'padding-left' : 25}), #Rangesilder to change log2
            dbc.Col([
             dcc.RangeSlider(
            id='my-range-slider', # any name you'd like to give it
            step=0.5,                # number of steps between values
            min=min_log,
            max=max_log,
            marks={i: {'label': str(i)} for i in range(-10, 10)},
            value=[0,1],     # default value initially chosen
            dots=True)             # True, False - insert dots, only when step>1
            ],width={'size':5,'offset':0,'order':2}),        
            
            dbc.Col([        
            html.H5('Select Genes',className='text-center'),
            ],width={'size':2,'offset':0,'order':2}),
            dbc.Col([
            dcc.Dropdown(id='genes_type',placeholder="Please select gent", #Dropdown for line graphs
                            value='Select',
                            multi=True,
                            disabled=False,
                            clearable=True,
                            searchable=True)
          ],width={'size':4,'offset':0,'order':2}),        
        ]),
        dbc.Row([
            dbc.Col([
            html.H6('P-adj',className='text-left')],width={'size':1,'offset':0,'order':2},style={'padding-left' : 25}),
            dbc.Col([
            dcc.Input(
            id="input_range_3", type="number", placeholder="Input number",
            min=-200, max=200, step=10,value=50,className='text-center'),
          ],width={'size':5,'offset':0,'order':2}),        

          dbc.Col([
          dcc.Graph(id='line_graph',figure={},style={'height':400,'width':'auto'})    
          ],width={'size':6,'offset':0,'order':2}),    
        ]),   
          dcc.Store(id='store-data', data=[], storage_type='memory'), # 'local' or 'session'         
      ])
    
    elif active_tab == "table":
        return html.Div([
        dbc.Row([
            dbc.Col([
            html.H5('Data Table',className='text-center'),
            dash_table.DataTable(id='tbl',
            data=diff_df.to_dict('records'),
            columns=[{"name":k,"id":k} for k in diff_df.columns],
            style_table={'overflow':'scroll','height':550},
            style_header={'backgroundColor':'#305D91','padding':'10px','color':'#FFFFFF'},
            style_cell={'textAlign':'center','minWidth': 95, 'maxWidth': 95, 'width': 95,'font_size': '12px',
                       'whiteSpace':'normal','height':'auto'},
            editable=True,              # allow editing of data inside all cells
            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",         # sort across 'multi' or 'single' columns
            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            row_selectable="multi",     # allow users to select 'multi' or 'single' rows
            row_deletable=True,         # choose if user can delete a row (True) or not (False)
            selected_columns=[],        # ids of columns that user selects
            selected_rows=[],           # indices of rows that user selects
            page_action="native"),    
            html.Hr()
            ],width={'size':12,'offset':0,'order':2},style={'padding-top' : 25}),
        ]),
        ])


@app.callback(Output('volcano','figure'),
             [Input('my-range-slider', 'value'),
             Input('input_range_3', 'value')])    
    
def update_volcano(log_range,padj_range):
    volcano_plot = dash_bio.VolcanoPlot(dataframe=diff_df, 
                     title=dict(text=''),
                     effect_size='log2FoldChange', 
                     logp=True,
                     p='padj', 
                     snp=None, 
                     annotation = 'ANOT',
                     gene='GENENAME',
                     genomewideline_value=padj_range, #Range from input
                     genomewideline_width = 1,
                     genomewideline_color='#EF553B',
                     effect_size_line=log_range, #Range from slider
                     effect_size_line_width = 2,
                     effect_size_line_color='#EF553B',
                     xlabel='log2 Fold Change', 
                     ylabel='-(p-adjusted)')
    volcano_plot.update_layout(plot_bgcolor='white')
    volcano_plot.update_yaxes(showline=False,showgrid=False)
    volcano_plot.update_xaxes(showline=False,showgrid=False) 
    volcano_plot.write_html("volcano_plot.html")
    return volcano_plot

@app.callback(Output('store-data','data'),
             [Input('input_range_2', 'value')]) 

def update_store(genes_number):
    global GenesTop
    dff = df.copy()
    dff.index=dff['GENENAME']
    dff = dff.drop(['GENENAME'], axis = 1)
    Genes = dff[dff.padj < 0.05]
    Genes = Genes[(Genes.log2FoldChange > 1)|(Genes.log2FoldChange < -1)]
    #top 50 genes:
    Genes1 = Genes.sort_values(by=['padj'], ascending=True)
    #clean up the table
    lst = ['baseMean', 'log2FoldChange', 'lfcSE', 'stat', 'pvalue', 'padj', 'SYMBOL', 'GENENAME.1']
    Genes = Genes.drop(lst, axis=1)
    GenesTop = Genes1[:genes_number]
    GenesTop = GenesTop.drop(lst, axis=1)
    return GenesTop.to_dict(orient='records')

@app.callback(Output('heatmap','figure'),
             [Input('store-data','data'),
             Input('color_range', 'value')]) 

def update_heatmap(n,scale):    
    heatmap_plot = px.imshow(GenesTop, aspect="auto",color_continuous_scale=scale,text_auto=".2f")
    heatmap_plot.write_html("heatmap_plot.html")
    return heatmap_plot

@app.callback(
    Output('genes_type', 'options'),
    [Input('store-data','data')])

def options(search_value):
    global GenesTop_2
    GenesTop_2 = GenesTop.reset_index()
    return [{'label':l,'value':l} for l in GenesTop_2.sort_values('GENENAME')['GENENAME'].unique()]

@app.callback(Output('line_graph', 'figure'),
             [Input('genes_type', 'value')])                           
def update_line_graph(genes_type):
    if not genes_type or 'Select' in genes_type:
        raise PreventUpdate  
    else:
        selectgene = GenesTop_2[GenesTop_2["GENENAME"].isin(genes_type)]
        selectgene2 = selectgene.melt(id_vars=["GENENAME"], 
        var_name="HepGType", 
        value_name="Value")
        
        line_graph = px.scatter(selectgene2,
            x=selectgene2['HepGType'],
            y=selectgene2['Value'],
            color = selectgene2['GENENAME'])
        
        line_graph.update_traces(mode='lines',
                        text=selectgene2['Value'].round(decimals=2),
                        line_shape='spline',
                        textposition='top center',
                        texttemplate='%{text:,}')        
        line_graph.update_layout(plot_bgcolor='white')
        line_graph.update_yaxes(showline=False,showgrid=False,exponentformat="none",separatethousands=True)
        line_graph.update_xaxes(showline=False,showgrid=False,exponentformat="none",separatethousands=True)        
        line_graph.write_html("line_plot.html")
        return line_graph


app.run_server(port=8031,mode='inline') #You can delete mode='inline and dash will be open with link
