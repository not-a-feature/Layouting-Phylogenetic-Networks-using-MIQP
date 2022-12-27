"""
Create Multiplot from Graph.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""
from matplotlib import pyplot as plt
from math import sqrt, ceil


def multiplot(graph_list, path=None):
    """
    Plots multiple trees with title in one figure.
    Input:
        graph_list: list of (Graphs, Title)
                            Graph: Graph object
                            Title: str, title of subplot
    """
    if len(graph_list) == 1:
        g, title = graph_list[0]
        g.plot(title=title, path=path)
        return

    # Create subplot
    ncols = ceil(sqrt(len(graph_list)))
    if (ncols**2) - len(graph_list) > ncols:
        nrows = ncols - 1
    else:
        nrows = ncols

    fig, axs = plt.subplots(nrows, ncols, figsize=(nrows * 6, ncols * 4))

    for i, (g, title) in enumerate(graph_list):
        for node_name in g.names():
            node = g.get_node(node_name)

            axs[i // ncols, i % ncols].text(node.posx, node.posy, node_name, fontsize=17)

            for edge in g.edges:
                if edge.hybrid:
                    color = "orange"
                else:
                    color = "black"

                parent = g.get_node(edge.source)
                child = g.get_node(edge.target)
                axs[i // ncols, i % ncols].plot(
                    [parent.posx, child.posx], [parent.posy, child.posy], color=color
                )

        axs[i // ncols, i % ncols].set_title(title)

    for ax in axs.flat:
        ax.label_outer()

    if path is not None:
        plt.savefig(path)
        return

    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()

    plt.show()
