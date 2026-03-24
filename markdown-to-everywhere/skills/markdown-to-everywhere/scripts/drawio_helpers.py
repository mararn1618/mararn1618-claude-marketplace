#!/usr/bin/env python3
"""Shared draw.io diagram generation helpers.

Provides styles, ERD entity builder, legend, XML generation, and the critical
ID-prefixing write function. Zero external dependencies (stdlib only).

Usage:
    from drawio_helpers import STYLES, make_erd_entity, make_legend, write_diagram
    from pathlib import Path

    def gen_my_diagram():
        cells = []
        cells.append({"id": "box1", "value": "<b>Extract</b>", "style": STYLES["process"],
                       "x": 100, "y": 100, "w": 160, "h": 60})
        cells.append({"id": "store1", "value": "<b>Outbox</b>", "style": STYLES["store_existing"],
                       "x": 350, "y": 100, "w": 120, "h": 60})
        cells.append({"id": "e1", "source": "box1", "target": "store1",
                       "style": STYLES["arrow"], "label": "writes"})
        cells.extend(make_legend(500, 300))
        return cells

    write_diagram(Path("diagrams/01-my-diagram.drawio"), "My Diagram", gen_my_diagram())
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# ============================================================
# Shared styles: 7 entity categories + utilities
# ============================================================

STYLES = {
    # --- Entity categories (use consistently across ALL diagrams) ---
    "process": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFB3BA;strokeColor=#CC4455;"
        "fontFamily=Helvetica;fontSize=11;fontStyle=1;"
    ),
    "store_existing": (
        "shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#BAFFC9;strokeColor=#339944;"
        "fontFamily=Helvetica;fontSize=11;size=12;"
    ),
    "store_new": (
        "shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#FFFACD;strokeColor=#CC9900;"
        "fontFamily=Helvetica;fontSize=11;size=12;"
    ),
    "core_system": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#D4E6F1;strokeColor=#1A5276;"
        "fontFamily=Helvetica;fontSize=11;fontStyle=1;strokeWidth=2;"
    ),
    "external": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#BAE1FF;strokeColor=#2266AA;"
        "fontFamily=Helvetica;fontSize=11;"
    ),
    "btp": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFBA;strokeColor=#CC8800;"
        "dashed=1;dashPattern=5 3;fontFamily=Helvetica;fontSize=11;"
    ),
    "new_component": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8DAEF;strokeColor=#7744AA;"
        "fontFamily=Helvetica;fontSize=11;"
    ),
    # --- Grouping / container ---
    "cluster": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#999999;"
        "dashed=1;dashPattern=8 4;verticalAlign=top;fontFamily=Helvetica;fontSize=13;"
        "fontStyle=1;container=1;collapsible=0;"
    ),
    # --- Arrows ---
    "arrow": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "fontFamily=Helvetica;fontSize=9;strokeColor=#555555;"
    ),
    "arrow_dashed": (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "fontFamily=Helvetica;fontSize=9;strokeColor=#555555;dashed=1;"
    ),
    # --- Labels / tags ---
    "label": (
        "text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;"
        "fontFamily=Helvetica;fontSize=10;fontColor=#666666;"
    ),
    "tag_existing": "text;html=1;fontFamily=Helvetica;fontSize=9;fontColor=#339944;fontStyle=1;",
    "tag_new": "text;html=1;fontFamily=Helvetica;fontSize=9;fontColor=#2266AA;fontStyle=1;",
    "tag_changed": "text;html=1;fontFamily=Helvetica;fontSize=9;fontColor=#CC8800;fontStyle=1;",
    # --- ERD entities (professional table style) ---
    "erd_existing": (
        "shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;"
        "fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;"
        "fontFamily=Helvetica;fontSize=12;fillColor=#BAFFC9;strokeColor=#339944;"
        "strokeWidth=1.5;rounded=1;"
    ),
    "erd_new": (
        "shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;"
        "fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;"
        "fontFamily=Helvetica;fontSize=12;fillColor=#FFFACD;strokeColor=#CC9900;"
        "strokeWidth=1.5;rounded=1;"
    ),
    "erd_junction": (
        "shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;"
        "fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;"
        "fontFamily=Helvetica;fontSize=11;fillColor=#E8F5E9;strokeColor=#66BB6A;rounded=1;"
    ),
}

# Color scheme reference (for documentation / legend):
#   process:        salmon   #FFB3BA / #CC4455
#   store_existing: green    #BAFFC9 / #339944   (cylinder)
#   store_new:      lemon    #FFFACD / #CC9900   (cylinder)
#   core_system:    steel    #D4E6F1 / #1A5276   (bold, thick border)
#   external:       blue     #BAE1FF / #2266AA
#   btp:            yellow   #FFFFBA / #CC8800   (dashed)
#   new_component:  lavender #E8DAEF / #7744AA


# ============================================================
# ERD entity builder
# ============================================================

def make_erd_entity(entity_id, title, tag, fields, style_key, x, y, w=180):
    """Create a professional ERD entity as a unified box with header + fields.

    Args:
        entity_id: Unique ID for this entity (will be prefixed by write_diagram)
        title: Entity name shown in header
        tag: Status tag: "EXISTING", "NEW", or "CHANGED"
        fields: List of field name strings
        style_key: Key into STYLES dict (e.g., "erd_existing", "erd_new")
        x, y: Position
        w: Width (default 180)

    Returns:
        (cells, total_height) - list of cell dicts and the total height

    Edges should connect to '{entity_id}_fields', not the parent container.
    """
    tag_color = {"EXISTING": "#339944", "NEW": "#2266AA", "CHANGED": "#CC8800"}.get(tag, "#666666")
    field_lines = "<br>".join(f"- {f}" for f in fields)
    value = f'<b>{title}</b> <font color="{tag_color}">[{tag}]</font>'
    row_h = max(16 * len(fields) + 10, 30)
    total_h = 30 + row_h

    cells = [
        {
            "id": entity_id, "value": value,
            "style": STYLES[style_key],
            "x": x, "y": y, "w": w, "h": total_h,
        },
        {
            "id": f"{entity_id}_fields",
            "value": f'<font style="font-size:10px">{field_lines}</font>',
            "style": (
                "text;html=1;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;"
                "overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];"
                "portConstraint=eastwest;fontFamily=Helvetica;fontSize=10;fillColor=none;"
            ),
            "x": 0, "y": 30, "w": w, "h": row_h,
            "parent": entity_id,
        },
    ]
    return cells, total_h


# ============================================================
# Legend builder
# ============================================================

def make_legend(x, y):
    """Generate the standard 7-category color legend at the given position."""
    lw, rh, sw, gap = 200, 22, 30, 4
    rows = [
        ("Core System",     "rounded=1;whiteSpace=wrap;html=1;fillColor=#D4E6F1;strokeColor=#1A5276;fontSize=9;fontFamily=Helvetica;strokeWidth=2;"),
        ("Processing Stage","rounded=1;whiteSpace=wrap;html=1;fillColor=#FFB3BA;strokeColor=#CC4455;fontSize=9;fontFamily=Helvetica;"),
        ("Store (existing)","shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#BAFFC9;strokeColor=#339944;fontSize=9;fontFamily=Helvetica;size=6;"),
        ("Store (new)",     "shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#FFFACD;strokeColor=#CC9900;fontSize=9;fontFamily=Helvetica;size=6;"),
        ("External Party",  "rounded=1;whiteSpace=wrap;html=1;fillColor=#BAE1FF;strokeColor=#2266AA;fontSize=9;fontFamily=Helvetica;"),
        ("Cloud Service",   "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFBA;strokeColor=#CC8800;dashed=1;fontSize=9;fontFamily=Helvetica;"),
        ("New Component",   "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8DAEF;strokeColor=#7744AA;fontSize=9;fontFamily=Helvetica;"),
    ]
    total_h = 28 + len(rows) * (rh + gap) + 8
    cells = [{
        "id": "legend_box", "value": "<b>Legend</b>",
        "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CCCCCC;verticalAlign=top;fontFamily=Helvetica;fontSize=11;fontStyle=1;",
        "x": x, "y": y, "w": lw, "h": total_h,
    }]
    for i, (label, swatch_style) in enumerate(rows):
        ry = y + 28 + i * (rh + gap)
        cells.append({"id": f"leg_sw_{i}", "value": "", "style": swatch_style,
                       "x": x + 10, "y": ry, "w": sw, "h": rh})
        cells.append({"id": f"leg_lb_{i}", "value": label,
                       "style": "text;html=1;fontFamily=Helvetica;fontSize=10;align=left;verticalAlign=middle;",
                       "x": x + sw + 16, "y": ry, "w": lw - sw - 30, "h": rh})
    return cells


# ============================================================
# XML generation
# ============================================================

def make_mxfile(diagram_name, cells):
    """Build complete draw.io XML tree from a list of cell dicts.

    Cell dict format:
      Vertex: {"id", "value", "style", "x", "y", "w" (default 140), "h" (default 50)}
              Optional: "parent" (default "1")
      Edge:   {"id", "source", "target", "style"}
              Optional: "label"
    """
    mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
    diagram = ET.SubElement(mxfile, "diagram", name=diagram_name, id="d1")
    model = ET.SubElement(diagram, "mxGraphModel",
                          dx="1200", dy="800", grid="1", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1",
                          fold="1", page="0", pageScale="1", math="0", shadow="0")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for c in cells:
        attrs = {"id": c["id"], "parent": c.get("parent", "1")}
        if "value" in c:
            attrs["value"] = c["value"]
        if "style" in c:
            attrs["style"] = c["style"]
        if "source" in c:
            attrs["source"] = c["source"]
            attrs["target"] = c["target"]
            attrs["edge"] = "1"
        else:
            attrs["vertex"] = "1"

        cell = ET.SubElement(root, "mxCell", **attrs)
        geo = ET.SubElement(cell, "mxGeometry")
        if "x" in c:
            geo.set("x", str(c["x"]))
            geo.set("y", str(c["y"]))
            geo.set("width", str(c.get("w", 140)))
            geo.set("height", str(c.get("h", 50)))
        elif "source" in c:
            geo.set("relative", "1")
        geo.set("as", "geometry")

        if c.get("label"):
            point = ET.SubElement(geo, "mxPoint")
            point.set("as", "offset")

    return ET.ElementTree(mxfile)


def write_diagram(path, name, cells):
    """Write cells to a .drawio file, prefixing all IDs to avoid collisions.

    CRITICAL: When multiple diagrams appear on the same HTML page, the draw.io
    viewer shares a cell ID namespace. Without prefixing, you get
    'd.setId is not a function' errors. This function handles it automatically.
    """
    path = Path(path)
    prefix = path.stem.replace('-', '_') + '_'
    for c in cells:
        c["id"] = prefix + c["id"]
        if "source" in c:
            c["source"] = prefix + c["source"]
            c["target"] = prefix + c["target"]
        if c.get("parent") and c["parent"] not in ("0", "1"):
            c["parent"] = prefix + c["parent"]

    tree = make_mxfile(name, cells)
    ET.indent(tree, space="  ")
    tree.write(str(path), xml_declaration=True, encoding="UTF-8")
    print(f"  Generated: {path.name}")
