"""MathSense-ID Knowledge Graph module.

Menyediakan:
- build_knowledge_graph: membangun networkx.DiGraph dari entities dan relations
- visualize_kg: visualisasi Knowledge Graph 300 DPI untuk publikasi ilmiah
- ascii_kg: visualisasi ASCII + tabel untuk fallback/debugging
- build_equation: re-export dari equation_templates untuk kemudahan integrasi
"""
from typing import List, Any, Optional, Dict
import textwrap
import networkx as nx

try:
    from equation_templates import build_equation
except ImportError:
    try:
        from src.equation_templates import build_equation
    except ImportError:
        build_equation = None


def build_knowledge_graph(entities: List[Any], relations: List[Any]) -> nx.DiGraph:
    """Membangun NetworkX DiGraph dari daftar entities dan relations.

    Mendukung ExtractedEntity/ExtractedRelation (dataclass) maupun dictionary.
    """
    G = nx.DiGraph()

    for e in entities:
        if hasattr(e, "text"):
            text = e.text
            role = e.role
            value = e.value
            unit = e.unit
            confidence = e.confidence
        elif isinstance(e, dict):
            text = e.get("text", "")
            role = e.get("role", "")
            value = float(e.get("value", 0.0))
            unit = e.get("unit", "")
            confidence = float(e.get("confidence", 1.0))
        else:
            continue

        G.add_node(
            text,
            role=role,
            value=value,
            unit=unit,
            confidence=confidence
        )

    for r in relations:
        if hasattr(r, "head"):
            head = r.head
            tail = r.tail
            relation = r.relation
            operation = r.operation
            confidence = r.confidence
        elif isinstance(r, dict):
            head = r.get("head", "")
            tail = r.get("tail", "")
            relation = r.get("relation", "")
            operation = r.get("operation", "?")
            confidence = float(r.get("confidence", 1.0))
        else:
            continue

        G.add_edge(
            head,
            tail,
            relation=relation,
            operation=operation,
            confidence=confidence
        )

    return G


def ascii_kg(G: nx.DiGraph) -> str:
    """Representasi ASCII dan tabel dari Knowledge Graph."""
    lines = ["=== Knowledge Graph ASCII Representation ==="]
    lines.append(f"Nodes ({G.number_of_nodes()}):")
    for node, data in G.nodes(data=True):
        role = data.get("role", "-")
        val = data.get("value", "-")
        unit = data.get("unit", "-")
        conf = data.get("confidence", 1.0)
        lines.append(f"  [{node}] -> role: {role}, value: {val}, unit: {unit}, conf: {conf:.2f}")

    lines.append(f"\nEdges ({G.number_of_edges()}):")
    for u, v, data in G.edges(data=True):
        rel = data.get("relation", "-")
        op = data.get("operation", "-")
        conf = data.get("confidence", 1.0)
        lines.append(f"  [{u}] ---> ({rel} [op: {op}], conf: {conf:.2f}) ---> [{v}]")

    return "\n".join(lines)


