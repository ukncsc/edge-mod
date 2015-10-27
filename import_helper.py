
try:
    # In the cert-uk refactor, EdgeObject has been moved...
    from edge.edge_object import EdgeObject
except ImportError:
    from edge.generic import EdgeObject

