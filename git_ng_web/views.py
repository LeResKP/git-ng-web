from collections import defaultdict
import json
from pyramid.view import view_config

from . import git_helper as git

from git import Repo


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
        gitobj = git.Git(project['path'])
        data.append({
            'id': project['id'],
            'name': project['name'],
            'branches': gitobj.get_branch_names(),
        })
    return data


@view_config(route_name='logs', renderer='json')
def logs(request):
    project_id = int(request.matchdict['project_id'])
    branch = request.GET.get('branch')
    skip = request.GET.get('skip')
    rev = request.GET.get('rev')

    skip = int(skip) if skip else 0

    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')

    gitobj = git.Git(project['path'])
    if not gitobj.exist_branch(branch):
        raise Exception('TODO')

    return gitobj.get_logs(branch, rev, skip)


@view_config(route_name='log_details', renderer='json')
def log_details(request):
    project_id = int(request.matchdict['project_id'])
    h = request.matchdict['hash']
    if not h.isalnum():
        # TODO: validate correctly hash
        raise Exception('TODO')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])
    return gitobj.get_log_details(h)


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


@view_config(route_name='opt', renderer='json')
def opt(request):
    return {}


@view_config(route_name='diff_context', renderer='json')
def diff_context(request):
    project_id = int(request.matchdict['project_id'])
    h = request.matchdict['hash']
    if not h.isalnum():
        # TODO: validate correctly hash
        raise Exception('TODO')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])

    # TODO: validation
    filename = request.json_body['path']
    return gitobj.get_diff_context(
        filename, h,
        **request.json_body['data']
    )


@view_config(route_name='tree', renderer='json')
def tree(request):
    project_id = int(request.matchdict['project_id'])
    h = request.matchdict['hash']
    if not h.isalnum():
        # TODO: validate correctly hash
        raise Exception('TODO')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])
    path = request.GET['path']
    return gitobj.tree(
        path, h
    )


@view_config(route_name='blob', renderer='json')
def blob(request):
    project_id = int(request.matchdict['project_id'])
    h = request.matchdict['hash']
    if not h.isalnum():
        # TODO: validate correctly hash
        raise Exception('TODO')
    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')
    gitobj = git.Git(project['path'])
    path = request.GET['path']
    return gitobj.blob(
        path, h
    )
