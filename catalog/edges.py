from edge.generic import EdgeError


class EdgeGenerator(object):
    @staticmethod
    def gather_edges(queue, load_by_id):

        history = set()

        ax = []
        for ref in queue:
            try:
                eo = load_by_id(ref.id_)
            except EdgeError:
                eo = None

            if ref.id_ in history:
                continue

            history.add(ref.id_)
            ax.append({
                'ty': ref.ty,
                'id_': ref.id_,
                'is_external': eo is None
            })

            if eo and eo.summary.get('type', None) == "ObservableComposition":
                queue.extend(eo.edges)

        return ax
