import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_chart(symbol, df, theme):
    dark_palette = {}
    dark_palette["bg_color"] = "#2e2e2e"
    dark_palette["plot_bg_color"] = "#2e2e2e"
    dark_palette["grid_color"] = "#595656"
    dark_palette["text_color"] = "#ffffff"
    dark_palette["dark_candle"] = "#226287"
    dark_palette["light_candle"] = "#a6a4a4"
    dark_palette["volume_color"] = "#5c285b"
    dark_palette["border_color"] = "#ffffff"
    dark_palette["color_1"] = "#5c285b"
    dark_palette["color_2"] = "#802c62"
    dark_palette["color_3"] = "#a33262"
    dark_palette["color_4"] = "#c43d5c"
    dark_palette["color_5"] = "#de4f51"
    dark_palette["color_6"] = "#f26841"
    dark_palette["color_7"] = "#fd862b"
    dark_palette["color_8"] = "#ffa600"
    dark_palette["color_9"] = "#3366d6"
    light_palette = {}
    light_palette["bg_color"] = "#ffffff"
    light_palette["plot_bg_color"] = "#ffffff"
    light_palette["grid_color"] = "#e6e6e6"
    light_palette["text_color"] = "#2e2e2e"
    light_palette["dark_candle"] = "#4d98c4"
    light_palette["light_candle"] = "#b1b7ba"
    light_palette["volume_color"] = "#c74e96"
    light_palette["border_color"] = "#2e2e2e"
    light_palette["color_1"] = "#5c285b"
    light_palette["color_2"] = "#802c62"
    light_palette["color_3"] = "#a33262"
    light_palette["color_4"] = "#c43d5c"
    light_palette["color_5"] = "#de4f51"
    light_palette["color_6"] = "#f26841"
    light_palette["color_7"] = "#fd862b"
    light_palette["color_8"] = "#ffa600"
    light_palette["color_9"] = "#3366d6"
    palette = light_palette
    if theme == "Dark Mode":
        palette = dark_palette
    #  Create sub plots
    fig = make_subplots(rows=4, cols=1, subplot_titles=[f"{symbol} Chart", '', '', 'Volume'], \
                        specs=[[{"rowspan": 3, "secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}],
                               [{"secondary_y": True}]], \
                        vertical_spacing=0.04, shared_xaxes=True)
    #  Plot close price
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 close=df['Close'],
                                 low=df['Low'],
                                 high=df['High'],
                                 increasing_line_color=palette['light_candle'], decreasing_line_color=palette['dark_candle'], name='Price'), row=1, col=1)
    #  Add EMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color=palette['color_3'], width=1), name="EMA 9"),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color=palette['color_8'], width=1), name="EMA 21"), row=1,
                  col=1)
    #  Add Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_HIGH'], line=dict(color=palette['color_5'], width=1), name="BB High"),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_LOW'], line=dict(color=palette['color_9'], width=1), name="BB Low"), row=1,
                  col=1)
    #  Volume Histogram
    fig.add_trace(go.Bar(
        name='Volume',
        x=df.index, y=df['Volume'], marker_color=palette['volume_color']), row=4,col=1)
    fig.update_layout(
            title={'text': '', 'x': 0.5},
            font=dict(family="Verdana", size=12, color=palette["text_color"]),
            autosize=True,
            width=1280, height=720,
            xaxis={"rangeslider": {"visible": False}},
            plot_bgcolor=palette["plot_bg_color"],
            paper_bgcolor=palette["bg_color"])
    fig.update_yaxes(visible=False, secondary_y=True)
    #  Change grid color
    fig.update_xaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"])
    fig.update_yaxes(showline=True, linewidth=1, linecolor=palette["grid_color"],gridcolor=palette["grid_color"])
    #  Create output file
    #file_name = f"{symbol}_chart.png"
    #fig.write_image(file_name, format="png")
    return fig
