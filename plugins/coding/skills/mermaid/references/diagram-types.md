# Mermaid Diagram Types

Canonical lookup of every Mermaid diagram type, its keyword, use cases, and a link to the official, always-current syntax documentation. Read this table to pick the right type, then read the linked official page for exact syntax before generating code.

Official docs base: `https://mermaid.ai/open-source/syntax/<chart_type>.html`

## General Syntax

Before diving into a specific diagram type, read the [general syntax reference](https://mermaid.ai/open-source/intro/syntax-reference.html) for diagram structure, frontmatter configuration, layout/look selection, and words that break diagrams (`end`, nested nodes).

## Diagram Types

| Type | Keyword | Use Cases | Official Docs |
| --- | --- | --- | --- |
| Flowchart | `flowchart` / `graph` | Processes, decisions, steps, workflows | [flowchart.html](https://mermaid.ai/open-source/syntax/flowchart.html) |
| Swimlanes | `swimlane` | Cross-team processes, ownership, handoffs, approval flows (v11.16.0+) | [swimlanes.html](https://mermaid.ai/open-source/syntax/swimlanes.html) |
| Sequence Diagram | `sequenceDiagram` | Interactions, messaging, API calls, temporal ordering | [sequenceDiagram.html](https://mermaid.ai/open-source/syntax/sequenceDiagram.html) |
| Class Diagram | `classDiagram` | Class structure, inheritance, associations, methods | [classDiagram.html](https://mermaid.ai/open-source/syntax/classDiagram.html) |
| State Diagram | `stateDiagram` | State machines, state transitions, lifecycle | [stateDiagram.html](https://mermaid.ai/open-source/syntax/stateDiagram.html) |
| ER Diagram | `erDiagram` | Database design, entity relationships, schema | [entityRelationshipDiagram.html](https://mermaid.ai/open-source/syntax/entityRelationshipDiagram.html) |
| User Journey | `journey` | User experience flows, satisfaction mapping | [userJourney.html](https://mermaid.ai/open-source/syntax/userJourney.html) |
| Gantt | `gantt` | Project planning, timelines, scheduling | [gantt.html](https://mermaid.ai/open-source/syntax/gantt.html) |
| Pie Chart | `pie` | Proportions, distributions, donut charts | [pie.html](https://mermaid.ai/open-source/syntax/pie.html) |
| Quadrant Chart | `quadrantChart` | Four-quadrant analysis, prioritization | [quadrantChart.html](https://mermaid.ai/open-source/syntax/quadrantChart.html) |
| Requirement Diagram | `requirementDiagram` | Requirements traceability, verification | [requirementDiagram.html](https://mermaid.ai/open-source/syntax/requirementDiagram.html) |
| Use Case Diagram | `usecase-beta` | Actor-system interactions, use cases (12.0.0+) | [usecase.html](https://mermaid.ai/open-source/syntax/usecase.html) |
| GitGraph | `gitGraph` | Branches, merges, commit history, versions | [gitgraph.html](https://mermaid.ai/open-source/syntax/gitgraph.html) |
| C4 Diagram | `C4Context` / `C4Container` / `C4Component` / `C4Dynamic` | System architecture (C4 model), contextual/containers/components | [c4.html](https://mermaid.ai/open-source/syntax/c4.html) |
| Mindmap | `mindmap` | Hierarchical structures, knowledge graphs, brainstorming | [mindmap.html](https://mermaid.ai/open-source/syntax/mindmap.html) |
| Timeline | `timeline` | Historical events, milestones, chronologies | [timeline.html](https://mermaid.ai/open-source/syntax/timeline.html) |
| ZenUML | `zenuml` | Sequence diagrams in code-style syntax | [zenuml.html](https://mermaid.ai/open-source/syntax/zenuml.html) |
| Sankey | `sankey` | Flow, conversions, resource distribution | [sankey.html](https://mermaid.ai/open-source/syntax/sankey.html) |
| XY Chart | `xychart-beta` | Line charts, bar charts, quantitative data | [xyChart.html](https://mermaid.ai/open-source/syntax/xyChart.html) |
| Block Diagram | `block-beta` | System components, modules, structural blocks | [block.html](https://mermaid.ai/open-source/syntax/block.html) |
| Packet | `packet-beta` | Network protocols, data structures, byte layout | [packet.html](https://mermaid.ai/open-source/syntax/packet.html) |
| Kanban | `kanban` | Task management, workflows, board columns | [kanban.html](https://mermaid.ai/open-source/syntax/kanban.html) |
| Architecture | `architecture-beta` | System architecture, service dependencies | [architecture.html](https://mermaid.ai/open-source/syntax/architecture.html) |
| Radar | `radar-beta` | Multi-dimensional comparison, capability scoring | [radar.html](https://mermaid.ai/open-source/syntax/radar.html) |
| Event Modeling | `eventmodeling-beta` | Event-sourced systems, event streams | [eventmodeling.html](https://mermaid.ai/open-source/syntax/eventmodeling.html) |
| Treemap | `treemap-beta` | Hierarchical data visualization, proportion | [treemap.html](https://mermaid.ai/open-source/syntax/treemap.html) |
| Venn | `venn` | Set intersection, overlap, grouping | [venn.html](https://mermaid.ai/open-source/syntax/venn.html) |
| Ishikawa | `ishikawa-beta` | Cause-and-effect (fishbone) diagrams, root cause | [ishikawa.html](https://mermaid.ai/open-source/syntax/ishikawa.html) |
| Wardley | `wardley` | Strategic mapping, value-chain evolution | [wardley.html](https://mermaid.ai/open-source/syntax/wardley.html) |
| Cynefin | `cynefin` | Decision frameworks, sense-making contexts | [cynefin.html](https://mermaid.ai/open-source/syntax/cynefin.html) |
| TreeView | `treeview-beta` | Expandable tree hierarchies, file/folder views | [treeView.html](https://mermaid.ai/open-source/syntax/treeView.html) |
| Railroad | `railroad-ebnf-beta` / `railroad-abnf-beta` / `railroad-peg-beta` / `railroad-beta` | Grammar diagrams, syntax notation (EBNF/ABNF/PEG) | [railroad.html](https://mermaid.ai/open-source/syntax/railroad.html) |

## Configuration & Styling

| Topic | Official Docs |
| --- | --- |
| Global Configuration | [configuration.html](https://mermaid.ai/open-source/config/configuration.html) |
| Directives (diagram-level) | [directives.html](https://mermaid.ai/open-source/config/directives.html) |
| Theming (colors, themes, looks) | [theming.html](https://mermaid.ai/open-source/config/theming.html) |
| Math (LaTeX support) | [math.html](https://mermaid.ai/open-source/config/math.html) |
| Layouts (direction, spacing) | [layouts.html](https://mermaid.ai/open-source/config/layouts.html) |

## Notes

- **Agentflow** (`agentflow`) exists in the Mermaid source but is deliberately unlisted in the official sidebar while beta. Excluded from this skill.
- Diagrams marked with a `🔥` in the official sidebar are newer/experimental additions. The `-beta` keyword suffix on several types above reflects their current maturity stage.
- When the user names a diagram type that does not exist, check this table. If absent, it is not a supported Mermaid diagram type.
