from edge.generic import TreeHasher


def apply_patch():
    _original_hash_object = TreeHasher.hash_object

    # for leaf observable objects, use localhash() otherwise use the existing hash_object()
    def _new_hash_object(self, ao, visited):
        if ao.ty == 'obs' and ao.obj.observable_composition is None:
            complete = True
            hash_ = ao.localhash()
        else:
            complete, hash_ = _original_hash_object(self, ao, visited)
        return complete, hash_

    TreeHasher.hash_object = _new_hash_object
