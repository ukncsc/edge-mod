import traceback
import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from edge.generic import EdgeObject, EdgeError
from crashlog.models import save
from adapters.certuk_mod.catalog.generate_snort import generate_snort


@login_required
def observable_extract(request, type, obs_type, id_):
    revision = "latest"
    try:
        eo = EdgeObject.load(id_, request.user.filters(), revision=revision)
    except EdgeError as e:
        e.message += " with revision %s" % revision
        save('catalog.downloads', e.message, traceback.format_exc())
        raise Http404()

    def text_writer(value, obs_type_in):
        if obs_type_in == obs_type or obs_type == "all":
            return value + os.linesep
        return ""

    def snort_writer(value, obs_type_in):
        if obs_type_in == obs_type or obs_type == "all":
            snort_val = generate_snort([value], obs_type_in, id_.split(':', 1)[1].split('-', 1)[1])
            if snort_val:
                return snort_val  + os.linesep
        return ""

    def not_implemented_writer(value, obs_type_in):
        return ""

    result = ""
    if type == "text":
        writer = text_writer
    elif type == "SNORT":
        writer = snort_writer
    else:
        writer = not_implemented_writer
        result = "%s not implemented" % type

    stack = [id_]
    history = {}
    while stack:
        node_id = stack.pop()
        if node_id in history:
            continue

        try:
            eo = EdgeObject.load(node_id, request.user.filters(), revision=revision)
        except EdgeError:
            continue

        for edge in eo.edges:
            stack.append(edge.id_)

        if eo.ty != 'obs':
            continue

        try:
            obs = EdgeObject.load(node_id, request.user.filters(), revision=revision)
        except EdgeError:
            continue

        if obs.apidata.has_key("observable_composition"):
            continue

        result += writer(obs.summary['value'], obs.summary['type'])

    response = HttpResponse(content_type='text/txt')
    response['Content-Disposition'] = 'attachment; filename="%s_%s_%s.txt"' % (type, obs_type, id_)
    response.write(result)
    return response
