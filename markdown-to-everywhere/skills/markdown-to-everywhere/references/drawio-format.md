# Draw.io Format Reference

Complete reference for the `.drawio` XML format, CLI export, and style properties.
This absorbs and extends the standalone draw.io skill content.

---

## XML Structure

Every `.drawio` file follows this structure:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<mxfile host="app.diagrams.net" type="device">
  <diagram name="Diagram Name" id="d1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10"
                  guides="1" tooltips="1" connect="1" arrows="1"
                  fold="1" page="0" pageScale="1" math="0" shadow="0">
      <root>
        <mxCell id="0"/>                    <!-- root layer -->
        <mxCell id="1" parent="0"/>         <!-- default parent -->
        <!-- diagram cells go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- Cell `id="0"` is the root layer (always present)
- Cell `id="1"` is the default parent (all top-level cells use `parent="1"`)

## Cell Types

### Vertex (box, shape)

```xml
<mxCell id="box1" value="Label" style="rounded=1;whiteSpace=wrap;html=1;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Edge (arrow, connector)

```xml
<mxCell id="e1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
        edge="1" source="box1" target="box2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Every edge must have a `<mxGeometry relative="1" as="geometry"/>` child element.** Self-closing edge cells are invalid.

### Labeled edge

```xml
<mxCell id="e2" value="1:N" style="edgeStyle=orthogonalEdgeStyle;"
        edge="1" source="a" target="b" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Common Shapes

| Shape | Style keyword |
|-------|--------------|
| Rounded rectangle | `rounded=1;whiteSpace=wrap;` |
| Database cylinder | `shape=cylinder3;whiteSpace=wrap;size=12;` |
| Diamond | `rhombus;whiteSpace=wrap;` |
| Ellipse | `ellipse;whiteSpace=wrap;` |
| Document | `shape=mxgraph.flowchart.document;` |
| Swimlane | `swimlane;startSize=30;` |
| Table/ERD | `shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;` |

## Style Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `rounded=1` | 0 or 1 | Rounded corners |
| `whiteSpace=wrap` | wrap | Text wrapping |
| `html=1` | 0 or 1 | Enable HTML in cell labels (`<b>`, `<font>`) |
| `fillColor=#hex` | Hex color | Background |
| `strokeColor=#hex` | Hex color | Border |
| `fontColor=#hex` | Hex color | Text |
| `fontFamily=Helvetica` | Font name | Font face |
| `fontSize=11` | Number | Font size |
| `fontStyle=1` | 1=bold, 2=italic, 4=underline | Font style (bitmask) |
| `strokeWidth=2` | Number | Border thickness |
| `dashed=1` | 0 or 1 | Dashed border |
| `dashPattern=5 3` | Space-separated | Dash pattern |
| `container=1` | 0 or 1 | Enable child containment |
| `collapsible=0` | 0 or 1 | Prevent collapse |
| `edgeStyle=orthogonalEdgeStyle` | Style name | Right-angle connectors |
| `jettySize=auto` | auto or number | Port spacing |

## Edge Routing

- Use `edgeStyle=orthogonalEdgeStyle` for clean right-angle connectors
- Space nodes at least 60px apart (prefer 200px horizontal / 120px vertical)
- Use `exitX`/`exitY` and `entryX`/`entryY` (0-1) to control connection sides
- Add waypoints when edges would overlap:

```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="300" y="150"/>
    <mxPoint x="300" y="250"/>
  </Array>
</mxGeometry>
```

## Containers

| Type | Style | Use case |
|------|-------|----------|
| Group (invisible) | `group;` | No visual border, no connections |
| Swimlane (titled) | `swimlane;startSize=30;` | Visible header, may have connections |
| Custom container | Add `container=1;pointerEvents=0;` | Any shape as container |

Children set `parent="containerId"` and use coordinates relative to the container.

## CLI Export

The draw.io desktop app supports command-line export:

```bash
# macOS
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -e -b 10 -o output.png input.drawio

# Linux
drawio -x -f svg -e -o output.svg input.drawio
```

Key flags: `-x` (export), `-f` (format: png/svg/pdf), `-e` (embed diagram XML), `-b` (border), `-s` (scale), `-t` (transparent).

PNG/SVG/PDF with `--embed-diagram` contain the full diagram XML, remaining editable in draw.io. Use double extensions: `name.drawio.png`.

## XML Well-formedness

- Never use `--` inside XML comments (illegal per XML spec)
- Escape attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Use unique `id` values for every cell
- When generating programmatically, prefix IDs with the diagram name to avoid collisions across diagrams on the same page
