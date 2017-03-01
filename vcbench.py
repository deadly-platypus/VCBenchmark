#!/usr/bin/python

import shutil
import sys, argparse, os
import svn.remote
from git import Repo, RemoteProgress
from subprocess import call

GITBENCHMARK = 'git-benchmark.sh'
SVNBENCHMARK = 'svn-benchmark.sh'
GIT_DIR = 'git-work'
SVN_DIR = 'svn-work'

commitslist = []

class CloneProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if cur_count / (max_count or 100.0) % 10:
            sys.stdout.write('.')
            sys.stdout.flush()

class IncorrectCommitOrder(Exception):
    def __init__(self, start, end):
        self.start = str(start)
        self.end = str(end)
    def __str__(self):
        return self.start + '->' + self.end

class CommitNotFound(Exception):
    def __init__(self, commit):
        self.commit = commit
    def __str__(self):
        return 'Commit ' + str(self.commit) + ' cannot be found.'

def parse_args():
    parser = argparse.ArgumentParser(description='Version Control Benchmark')
    parser.add_argument('vc', help='The version control to benchmark',
            choices=['git', 'svn'])
    parser.add_argument('-s', '--start', help="""The commit at which to start.\
            If omitted, the first commit will be used.""")
    parser.add_argument('-e', '--end', help="""The commit at which to end. If \
            omitted, the latest commit will be used.""")
    parser.add_argument('repo', help='The repository location')
    parser.add_argument('-pre', help='Instruction to run before benchmark')
    parser.add_argument('-post', help='Instruction to run after benchmark')
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
            raise IncorrectCommitOrder(start.name_rev[0:40], end.name_rev[0:40])

        if end_found:
            commitslist.append(commit.name_rev[0:40])

        if start_found:
            break

    commitslist.reverse()
    return

def benchmark_git(repourl, start, end, preInst, postInst):
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

    fo = open(GITBENCHMARK, 'w')
    print 'Outputting benchmark'
    fo.write("#!/usr/bin/sh\n")
    fo.write("cd " + GIT_DIR + "\n")
    if preInst:
        fo.write(preInst + "\n")
    fo.write("git checkout " + commitslist[0] + "\n")
    for commit in commitslist[1:]:
        fo.write("git merge -m \"benchmark\" " + commit + "\n")
    if postInst:
        fo.write(postInst + "\n")
    print 'Done.'

    return

def find_svn_start(client):
    end = 0
    for commit in client.log_default():
        end = commit

    return end.revision

def find_svn_end(client):
    for commit in client.log_default():
        return commit.revision

def verify_svn_revs(startcommit, endcommit, client):
    start_found = False
    end_found = False

    for commit in client.log_default():
        if commit.revision == startcommit:
            start_found = True
        elif commit.revision == endcommit:
            end_found = True

        if end_found:
            commitslist.append(commit.revision)

        if start_found:
            break

    if not start_found:
        raise CommitNotFound(startcommit)
    elif not end_found:
        raise CommitNotFound(endcommit)
    elif startcommit > endcommit:
        raise IncorrectCommitOrder(startcommit, endcommit)

    commitslist.reverse()
    return

def benchmark_svn(repourl, start, end, preInst, postInst):
    if os.path.exists(SVN_DIR):
        shutil.rmtree(SVN_DIR)

    fo = open(SVNBENCHMARK, 'w')
    client = svn.remote.RemoteClient(repourl)
    sys.stdout.write('Checking out...')
    sys.stdout.flush()
    revision = client.checkout(SVN_DIR)
    print 'Done'

    if not start:
        startcommit = find_svn_start(client)
    else:
        startcommit = start

    if not end:
        endcommit = find_svn_end(client)
    else:
        endcommit = end

    verify_svn_revs(startcommit, endcommit, client)
    fo.write('#!/usr/bin/sh\n')
    fo.write('cd ' + SVN_DIR + '\n')
    if preInst:
        fo.write(preInst + "\n")
    fo.write('svn up -r' + str(commitslist[0]) + '\n')
    for commit in commitslist[1:]:
        fo.write("svn merge -c " + str(commit) + " .\n")
    if postInst:
        fo.write(postInst + "\n")

    return

def main():
    args = parse_args()
    try:
        if args.vc == 'git':
            benchmark_git(args.repo, args.start, args.end, args.pre, args.post)
        elif args.vc == 'svn':
            benchmark_svn(args.repo, args.start, args.end, args.pre, args.post)
    except IncorrectCommitOrder as ico:
        sys.stdout.write("Commit " + ico.start)
        sys.stdout.write(" comes before " + ico.end)
        sys.stdout.write("\n")
        sys.stdout.flush()
    except CommitNotFound as cnf:
        print(cnf)

    return


if __name__ == "__main__":
    main()
