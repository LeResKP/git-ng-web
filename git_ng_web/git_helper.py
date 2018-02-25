from collections import defaultdict
import datetime
from git import Repo
import subprocess
from email.utils import parseaddr


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

    def run(self, cmd):
        git = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.repo_path)
        stdout, stderr = git.communicate()
        return stdout.decode('utf-8', 'ignore')

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

    def _get_file_content_by_lines(self, filename, h):
        """Get the file content at revision
        """
        res = self.run(['git', 'show', '%s:%s' % (h, filename)])
        content_by_lines = {}
        for index, line in enumerate(res.split('\n'), start=1):
            content_by_lines[index] = line

        return content_by_lines

    def _get_filenames_and_content_from_patch(self, patch):
        after_filename = None
        before_filename = None
        content = []
        for line in patch.strip('\n').split('\n'):
            # TODO: when only renamed we have
            # rename from file
            # rename to newfile
            if line.startswith('+++'):
                after_filename = line[4:]
                continue
            if line.startswith('---'):
                before_filename = line[4:]
                continue
            if after_filename:
                content.append(line)
        return before_filename, after_filename, '\n'.join(content)

    def _get_diff_lines(self, h, patch):
        (before_filename,
         after_filename,
         content) = self._get_filenames_and_content_from_patch(patch)
        # TODO: /dev/null
        content_by_lines = self._get_file_content_by_lines(after_filename, h)

        lines = []
        current_line = 1

        if not content:
            return before_filename, after_filename, []

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

        for line in content.split('\n'):
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

        add_hidden_lines(current_line, len(content_by_lines))
        return before_filename, after_filename, lines

    def get_diff(self, h):
        res = self.run(['git', 'show', '--no-prefix', h])
        parts = res.split('diff --git')
        info = parts.pop(0)

        lis = []
        for part in parts:
            (before_filename,
             after_filename,
             lines) = self._get_diff_lines(h, part)

            if before_filename == after_filename:
                title = after_filename
            elif before_filename == '/dev/null':
                title =  'New file %s' % after_filename
            elif after_filename == '/dev/null':
                title =  'Delete file %s' % before_filename
            else:
                title = 'Rename %s -> %s' % (before_filename, after_filename)
            lis.append({
                'title': title,
                'lines': lines,
            })

        return {
            'info': info,
            'diffs': lis
        }
