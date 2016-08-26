from clippy.models import CLIPPY_TYPES
from edge.generic import EdgeError


class EdgeGenerator(object):

    @staticmethod
    def gather_edges(queue, depth_limit, load_by_id, current_depth=0):
        if current_depth == depth_limit:
            return []

        ax = []
        for ref in queue:
            try:
                eo = load_by_id(ref.id_)
            except EdgeError:
                reference_title = '(external reference)'
                eo = None
            else:
                reference_title = eo.summary.get('title', '(untitled)')
            if eo:
                if eo.ty == 'obs':
                    if eo.summary["type"] == "ObservableComposition":
                        ax.extend(EdgeGenerator.gather_edges(eo.edges, depth_limit, load_by_id, current_depth))

            depth_viz = '' * current_depth
            ax.append({
                'type' : '%s%s' % (depth_viz, CLIPPY_TYPES[ref.ty]),
                'ty' : ref.ty,
                'id_' : ref.id_,
                'title' : reference_title,
                'is_external' : eo is None,
                'depth' : current_depth,
            })

            if eo:
                ax.extend(EdgeGenerator.gather_edges(eo.edges, depth_limit, load_by_id, current_depth+1))

        return ax
