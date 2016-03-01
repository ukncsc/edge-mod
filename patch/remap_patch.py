import edge.remap as remap

#fixes a soltra bug. registered as MOD#20
def remap_tgt(src,maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n,'potential_coas'):
        ref.item.idref = remap.maybe_remap(ref.item.idref,maptable)
    for ref in remap.coalesce(n,'related_packages'):
        ref.item.idref = remap.maybe_remap(ref.item.idref,maptable)
    for ref in remap.coalesce(n,'related_exploit_targets'):
        ref.item.idref = remap.maybe_remap(ref.item.idref,maptable)

    return n


def apply_patch():
    remap.REMAP_DISPATCH['tgt'] = remap_tgt
