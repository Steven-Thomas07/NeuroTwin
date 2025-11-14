import plotly.graph_objects as go
import numpy as np

def render_brain(risk):
    regions = ["Prefrontal Cortex", "Amygdala (Anxiety)", "Hippocampus (Memory)"]
    x = [0, 1, 2]
    y = [0, 1, 0]
    z = [0, 0, 1]
    colors = ['green', 'red' if risk > 70 else 'yellow', 'blue']
    sizes = [15, 25 if risk > 70 else 18, 12]
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+text+lines',
        marker=dict(size=sizes, color=colors),
        text=regions,
        textposition="top center",
        line=dict(color='gray', width=3),
        hovertemplate='<b>%{text}</b><br>Risk Impact: %{customdata:.1f}%<extra></extra>',
        customdata=[risk * 0.3, risk, risk * 0.5]
    )])
    fig.update_layout(
        title=f"Brain Digital Twin | Risk: {risk:.1f}%",
        scene=dict(xaxis_title='Left → Right', yaxis_title='Front → Back', zaxis_title='Bottom → Top'),
        height=500
    )
    return fig
