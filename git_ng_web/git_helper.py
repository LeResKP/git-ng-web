from collections import defaultdict
from git import Repo, NULL_TREE


# These constant values are used in angular
DIFF_LINE_TYPE_ADDED = 'added'
DIFF_LINE_TYPE_DELETED = 'deleted'
DIFF_LINE_TYPE_CONTEXT = 'context'
DIFF_LINE_TYPE_EXPAND = 'expand'
DIFF_LINE_TYPE_HIDDEN = 'hidden'


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

        dic = {
            'hash': commit.hexsha,
            'short_hash': commit.hexsha[:7],
            'summary': commit.summary,
            'message': commit.message,
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
                          for f, d in commit.stats.files.items()],
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

        lines = []
        current_line = 1

        if not content:
            return []

        # NOTE: Create a class to be able to update value in closure
        class counter(object):
            before_line = 0
            after_line = 0

        def add_hidden_lines(start, end):
            sublines = []
            for nb in range(start, end):
                counter.after_line += 1
                counter.before_line += 1
                sublines.append({
                    'type': DIFF_LINE_TYPE_HIDDEN,
                    'after_line': counter.after_line,
                    'before_line': counter.before_line,
                    'content': ' %s' % content_by_lines[nb]
                })
            if sublines:
                lines.append({
                    'type': DIFF_LINE_TYPE_EXPAND,
                    'after_line': None,
                    'before_line': None,
                    'content': line,
                    'lines': sublines,
                })

        lis = content.split('\n')
        for index, line in enumerate(lis):
            if index == (len(lis) - 1):
                # We should always have an empty line at last
                if line != '':
                    raise
                continue
            if line.startswith('@@'):
                # We need to insert the lines before
                # @@ -18,6 +18,7 @@ def main(global_config, **settings):
                # we want to get +18,7
                after = line.split('@@')[1].strip().split(' ')[1]
                assert(after.startswith('+'))
                after = after[1:]
                split = after.split(',')
                start_patch_line = int(split[0])
                if len(split) == 2:
                    patch_line = int(after.split(',')[1])
                elif len(split) == 1:
                    # @@ -0,0 +1 @@
                    patch_line = 1
                else:
                    raise Exception('TODO')
                add_hidden_lines(current_line, start_patch_line)
                # start_patch_line & patch_line can be 0 when deleting a file
                current_line = (start_patch_line + patch_line) or 1
                continue

            if line.startswith('+'):
                counter.after_line += 1
                lines.append({
                    'type': DIFF_LINE_TYPE_ADDED,
                    'after_line': counter.after_line,
                    'before_line': None,
                    'content': line,
                })
                continue

            if line.startswith('-'):
                counter.before_line += 1
                lines.append({
                    'type': DIFF_LINE_TYPE_DELETED,
                    'after_line': None,
                    'before_line': counter.before_line,
                    'content': line,
                })
                continue

            counter.after_line += 1
            counter.before_line += 1
            lines.append({
                'type': DIFF_LINE_TYPE_CONTEXT,
                'after_line': counter.after_line,
                'before_line': counter.before_line,
                'content': line,
            })

        add_hidden_lines(current_line, len(content_by_lines) + 1)
        return lines

    def get_diff(self, h):
        commit = self.repo.commit(h)

        def cmd(create_patch):
            if commit.parents:
                assert len(commit.parents) == 1
                return commit.parents[0].diff(
                    commit, create_patch=create_patch)
            else:
                return commit.diff(NULL_TREE, create_patch=create_patch)

        # THe change_type and files information are returns when create_patch
        # is False
        diffs = cmd(create_patch=False)
        diff_with_patches = cmd(create_patch=True)

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
                'title': title,
                'lines': lines,
            })

        return {
            'commit': self.commit_to_json(commit, stat=True),
            'diffs': new_lis
        }
