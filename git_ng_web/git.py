
import subprocess


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
