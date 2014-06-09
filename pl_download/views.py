from django.http import HttpResponse
from pl_download.models import fetch_new_files


def test_fetch(request):
    result = fetch_new_files.delay()
    return HttpResponse("Downloaded file: " + str(result.get()))
