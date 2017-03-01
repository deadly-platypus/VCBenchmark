# VCBenchmark
A benchmarking tool for version control software.

`vcbench.py` checks out a repository you specify, and then creates a bash script
to apply all commits between two commit revisions.  If the start commit is not
specified, the first commit is used.  If the end commit is not specified, the
latest commit is used.

Examples: 

. python vcbench.py svn 
