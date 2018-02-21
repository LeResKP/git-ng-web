import datetime
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

    def run(self, cmd):
        git = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.repo_path)
        stdout, stderr = git.communicate()
        return stdout.decode('utf-8', 'ignore')

    def get_branches(self):
        res = self.run(['git', 'branch', '-a'])
        lbranches = []
        rbranches = []

        for line in res.split('\n'):
            if not line:
                continue
            line = line[2:]
            if line.startswith('(HEAD'):
                # We are not on a real branch
                continue
            if line.startswith('remotes/origin/HEAD'):
                continue
            if line.startswith('remotes/'):
                rbranches.append(line.replace('remotes/', ''))
            else:
                lbranches.append(line)

        return {
            'local_branches': lbranches,
            'remote_branches': rbranches,
        }

    def get_current_branch(self):
        res = self.run(['git', 'branch', '-a'])
        for line in res.split('\n'):
            if not line:
                continue
            if line.startswith('*'):
                if line.startswith('* (HEAD'):
                    # We are not on a real branch
                    break
                return line[2:]
        branches = self.get_branches()
        if branches['local_branches']:
            return branches['local_branches'][0]

    def get_logs(self, branch):
        separator = u'\x00'  # separator added with -z
        res = self.run(
            ['git', 'log', '--decorate', '-z',
             '--date', 'unix',
             '-n', '50', branch, '--'])

        data = []
        logs = res.split(separator)
        for log in logs:
            lis = log.split('\n')
            hashes = lis[0].split(' ')
            h = hashes[1]
            labels = []
            label_line = ' '.join(hashes[2:]).strip().strip('(').strip(')')
            for label in label_line.split(','):
                labels.append(label.strip())
            author_name, author_email = parseaddr(
                ' '.join(lis[1].split(' ')[1:]))

            messages = lis[3:]
            short_message = ''
            for msg in messages:
                if msg.strip():
                    short_message = msg.strip()
                    break

            data.append({
                'hash': h,
                'short_hash': h[:7],
                'author': {
                    'name': author_name,
                    'email': author_email,
                },
                'date': datetime.datetime.fromtimestamp(
                    int(' '.join(lis[2].split(' ')[1:]))),
                'short_message': short_message,
                'message': '\n'.join(messages),
                'labels': labels,
            })

        return data

    def _get_file_content_by_lines(self, filename, h):
        """Get the file content at revision
        """
        res = self.run(['git', 'show', '%s:%s' % (h, filename)])
        content_by_lines = {}
        for index, line in enumerate(res.split('\n'), start=1):
            content_by_lines[index] = line

        return content_by_lines

    def _get_filename_and_content_from_patch(self, patch):
        filename = None
        content = []
        for line in patch.strip('\n').split('\n'):
            if line.startswith('+++'):
                filename = line[4:]
                continue
            if filename:
                content.append(line)
        return filename, '\n'.join(content)

    def _get_diff_lines(self, h, patch):
        filename, content = self._get_filename_and_content_from_patch(patch)
        content_by_lines = self._get_file_content_by_lines(filename, h)

        lines = []
        current_line = 1

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
                start_patch_line = int(after.split(',')[0])
                patch_line = int(after.split(',')[1])
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
        return filename, lines

    def get_diff(self, h):
        res = self.run(['git', 'show', '--no-prefix', h])
        parts = res.split('diff --git')
        info = parts.pop(0)

        lis = []
        for part in parts:
            filename, lines = self._get_diff_lines(h, part)
            lis.append({
                'filename': filename,
                'lines': lines,
            })

        return {
            'info': info,
            'diffs': lis
        }
