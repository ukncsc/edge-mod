from edge.models import StixBacklink
from mongoengine import DoesNotExist
from clippy.models import CLIPPY_TYPES
from edge.generic import EdgeObject, EdgeError


class BackEdgeGenerator(object):

    @staticmethod
    def gather_back_edges(edgetable, load_by_id):
        ax = []
        for idref, type_ in edgetable.iteritems():
            try:
                eo_ = load_by_id(idref)
            except EdgeError:
                reference_title = '(external reference)'
                eo_ = None
            else:
                reference_title = eo_.summary.get('title', '(untitled)')

            ax.append({
                'ty': type_,
                'id_': idref,
                'type': CLIPPY_TYPES[type_],
                'depth': 1,
                'title': reference_title,
                'is_external': eo_ is None,
            })
        return ax

    @staticmethod
    def _generate_back_table(edge_object):
        try:
            backtable = StixBacklink.objects.get(id=edge_object.id_).edges

        except DoesNotExist:
            backtable = {}

        return backtable


    @staticmethod
    def retrieve_back_edges(edge_object, user_filters):

        backtable = BackEdgeGenerator._generate_back_table(edge_object)

        user_loader = lambda idref: EdgeObject.load(idref, user_filters)

        return BackEdgeGenerator.gather_back_edges(backtable, load_by_id=user_loader)

