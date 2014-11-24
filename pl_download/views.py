from django.http import HttpResponse
from pl_download.models import DataFileManager


def test_fetch(request):
    result = DataFileManager.fetch_new_files_task.delay()
    return HttpResponse("Downloaded file: " + str(result.get()))
