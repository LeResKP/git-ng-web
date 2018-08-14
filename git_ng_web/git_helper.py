import StringIO
from collections import defaultdict
from git import Repo, NULL_TREE, Blob
import os
import binascii


# These constant values are used in angular
DIFF_LINE_TYPE_ADDED = 'added'
DIFF_LINE_TYPE_DELETED = 'deleted'
DIFF_LINE_TYPE_CONTEXT = 'context'
DIFF_LINE_TYPE_EXTRA_CONTEXT = 'extra'
DIFF_LINE_TYPE_EXPAND = 'expand'
DIFF_LINE_TYPE_HIDDEN = 'hidden'

DIFF_CONTEXT_LINE = 20

DEFAULT_DIFF_CONTEXT = 3


def get_line_number_hunk(s):
    lis = s[1:].split(',')
    line_number = int(lis[0])
    if len(lis) == 2:
        hunk_size = int(lis[1])
    elif len(lis) == 1:
        # @@ -0,0 +1 @@
        hunk_size = 1
    else:
        raise Exception('TODO')

    return line_number, hunk_size


def parse_hunk_title(line):
    # @@ -18,6 +18,7 @@ def main(global_config, **settings):
    before, after = line.split('@@')[1].strip().split(' ')
    assert(before.startswith('-'))
    assert(after.startswith('+'))
    a_line_num, a_hunk_size = get_line_number_hunk(before)
    b_line_num, b_hunk_size = get_line_number_hunk(after)
    return {
        'a_line_num': a_line_num,
        'a_hunk_size': a_hunk_size,
        'b_line_num': b_line_num,
        'b_hunk_size': b_hunk_size,
    }


def _get_missing_lines(b_line_num, prev_b_line_num, file_length):

    if prev_b_line_num is not None:
        start = max(prev_b_line_num + 1, b_line_num - DIFF_CONTEXT_LINE)
        end = b_line_num
    else:
        start = b_line_num
        end = min(start + DIFF_CONTEXT_LINE, file_length + 1)

    return range(start, end)


def _parse_patch(content, nb_lines):
    if not content:
        return []

    lines = []
    last_separator = None

    a_line_num = 1
    b_line_num = 1

    lis = content.split('\n')
    # Make sure the end of patch is correct
    assert lis[-1] == ''

    for line in lis[:-1]:
        if line.startswith('@@'):
            data = parse_hunk_title(line)
            if data['b_line_num'] == 1:
                continue

            if last_separator:
                data['prev_b_line_num'] = (
                    last_separator['b_line_num'] +
                    last_separator['b_hunk_size'] - 1
                )
            else:
                data['prev_b_line_num'] = 0

            a_line_num = data['a_line_num']
            b_line_num = data['b_line_num']
            if b_line_num > 1:
                lines.append({
                    'type': DIFF_LINE_TYPE_EXPAND,
                    'a_line_num': None,
                    'b_line_num': None,
                    'content': line,
                    'context_data': data,
                })

            last_separator = data

        elif line.startswith('+'):
            lines.append({
                'type': DIFF_LINE_TYPE_ADDED,
                'a_line_num': None,
                'b_line_num': b_line_num,
                'content': line,
            })
            b_line_num += 1

        elif line.startswith('-'):
            lines.append({
                'type': DIFF_LINE_TYPE_DELETED,
                'a_line_num': a_line_num,
                'b_line_num': None,
                'content': line,
            })
            a_line_num += 1

        else:
            lines.append({
                'type': DIFF_LINE_TYPE_CONTEXT,
                'a_line_num': a_line_num,
                'b_line_num': b_line_num,
                'content': line,
            })
            a_line_num += 1
            b_line_num += 1

    if b_line_num > 1 and b_line_num < nb_lines:
        lines.append({
            'type': DIFF_LINE_TYPE_EXPAND,
            'b_line_num': None,
            'a_line_num': None,
            'content': '',
            'context_data': {
                'a_line_num': a_line_num,
                'b_line_num': b_line_num,
                'a_hunk_size': None,
                'b_hunk_size': None,
                'prev_b_line_num': None,
            },
        })

    return lines


