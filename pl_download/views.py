from django.http import HttpResponse
from pl_download.models import DataFile, fetch_new_file


def test_fetch(request):
    result = fetch_new_file.delay()
    return HttpResponse("Downloaded file " + result.get())