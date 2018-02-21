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
    index = 0
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


def get_project(request, project_id):
    lis = get_projects_from_settings(request)
    for project in lis:
        if project['id'] == project_id:
            return project


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


@view_config(route_name='logs', renderer='json')
def logs(request):
    project_id = int(request.matchdict['project_id'])
    branch = request.GET.get('branch')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])
    branches = gitobj.get_branches()
    if branch not in sum(branches.values(), []):
        raise Exception('TODO')
    return gitobj.get_logs(branch)


@view_config(route_name='diff', renderer='json')
def diff(request):
    project_id = int(request.matchdict['project_id'])
    h = request.matchdict['hash']
    if not h.isalnum():
        # TODO: validate correctly hash
        raise Exception('TODO')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])
    return gitobj.get_diff(h)
