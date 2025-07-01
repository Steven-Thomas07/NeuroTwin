import plotly.graph_objects as go
import numpy as np

def render_brain(risk):
    # 3D brain with amygdala (anxiety), hippocampus (memory), prefrontal (control)
    regions = ["Prefrontal", "Amygdala", "Hippocampus"]
    x = [0, 1, 2]
    y = [0, 1, 0]
    z = [0, 0, 1]
    colors = ['green', 'red' if risk > 70 else 'yellow', 'blue']
    sizes = [15, 25 if risk > 70 else 18, 12]
    
    hovertext = [f"{r}<br>Activity: {100-risk if r=='Amygdala' else risk}%" for r in regions]
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+text+lines',
        marker=dict(size=sizes, color=colors),
        text=regions,
        textposition="top center",
        hovertext=hovertext,
        line=dict(color='gray', width=3)
    )])
    fig.update_layout(
        title=f"Brain Digital Twin | Depression Risk: {risk}%",
        scene=dict(
            xaxis_title='Left ← → Right',
            yaxis_title='Front ← → Back',
            zaxis_title='Bottom ← → Top'
        ),
        height=600
    )
    return fig
