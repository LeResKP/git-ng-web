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
        dic = {
            'id': project['id'],
            'name': project['name'],
            'current_branch': gitobj.get_current_branch(),
        }
        dic.update(gitobj.get_branches())

        data.append(dic)

    return data


@view_config(route_name='logs', renderer='json')
def logs(request):
    NB_COMMIT = 50

    project_id = int(request.matchdict['project_id'])
    branch = request.GET.get('branch')
    skip = request.GET.get('skip')
    rev = request.GET.get('rev')

    skip = int(skip) if skip else 0

    project = get_project(request, project_id)
    if not project:
        raise Exception('TODO')

    gitobj = git.Git(project['path'])
    branches = gitobj.get_branches()
    if branch not in sum(branches.values(), []):
        raise Exception('TODO')

    def get_branches(commit):
        brs = []
        for br in repo.branches + repo.remotes.origin.refs:
            if br.commit == commit:
                brs.append(br.name)
        return brs

    last = None
    first = None
    commits_by_date = defaultdict(list)
    repo = Repo(project['path'])
    for commit in repo.iter_commits(rev or branch, max_count=NB_COMMIT,
                                    skip=skip):
        last = commit
        first = commit if first is None else first
        commits_by_date[commit.committed_datetime.date()].append({
            'hash': commit.hexsha,
            'short_hash': commit.hexsha[:7],
            'summary': commit.summary,
            'author': {
                'name': commit.author.name,
                'email': commit.author.email,
            },
            'date': commit.committed_datetime,
            'stats': [{'filename': f, 'data': d}
                      for f, d in commit.stats.files.items()],
            'branches': get_branches(commit)
        })

    logs = [t for t in sorted(commits_by_date.items(),
                              key=lambda(k, v): k, reverse=True)]

    newer = skip - NB_COMMIT
    skip += NB_COMMIT
    return {
        'logs': logs,
        'rev': rev or first.hexsha,
        'skip_older': skip if last.parents else None,
        'skip_newer': newer if newer >= 0 else None,
    }


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
