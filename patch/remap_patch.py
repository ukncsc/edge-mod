import edge.remap as remap


# fixes a soltra bug. registered as MOD#20
def remap_tgt(src, maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n, 'potential_coas'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_packages'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_exploit_targets'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)

    return n


def remap_ind(src, maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n, 'composite_indicator_expression'):
        ref.idref = remap.maybe_remap(ref.idref, maptable)
    for ref in remap.coalesce(n, 'indicated_ttps'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'suggested_coas'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_indicators'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'observables'):
        ref.idref = remap.maybe_remap(ref.idref, maptable)

    return n


def apply_patch():
    remap.REMAP_DISPATCH['tgt'] = remap_tgt
    remap.REMAP_DISPATCH['ind'] = remap_ind
