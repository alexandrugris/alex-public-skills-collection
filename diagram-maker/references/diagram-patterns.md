# Diagram patterns and palette

Use these values as diagram-specific applications of AG Style. The canonical tokens are in alexandru-style/brand/references/tokens.css and the visual rules are in alexandru-style/brand/references/style-spec.md. If the sibling style skill is unavailable, these values are sufficient.

## Core palette

| Role | Value | Use |
|---|---|---|
| Paper | #FBFAF7 | Main canvas and label backing |
| Warm panel | #F2EEE4 | Group or subsystem background |
| Alternate panel | #F7F4ED | Secondary zone |
| Ink | #30332F | Body labels and primary lines |
| Deep ink | #292B28 | Main component titles |
| Muted text | #686B64 | Supporting descriptions |
| Hairline | #D8D4CA | Secondary borders and separators |
| Burgundy | #8D2829 | Primary emphasis or one important path per visual block |
| Green | #415649 | Trust, identity, or human approval when that distinction exists |

Use burgundy sparingly. For diagrams that need more than two semantic categories, add only muted, low-saturation colors with light fills and darker text. A practical extension is a soft slate blue (#EAF1F7 fill, #41657F stroke/text) for runtime or infrastructure boundaries, and a pale ochre (#F5EEDC fill, #80622F stroke/text) for external tools or policy layers. Use color consistently and explain it in a small key. Never use color as the sole carrier of meaning.

## Components and boundaries

- Keep the canvas warm off-white. Use ink for headings and body text; use Inter or a system sans-serif for labels and IBM Plex Mono or a system monospace for code identifiers.
- Use regular-weight titles and readable supporting type. Keep all essential text comfortably readable at the output's intended size; enlarge the diagram or split it when labels become cramped.
- Prefer square or gently rounded rectangles with thin solid borders, restrained pale fills, and no shadows. Reserve a slightly stronger border or top rule for the primary component.
- Use solid enclosing outlines for application or deployment boundaries. A dashed outline is allowed for a trust boundary, network edge, or explicitly conditional group; label it. Do not use dashed lines as decoration.
- Draw direct synchronous calls as solid arrows. Use dashed arrows only for asynchronous, optional, or event-driven flows, and explain the convention in a key when multiple meanings occur. Use a distinct accent path only when the flow is materially important, such as explicit approval or a return path.
- Use short noun phrases for nodes and verb or protocol labels for edges. Explain acronyms once when the audience may not know them.

## Mermaid

Use Mermaid when the graph is small enough that its renderer can keep the reading order and edge labels clear. Put the source in a fenced Mermaid block or a .mmd file. Define a restrained theme with the palette above and apply classes to distinguish only meaningful categories. Avoid excessive subgraphs, labels on every edge, and layout workarounds that make the source hard to edit. When the rendered result is crowded or important connectors need manual routing, move the presentation version to SVG and retain Mermaid as an optional structural source.

## SVG

Use a responsive viewBox, a warm paper background, native SVG text, and explicit dimensions when needed for print. Group related nodes and their labels with `<g>`; use reusable marker definitions for arrowheads. Keep connector paths behind nodes and use paper-backed text for edge labels. Add a top-level `<title>` and `<desc>`; ensure text and strokes have sufficient contrast. Keep the file self-contained and editable in a vector editor.
