import json
from pyramid.view import view_config

from . import git


@view_config(route_name='home', renderer='templates/mytemplate.mako')
def my_view(request):
    return {'project': 'Git Ng Web'}


def get_projects_from_settings(request):
    settings = request.registry.settings
    projects = []
    lis = settings.get('git_projects').split('\n')
    index = 1
    for line in lis:
        if not line:
            continue
        name, path = json.loads(line)
        projects.append({
            'id': index,
            'name': name,
            'path': path,
        })
        index += 1
    return projects


@view_config(route_name='projects', renderer='json')
def projects(request):
    data = []
    lis = get_projects_from_settings(request)
    for project in lis:
        dic = {
            'id': project['id'],
            'name': project['name'],
        }
        dic.update(git.Git(project['path']).get_branches())
        data.append(dic)

    return data
