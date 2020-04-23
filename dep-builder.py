#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import os
import subprocess


def _wrap_with(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = '1;%s' % c
        return '\033[%sm%s\033[0m' % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')


def run(*cmd):
    cmdstr = ' '.join(cmd)
    print cyan(cmdstr)
    return subprocess.call(cmdstr, shell=True)


class cd(object):

    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(path, 0755)
        self.path = path
        self.oldpath = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.oldpath)


def read_deps(f):
    def parse_dep(line):
        git, _, commit = line.partition('@')
        return git, commit

    deps = {}
    with open(f) as fp:
        for line in fp.readlines():
            if not line.startswith('#'):
                p = parse_dep(line.strip())
                deps[p[0]] = {
                    'url': p[0],
                    'root': p[0].split('/')[-1],
                    'commit': p[1]
                }
    return deps

def build_dep(root, commit, jobs=multiprocessing.cpu_count()-1):
    with cd(root):
        if commit:
            run('git checkout', commit)
        with cd('build'):
            run('cmake .. && make -j%d' % jobs)
            run('make DESTDIR=../.. install')


if __name__ == '__main__':
    deps = read_deps('deps.conf')
    with cd('deps'):
        for dep in deps.itervalues():
            if not os.path.exists(dep['root']):
                run('git', 'clone', dep['url'])
        for dep in deps.itervalues():
            build_dep(dep['root'], dep['commit'])
