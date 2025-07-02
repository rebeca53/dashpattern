import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy, Input, Output, html
from dash_extensions.javascript import arrow_function, assign
import dash_svg as svg

# https://medium.com/@kuldippmagar/creating-interactive-maps-with-svg-patterns-a121e2970d72
# https://github.com/stevej2608/dash-svg/tree/master
# https://www.dash-leaflet.com/components/vector_layers/svg_overlay
# https://stackoverflow.com/questions/13069446/simple-fill-pattern-in-svg-diagonal-hatching

def get_info(feature=None):
    header = [html.H4("US Population Density")]
    if not feature:
        return header + [html.P("Hoover over a state")]
    return header + [
        html.B(feature["properties"]["name"]),
        html.Br(),
        "{:.3f} people / mi".format(feature["properties"]["density"]),
        html.Sup("2"),
    ]

def create_svg(color):
    return svg.Svg([
        svg.Defs([
            svg.Pattern(
                id="diagonalHatch",
                patternUnits="userSpaceOnUse",
                width=20,
                height=20,
                children=[
                    svg.Rect(width=20, height=20, fill=color),
                    svg.Path(
                        d="M-5,5 l10,-10 M0,20 l20,-20 M15,25 l10,-10",
                        stroke="gray",
                        strokeWidth=4
                    )
                ]
            )
        ])
    ], style={"height": 0, "width": 0, "position": "absolute"})

classes = [0, 10, 20, 50, 100, 200, 500, 1000]
colorscale = ["#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"]
style = dict(weight=2, opacity=1, color="white", dashArray="3", fillOpacity=0.7)
# Create colorbar.
ctg = [
    "{}+".format(
        cls,
    )
    for i, cls in enumerate(classes[:-1])
] + ["{}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
                      
    function createSVG(color) {
        const existing = document.getElementById("diagonalHatch");
        if (existing) {
            // Just update the color of the existing rect
            const rect = existing.querySelector("rect");
            if (rect) rect.setAttribute("fill", color);
            return;
        }
                      
        // Create the SVG namespace
        const svgns = "http://www.w3.org/2000/svg";

        // Create SVG element
        const svg = document.createElementNS(svgns, "svg");
        svg.setAttribute("style", "height: 0; width: 0; position: absolute");

        // Create <defs> element
        const defs = document.createElementNS(svgns, "defs");

        // Create <pattern> element
        const pattern = document.createElementNS(svgns, "pattern");
        pattern.setAttribute("id", "diagonalHatch");
        pattern.setAttribute("patternUnits", "userSpaceOnUse");
        pattern.setAttribute("width", "20");
        pattern.setAttribute("height", "20");

        // Create <rect> background with provided color
        const rect = document.createElementNS(svgns, "rect");
        rect.setAttribute("width", "20");
        rect.setAttribute("height", "20");
        rect.setAttribute("fill", color);

        // Create <path> hatch lines
        const path = document.createElementNS(svgns, "path");
        path.setAttribute("d", "M-5,5 l10,-10 M0,20 l20,-20 M15,25 l10,-10");
        path.setAttribute("stroke", "gray");
        path.setAttribute("stroke-width", "4");

        // Assemble the elements
        pattern.appendChild(rect);
        pattern.appendChild(path);
        defs.appendChild(pattern);
        svg.appendChild(defs);

        // Append to the document body
        document.body.appendChild(svg);
    }

    const {classes, colorscale, style, colorProp} = context.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class            
        }
    }

    if (parseFloat(value) > 100) {
        style.fillColor = "url(#diagonalHatch)";
    } 
                      
    return style;
}""")
# Create geojson.
geojson = dl.GeoJSON(
    url="/assets/us-states.json",  # url to geojson file
    style=style_handle,  # how to style each polygon
    zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
    zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
    hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray="")),  # style applied on hover
    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="density"),
    
    id="geojson",
)
# Create info control.
info = html.Div(
    children=get_info(),
    id="info",
    className="info",
    style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"},
)
# Create app.
app = DashProxy(prevent_initial_callbacks=True)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        <script>
            L_PREFER_CANVAS=true;
            L_SCROLL_WHEEL_ZOOM=false;

            HTMLCanvasElement.prototype.getContext = function(origFn) {
            return function(type, attribs) {
            attribs = attribs || {};
            attribs.preserveDrawingBuffer = true;
            return origFn.call(this, type, attribs);
             };
            }(HTMLCanvasElement.prototype.getContext);
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}

        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div([
    dl.Map(
        children=[dl.TileLayer(), geojson, colorbar, info], style={"height": "50vh"}, center=[56, 10], zoom=6
    ),
    html.Div(id="svg-dashed-mask", children=create_svg("blue"))
])



@app.callback(Output("info", "children"), Input("geojson", "hoverData"))
def info_hover(feature):
    return get_info(feature)


if __name__ == "__main__":
    app.run()