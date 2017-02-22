#!/usr/bin/python

import shutil
import sys, argparse, os
from git import Repo, RemoteProgress

GIT_DIR = 'git-work'

class CloneProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if cur_count / (max_count or 100.0) % 10:
            sys.stdout.write('.')
            sys.stdout.flush()

class IncorrectCommitOrder(Exception):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __str__(self):
        return self.start.name_rev + '->' + self.end.name_rev

def parse_args():
    parser = argparse.ArgumentParser(description='Version Control Benchmark')
    parser.add_argument('vc', help='The version control to benchmark',
            choices=['git', 'svn'])
    parser.add_argument('-s', '--start', help='The commit at which to start')
    parser.add_argument('-e', '--end', help='The commit at which to end')
    parser.add_argument('repo', help='The repository location')
    return parser.parse_args()

def find_git_start(repo):
    commits = repo.iter_commits()
    commit = ''
    for commit in commits:
        pass

    return commit

def find_git_end(repo):
    commits = repo.iter_commits()
    for commit in commits:
        return commit

def verify_git_revs(start, end, repo):
    start_found = False
    end_found = False
    for commit in repo.iter_commits():
        if commit == start:
            start_found = True
        elif commit == end:
            end_found = True

        if not end_found and start_found:
            raise IncorrectCommitOrder(start, end)

    return

def benchmark_git(repourl, start, end):
    if os.path.exists(GIT_DIR):
        shutil.rmtree(GIT_DIR)

    print 'Benchmarking git repo ' + repourl
    sys.stdout.write('Cloning')
    sys.stdout.flush()
    repo = Repo.clone_from(repourl, GIT_DIR, progress=CloneProgressPrinter())
    print 'Done'

    if not start:
        startcommit = find_git_start(repo)
    else:
        startcommit = repo.commit(start)

    if not end:
        endcommit = find_git_end(repo)
    else:
        endcommit = repo.commit(end)

    verify_git_revs(startcommit, endcommit, repo)

    print 'Checking out commit ' + startcommit.name_rev[0:40]

    shutil.rmtree(GIT_DIR)

def main():
    args = parse_args()
    try:
        if args.vc == 'git':
            benchmark_git(args.repo, args.start, args.end)
    except IncorrectCommitOrder as ico:
        sys.stdout.write("Commit " + ico.end.name_rev[0:40])
        sys.stdout.write(" comes before " + ico.start.name_rev[0:40])
        sys.stdout.write("\n")
        sys.stdout.flush()

    return


if __name__ == "__main__":
    main()
