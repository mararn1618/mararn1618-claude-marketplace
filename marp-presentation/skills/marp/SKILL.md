---
description: "Create Marp presentations from markdown"
---

# Marp Presentations Reference

## What is Marp?

Marp (Markdown Presentation Ecosystem) is a tool for creating presentation slide decks from Markdown files. It converts Markdown into HTML, PDF, or PowerPoint presentations with minimal configuration.

## Installation & Running

```bash
# Use npx (no installation required, recommended for one-shot conversions)
npx @marp-team/marp-cli slide.md

# Install globally via npm
npm install -g @marp-team/marp-cli

# Install via Homebrew (macOS)
brew install marp-cli
```

Requires Node.js v18 or later.

## Essential Syntax

### Front Matter

YAML front matter must be the first thing in the Markdown file, between triple dashes:

```yaml
---
marp: true
theme: default
paginate: true
header: 'My Presentation'
footer: 'Author Name | Date'
size: 16:9
backgroundColor: white
---
```

Common front matter options:
- `marp: true` - Enable Marp processing (required)
- `theme` - Theme name (default, gaia, uncover)
- `paginate` - Show page numbers (true/false)
- `header` - Text in header on all slides
- `footer` - Text in footer on all slides
- `size` - Aspect ratio (16:9, 4:3)
- `backgroundColor` - Background color
- `backgroundImage` - Background image or gradient

### Slide Separators

Use three dashes `---` on a line by itself to separate slides:

```markdown
# Slide 1

Content here

---

# Slide 2

More content
```

### Directives

**Global directives** (apply to all slides): Set in front matter or at document start.

**Local directives** (apply to current and following slides): Use within slide content.

**Scoped directives** (apply only to current slide): Prefix with underscore `_`.

```markdown
<!-- Global directive (affects all following slides) -->
<!-- theme: gaia -->

---

<!-- Local directive (affects this and following slides) -->
<!-- backgroundColor: #ffffff -->

# Slide 1

---

<!-- Scoped directive (affects only this slide) -->
<!-- _backgroundColor: #000000 -->
<!-- _color: #ffffff -->

# Slide 2 with black background

---

# Slide 3 (back to white background)
```

Common directives:
- `class` - CSS class name
- `color` - Text color
- `backgroundColor` - Background color
- `backgroundImage` - Background image
- `backgroundSize` - Background size (cover, contain, etc.)
- `paginate` - Enable/disable page numbers

### Speaker Notes

Use HTML comments for speaker notes (visible in presenter mode):

```markdown
# My Slide

Slide content here

<!--
Speaker notes go here. These are only visible in presenter mode.
You can write multiple lines.
-->
```

### Image Syntax & Sizing

Basic image with size control:

```markdown
![width:200px](image.jpg)
![height:300px](image.jpg)
![w:200px h:300px](image.jpg)
```

Background images:

```markdown
![bg](background.jpg)
![bg fit](background.jpg)
![bg contain](background.jpg)
![bg cover](background.jpg)
![bg left](image.jpg)
![bg right](image.jpg)
![bg left:33%](image.jpg)
```

Multiple backgrounds:

```markdown
![bg](bg1.jpg)
![bg](bg2.jpg)
```

Image filters:

```markdown
![bg brightness:0.5](image.jpg)
![bg blur:10px](image.jpg)
```

### Fitting Text

Use `<!-- fit -->` comment before headings to auto-scale text to fit the slide:

```markdown
<!-- fit -->
# This heading will auto-scale to fit
```

### Columns/Split Layouts

Define columns using HTML and custom CSS in front matter or style section:

```markdown
---
marp: true
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
---

<div class="columns">

<div>

## Column 1
Content for left column

</div>

<div>

## Column 2
Content for right column

</div>

</div>
```

### Built-in Themes

Marp includes three built-in themes:
- `default` - Clean, minimal design
- `gaia` - Modern, colorful theme
- `uncover` - Dark theme with reveal effect

```yaml
---
theme: gaia
---
```

## Export Commands

### HTML Export

```bash
# Basic HTML export
npx @marp-team/marp-cli slide.md

# HTML with custom output path
npx @marp-team/marp-cli slide.md -o output.html

# HTML with embedded assets
npx @marp-team/marp-cli slide.md --html
```

### PDF Export

```bash
# Export to PDF
npx @marp-team/marp-cli slide.md --pdf

# PDF with custom output path
npx @marp-team/marp-cli slide.md -o output.pdf
```

### PowerPoint Export

```bash
# Export to PPTX
npx @marp-team/marp-cli slide.md --pptx

# PPTX with custom output path
npx @marp-team/marp-cli slide.md -o output.pptx
```

### Image Export

```bash
# Export as PNG images (one per slide)
npx @marp-team/marp-cli --images png slide.md

# Export as JPEG images
npx @marp-team/marp-cli --images jpeg slide.md
```

### Watch Mode

```bash
# Auto-rebuild on file changes
npx @marp-team/marp-cli slide.md --watch
```

### Server Mode

```bash
# Start local server with live preview
npx @marp-team/marp-cli -s slide.md

# Access different formats via query strings:
# http://localhost:8080/slide.md?pdf
# http://localhost:8080/slide.md?pptx
```

## Best Practices

1. **Keep text minimal**: Use bullet points, not paragraphs. One idea per slide.

2. **Use visual hierarchy**:
    - One H1 heading per slide
    - Use H2/H3 for subheadings
    - Limit bullet nesting to 2 levels

3. **Leverage images**: Use background images and split layouts for visual interest.

4. **Use tables for structured data**: Markdown tables render well in Marp.

5. **Consistent spacing**: Use blank lines between elements for better parsing.

6. **Test early**: Export to your target format (PDF/PPTX) early to check rendering.

7. **One concept per slide**: Split complex ideas across multiple slides.

8. **Use speaker notes**: Add context for presenters without cluttering slides.

9. **Contrast matters**: Ensure text is readable against backgrounds.

10. **Font sizing**: Use `<!-- fit -->` sparingly; manually control sizes with heading levels.

## Example Slide Deck

```markdown
---
marp: true
theme: default
paginate: true
footer: 'My Presentation | 2026'
---

# Welcome to Marp

Creating presentations from Markdown

---

## Why Marp?

- Write slides in plain text
- Version control friendly
- Fast and efficient
- Multiple export formats

<!--
Remember to mention Git integration and collaboration benefits
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Key Features

---

## Image Support

![width:600px](diagram.png)

Easy image sizing and placement

---

![bg right:40%](photo.jpg)

## Split Layouts

Content on the left
Image background on the right

---

<!-- fit -->
# Thank You

Questions?
```

## References

- [Marp Official Site](https://marp.app/)
- [Marp CLI GitHub](https://github.com/marp-team/marp-cli)
- [Marpit Framework Documentation](https://marpit.marp.app/)
- [Image Syntax Documentation](https://marpit.marp.app/image-syntax)
- [Directives Documentation](https://marpit.marp.app/directives)
