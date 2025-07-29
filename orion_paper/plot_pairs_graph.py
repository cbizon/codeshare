import networkx as nx
import matplotlib.pyplot as plt
import argparse

# Define sources to exclude
EXCLUDE = [
    "litcoin", "yeast", "costanza", "old_ubergraph",
    "string-db-human", "biolink", "chebiprops", "mondoprops", "ubergraphnonredundant"
]

def should_exclude(source):
    source_lower = source.lower()
    return any(ex in source_lower for ex in EXCLUDE)

def main():
    parser = argparse.ArgumentParser(description="Visualize knowledge source network from pairs.txt")
    parser.add_argument('--layout', choices=['spring', 'kamada_kawai', 'circular', 'shell', 'spectral'], default='circular', help='Graph layout to use')
    args = parser.parse_args()

    edges_post = []
    edges_pre = []
    with open("pairs.txt", "r") as f:
        header = next(f)  # Skip header
        for line in f:
            if line.strip() and not line.startswith("//"):
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    src, tgt, pre, post = parts[:4]
                    if should_exclude(src) or should_exclude(tgt):
                        continue
                    try:
                        pre_val = int(pre)
                        post_val = int(post)
                    except ValueError:
                        continue
                    if pre_val > 0:
                        edges_pre.append((src, tgt))
                    if post_val > 0:
                        edges_post.append((src, tgt))

    G_pre = nx.Graph()
    G_pre.add_edges_from(edges_pre)
    G_post = nx.Graph()
    G_post.add_edges_from(edges_post)

    layouts = {
        'spring': nx.spring_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
        'circular': nx.circular_layout,
        'shell': nx.shell_layout,
        'spectral': nx.spectral_layout
    }
    layout_func = layouts[args.layout]
    # Use the union of nodes and all edges for consistent layout
    all_nodes = set(G_pre.nodes) | set(G_post.nodes)
    all_edges = set(G_pre.edges) | set(G_post.edges)
    G_all = nx.Graph()
    G_all.add_nodes_from(all_nodes)
    G_all.add_edges_from(all_edges)
    if args.layout == 'spring':
        pos = layout_func(G_all, seed=42)
    else:
        pos = layout_func(G_all)

    # Build edge alpha values for (a)
    edge_alpha = {}
    with open("pairs.txt", "r") as f:
        header = next(f)
        for line in f:
            if line.strip() and not line.startswith("//"):
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    src, tgt, pre, post = parts[:4]
                    if should_exclude(src) or should_exclude(tgt):
                        continue
                    try:
                        pre_val = int(pre)
                        post_val = int(post)
                    except ValueError:
                        continue
                    if pre_val > 0 and post_val > 0:
                        alpha = min(1.0, pre_val / post_val) if post_val > 0 else 1.0
                        edge_alpha[(src, tgt)] = alpha
                    elif pre_val > 0:
                        edge_alpha[(src, tgt)] = 1.0

    plt.figure(figsize=(12, 6))
    # Draw (a) with edge alpha
    plt.subplot(1, 2, 1, aspect='equal')
    edges = list(G_pre.edges())
    alphas = [edge_alpha.get(edge, 1.0) for edge in edges]
    nx.draw_networkx_nodes(G_pre, pos, node_size=700, node_color='lightblue')
    nx.draw_networkx_labels(G_pre, pos, font_size=10)
    for i, edge in enumerate(edges):
        nx.draw_networkx_edges(G_pre, pos, edgelist=[edge], edge_color='gray', alpha=alphas[i])
    plt.title(f"(a) Knowledge Source Network (Pre > 0)", pad=20)
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    # Draw (b) as before
    plt.subplot(1, 2, 2, aspect='equal')
    nx.draw(G_post, pos, with_labels=True, node_size=700, node_color='lightblue', edge_color='gray', font_size=10)
    plt.title(f"(b) Knowledge Source Network (Post > 0)", pad=20)
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()
