from django.http import HttpResponse
from pl_download.models import DataFileManager
from django.http import HttpResponseForbidden
from django.http import Http404


def test_fetch(request):
    #Validate User Permissions
    if request.user.is_anonymous():
        raise Http404("You do not have admin permissions to this site. Please contact your page administrator.")
    else:
        result = DataFileManager.fetch_new_files.delay()
        return HttpResponse("Downloaded file: " + str(result.get()))
