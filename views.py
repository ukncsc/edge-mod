from itertools import chain
from StringIO import StringIO
import re
import urllib2

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from edge import IDManager
from edge.edge_object import EdgeObject
from users.decorators import superuser_or_staff_role
from edge import LOCAL_ALIAS, LOCAL_NAMESPACE
#  from xforms import package_from_csv
from stix.core.stix_header import STIXHeader
from taxii.models import Upload
from uploads.jobs import process_upload

from catalog.views import ajax_load_catalog

objectid_matcher = re.compile(
    # {STIX/ID Alias}:{type}-{GUID}
    r".*/([a-z\d-]+:[a-z\d]+-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})/?$",
    re.IGNORECASE  # | re.DEBUG
)


@login_required
def review(request):
    referrer = urllib2.unquote(request.META.get("HTTP_REFERER", ""))
    match = objectid_matcher.match(referrer)
    if match is not None and len(match.groups()) == 1:
        id_ = match.group(1)
        root = EdgeObject.load(id_)
        pkgid = IDManager().get_new_id(prefix="package")
        package, contents = root.capsulize(pkgid, enable_bfs=True)
        return render(request, "publisher_review.html", {
            "root_id": id_,
            "root_type": root.ty,
            "package": package,
        })
    else:
        return redirect(reverse("publisher_not_found"))


@login_required
def not_found(request):
    return render(request, "publisher_not_found.html", {})


'''
def do_upload(request):

    namespace_data = request.POST['namespace_data'].strip()
    namespace_alias = request.POST['namespace_alias'].strip()
    head_title = request.POST.get('head_title','')
    head_description = request.POST.get('head_description','')
    enable_grouping = request.POST.get('enable_grouping') == 'true'

    settings = {}
    settings['namespace_data'] = namespace_data
    settings['namespace_alias'] = namespace_alias
    if head_title:
        settings['head_title'] = head_title
    if head_description:
        settings['head_description'] = head_description
    settings['enable_grouping'] = enable_grouping

    settings_and_data = "\n".join(chain(
        ("%s=%s" %(key,val) for key,val in settings.iteritems()),
        [request.POST['csvdata']],
    ))

    csvstream = StringIO(settings_and_data)

    packagefd = package_from_csv(csvstream)

    rawdata = packagefd.read()

    request.session['csvind_output'] = rawdata
    request.session['csvind_id'] = str(len(rawdata)) #XXX
    return redirect(reverse('csvind_review'))


@login_required
def review(request):
    request.breadcrumbs([ ("CSV Indicator Review",""), ])
    return render(request,'csvind-review.html',{
        'package' : request.session['csvind_output'],
        'package_id' : request.session['csvind_id'],
        'publish_uri' : reverse('csvind_publish'),
    })


@login_required
def upload(request):
    if request.method == 'POST':
        return do_upload(request)

    request.breadcrumbs([ ("CSV Indicators",""), ])
    return render(request,'csvind-upload.html',{
        'ajax_uri' : '', # reverse('trustgroups_ajax'),
        'namespace_data' : LOCAL_NAMESPACE,
        'namespace_alias' : LOCAL_ALIAS,
    })


@login_required
def publish(request):
    if request.method != 'POST':
        raise Exception('expected POST')

    expected_package_id = request.POST['package_id'].strip()
    if expected_package_id != request.session['csvind_id']:
        raise Exception('The CSV data was modified by another request.  Publish Aborted.')

    gfs_content = Upload.new_file()
    data = request.session['csvind_output']
    #thash = hashlib.sha1(request.session['csvind_output'])
    gfs_content.write(data)
    gfs_content.close()

    newpkg = Upload(
        state = 'new',
        file_id = gfs_content._id,
        bytes = len(data),
        uploaded_by = request.user.id,
        binding = 'urn:stix.mitre.org:xml:1.1.1',
        filename = 'csvind',
    ).save()

    process_upload.delay(newpkg.id)

    return redirect(reverse('uploads'))
'''