class Git(object):

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def get_branch_names(self):
        return {
            'local': [b.name for b in self.repo.branches],
            'remote': [b.name for b in self.repo.remotes.origin.refs],
            'default': self.get_default_branch_name(),
        }

    def exist_branch(self, branch):
        branches = self.repo.branches + self.repo.remotes.origin.refs
        return branch in [b.name for b in branches]

    def get_default_branch_name(self):
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Raised when the branch is detached
            pass
        branches = ['master', 'develop']
        names = [b.name for b in self.repo.branches]
        for b in branches:
            if b in names:
                return b

        return self.repo.branches[0].name

    def commit_to_json(self, commit, stat):

        def get_branches(commit):
            brs = []
            for br in self.repo.branches + self.repo.remotes.origin.refs:
                if br.commit == commit:
                    brs.append(br.name)
            return brs

        # Remove the summary from the message
        message = commit.message[len(commit.summary):].strip()
        dic = {
            'hash': commit.hexsha,
            'short_hash': commit.hexsha[:7],
            'summary': commit.summary,
            'message': message,
            'author': {
                'name': commit.author.name,
                'email': commit.author.email,
            },
            'date': commit.committed_datetime,
            'branches': get_branches(commit)
        }

        if stat:
            dic['stats'] = {
                'files': [{'filename': f, 'data': d}
                          for f, d in sorted(commit.stats.files.items(),
                                             key=lambda (k, v): k)],
                'total': commit.stats.total,
            }
        return dic

    def get_logs(self, branch, rev, skip):
        NB_COMMIT = 50

        last = None
        first = None
        commits_by_date = defaultdict(list)
        for commit in self.repo.iter_commits(rev or branch,
                                             max_count=NB_COMMIT, skip=skip):
            last = commit
            first = commit if first is None else first
            commits_by_date[commit.committed_datetime.date()].append(
                self.commit_to_json(commit, stat=False))
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

    def get_log_details(self, h):
        commit = self.repo.commit(h)
        return {
            'files': [{'filename': f, 'data': d}
                      for f, d in commit.stats.files.items()],
            'total': commit.stats.total,
        }

    def _get_file_content_by_lines(self, filename, h):
        """Get the file content at revision
        """
        res = self.repo.git.show('%s:%s' % (h, filename))
        content_by_lines = {}
        for index, line in enumerate(res.split('\n'), start=1):
            content_by_lines[index] = line

        return content_by_lines

    def _get_diff_lines(self, h, after_filename, content, full_diff):
        content_by_lines = []
        if full_diff:
            content_by_lines = self._get_file_content_by_lines(
                after_filename, h)

        nb_lines = len(content_by_lines)
        return _parse_patch(content, nb_lines)

    def get_diff_context(self, filename, h,
                         a_line_num, a_hunk_size,
                         b_line_num, b_hunk_size,
                         prev_b_line_num):

        content_by_lines = self._get_file_content_by_lines(
            filename, h)

        line_numbers = _get_missing_lines(
            b_line_num, prev_b_line_num, len(content_by_lines))

        if not line_numbers:
            return []

        lines = []

        if (prev_b_line_num is not None and
                line_numbers[0] > prev_b_line_num + 1):
            lines.append({
                'type': DIFF_LINE_TYPE_EXPAND,
                'a_line_num': None,
                'b_line_num': None,
                'content': '@@ -%i,%i +%i,%i @@ %s' % (
                    a_line_num - DIFF_CONTEXT_LINE,
                    a_hunk_size + DIFF_CONTEXT_LINE,
                    b_line_num - DIFF_CONTEXT_LINE,
                    b_hunk_size + DIFF_CONTEXT_LINE,
                    content_by_lines[line_numbers[0] - 1]
                ),
                'context_data': {
                    'a_line_num': a_line_num - DIFF_CONTEXT_LINE,
                    'b_line_num': b_line_num - DIFF_CONTEXT_LINE,
                    'a_hunk_size': a_hunk_size + DIFF_CONTEXT_LINE,
                    'b_hunk_size': b_hunk_size + DIFF_CONTEXT_LINE,
                    'prev_b_line_num': prev_b_line_num,
                }
            })

        for n in line_numbers:
            lines.append({
                'type': DIFF_LINE_TYPE_EXTRA_CONTEXT,
                'a_line_num': n - (b_line_num - a_line_num),
                'b_line_num': n,
                'content': ' %s' % content_by_lines[n]
            })

        if (prev_b_line_num is None and
                line_numbers[-1] < len(content_by_lines)):
            lines.append({
                'type': DIFF_LINE_TYPE_EXPAND,
                'a_line_num': None,
                'b_line_num': None,
                'content': '',
                'context_data': {
                    'a_line_num': lines[-1]['a_line_num'] + 1,
                    'b_line_num': lines[-1]['b_line_num'] + 1,
                    'a_hunk_size': None,
                    'b_hunk_size': None,
                    'prev_b_line_num': None,
                }
            })
        return lines

    def _get_diff(self, commit, create_patch,
                  ignore_all_space=False, unified=DEFAULT_DIFF_CONTEXT):
        unified = unified if unified is not None else DEFAULT_DIFF_CONTEXT
        if commit.parents:
            # When it's a merge commit we have 2 parents.
            assert len(commit.parents) < 3
            return commit.parents[0].diff(
                commit, create_patch=create_patch,
                ignore_all_space=ignore_all_space, unified=unified)
        else:
            return commit.diff(NULL_TREE, create_patch=create_patch,
                               ignore_all_space=ignore_all_space,
                               unified=unified)

    def get_diff(self, h, ignore_all_space=False, unified=DEFAULT_DIFF_CONTEXT):
        commit = self.repo.commit(h)

        # THe change_type and files information are returns when create_patch
        # is False
        diffs = self._get_diff(commit, create_patch=False)
        diff_with_patches = self._get_diff(commit, create_patch=True,
                                           ignore_all_space=ignore_all_space,
                                           unified=unified)

        new_lis = []
        path = None
        for index, (diff, diff_patch) in enumerate(zip(diffs, diff_with_patches)):
            if diff.change_type == 'A':
                title = 'New file %s' % diff.b_path
                path = diff.b_path
            elif diff.change_type == 'D':
                title = 'Delete file %s' % diff.a_path
                path = diff.a_path
            elif diff.change_type == 'R':
                title = 'Rename %s -> %s' % (diff.a_path, diff.b_path)
                path = diff.b_path
            elif diff.change_type == 'M':
                assert diff.a_path == diff.b_path
                title = diff.b_path
                path = diff.b_path
            else:
                raise ValueError(
                    'change type %s is not supported in commit %s' % (
                        diff.change_type, h,
                    )
                )

            full_diff = diff.change_type not in ('A', 'D')
            lines = self._get_diff_lines(h, path, diff_patch.diff,
                                         full_diff=full_diff)

            new_lis.append({
                'path': path,
                'title': title,
                'lines': lines,
            })

        return {
            'commit': self.commit_to_json(commit, stat=True),
            'diffs': new_lis
        }

    def tree(self, path, h, blob=False):
        res = self.repo.git.ls_tree(h, path)
        lis = []
        for line in res.split('\n'):
            perm, typ, sha, path = filter(bool, line.replace('\t', ' ').split(' '))

            dic = {
                'name': os.path.basename(path),
                'type': typ,
                'path': path,
            }
            if blob and typ == 'blob':
                dic['blob'] = sha
            lis.append(dic)
        return sorted(lis, key=lambda x: (x['type'] == 'blob', x['name']))

    def blob(self, path, h):
        lis = self.tree(path, h, blob=True)
        assert(len(lis) == 1)
        blob = lis[0]['blob']

        bl = Blob(
            self.repo,
            binascii.unhexlify(blob))
        sio = StringIO.StringIO()
        bl.stream_data(sio)
        lines = []
        for index, line in enumerate(sio.getvalue().split('\n'), start=1):
            lines.append({
                'line_num': index,
                'content': line
            })
        return {
            'lines': lines,
            'path': path,
        }
