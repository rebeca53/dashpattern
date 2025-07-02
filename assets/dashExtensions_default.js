window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {

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

            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class            
                }
            }

            if (parseFloat(value) > 100) {
                style.fillColor = "url(#diagonalHatch)";
            }

            return style;
        }
    }
});