def visualize_kg(
    G: nx.DiGraph,
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    dpi: int = 300,
) -> Any:
    """Visualisasi Knowledge Graph kualitas publikasi (300 DPI).

    Menggunakan styling profesional dengan pembagian warna berdasarkan role:
    - quantity: biru lembut (#E0F2FE, border #0284C7)
    - price: hijau lembut (#DCFCE7, border #16A34A)
    - variable: kuning amber (#FEF3C7, border #D97706)
    - subject: ungu lembut (#EDE9FE, border #7C3AED)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=dpi)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("#FAFAFA")

    nodes = list(G.nodes())
    n_nodes = len(nodes)

    # Posisi node
    pos: Dict[str, tuple] = {}
    if n_nodes == 2:
        pos[nodes[0]] = (0.22, 0.5)
        pos[nodes[1]] = (0.78, 0.5)
    elif n_nodes == 3:
        pos[nodes[0]] = (0.18, 0.65)
        pos[nodes[1]] = (0.82, 0.65)
        pos[nodes[2]] = (0.50, 0.25)
    elif n_nodes == 4:
        pos[nodes[0]] = (0.2, 0.7)
        pos[nodes[1]] = (0.8, 0.7)
        pos[nodes[2]] = (0.2, 0.3)
        pos[nodes[3]] = (0.8, 0.3)
    else:
        # Spiral / circular fallback untuk n > 4
        import math
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / max(1, n_nodes)
            pos[node] = (0.5 + 0.35 * math.cos(angle), 0.5 + 0.32 * math.sin(angle))

    # Skema warna role
    color_palette = {
        "quantity": {"face": "#E0F2FE", "edge": "#0284C7", "text": "#0369A1", "badge": "Quantity"},
        "price": {"face": "#DCFCE7", "edge": "#16A34A", "text": "#15803D", "badge": "Price"},
        "variable": {"face": "#FEF3C7", "edge": "#D97706", "text": "#B45309", "badge": "Variable"},
        "subject": {"face": "#EDE9FE", "edge": "#7C3AED", "text": "#6D28D9", "badge": "Subject"},
    }
    default_color = {"face": "#F1F5F9", "edge": "#64748B", "text": "#334155", "badge": "Entity"}

    box_w = 0.25
    box_h = 0.17

    # Gambar edges terlebih dahulu agar panah berada di bawah kotak
    for u, v, data in G.edges(data=True):
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]

        # Draw arrow
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#475569",
                lw=2.2,
                shrinkA=box_w * 220,
                shrinkB=box_w * 220,
                mutation_scale=16,
            ),
        )

        # Label pada edge
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + 0.05
        rel = data.get("relation", "")
        op = data.get("operation", "")
        edge_label = f"{rel}\n[op: {op}]" if op else rel

        ax.text(
            mx,
            my,
            edge_label,
            ha="center",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color="#1E293B",
            bbox=dict(
                boxstyle="round,pad=0.35",
                facecolor="#FFFFFF",
                edgecolor="#94A3B8",
                linewidth=1.2,
                alpha=0.95,
            ),
        )

    # Gambar nodes
    for node in nodes:
        x, y = pos[node]
        data = G.nodes[node]
        role = data.get("role", "entity")
        val = data.get("value", None)
        unit = data.get("unit", "")
        conf = data.get("confidence", 1.0)

        theme = color_palette.get(role, default_color)

        # Kotak node rounded
        rect = patches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2),
            box_w,
            box_h,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor=theme["face"],
            edgecolor=theme["edge"],
            linewidth=2.0,
            zorder=3,
        )
        ax.add_patch(rect)

        # Text di dalam node dengan wrapping untuk label panjang
        wrapped_node = textwrap.fill(str(node), width=16)
        header_text = f'"{wrapped_node}"'
        val_str = f"{int(val)}" if isinstance(val, (int, float)) and float(val).is_integer() else f"{val}"
        detail_text = f"Role: {theme['badge']}\nVal: {val_str} {unit} (c={conf:.1f})"

        ax.text(
            x,
            y + 0.025,
            header_text,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=theme["text"],
            zorder=4,
        )
        ax.text(
            x,
            y - 0.038,
            detail_text,
            ha="center",
            va="center",
            fontsize=8.5,
            color="#334155",
            zorder=4,
        )

    # Judul dan metadata
    if title:
        ax.text(
            0.5,
            0.96,
            title,
            ha="center",
            va="top",
            fontsize=13,
            fontweight="bold",
            color="#0F172A",
        )
    if subtitle:
        ax.text(
            0.5,
            0.90,
            subtitle,
            ha="center",
            va="top",
            fontsize=9.5,
            fontstyle="italic",
            color="#475569",
        )

    # Legend / footer info
    ax.text(
        0.5,
        0.03,
        "MathSense-ID Knowledge Graph Representation (300 DPI)",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#94A3B8",
    )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    if output_path:
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return output_path

    return fig
