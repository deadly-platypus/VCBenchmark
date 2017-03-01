# VCBenchmark
A benchmarking tool for version control software.

`vcbench.py` checks out a repository you specify, and then creates a bash script
to apply all commits between two commit revisions.  If the start commit is not
specified, the first commit is used.  If the end commit is not specified, the
latest commit is used.

Examples: 

SVN: `python vcbench.py svn http://llvm.org/svn/llvm-project/libcxx/trunk/ --end 296642 --start 162644`

git: `python vcbench.py git https://github.com/llvm-mirror/libcxx -s 0268c19d723847b9c2973b577f67324449a01957 -e 29ed46b12e6c5cf0e2f5aadae50137d8eb31bcac`

`vcbench.py` creates a file called `svn-benchmark.sh` for SVN and `git-benchmark.sh` for git.

You can also specify a command to run before starting the checkout, and a command for after all merges are complete by specifying `--pre` and `--post` 
