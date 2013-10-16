from sh import git

def get_versions(rootdir):
    return git('--git-dir={rootdir}/keystone/.git'.format(rootdir=rootdir), 'rev-list', 'HEAD', max_count=100, abbrev_commit=True).splitlines()
