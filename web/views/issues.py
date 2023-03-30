from django.shortcuts import render

from web.forms.issues import IssuesModelForm


def issues(request, project_id):

    form = IssuesModelForm()

    return render(request, 'issues/issues.html', {'form': form})
