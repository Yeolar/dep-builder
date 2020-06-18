#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Yeolar
#

import multiprocessing
import os
import subprocess
import sys


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


def read_deps(f, *args):
    deps = []
    if f != '-':
        with open(f) as fp:
            args = fp.readlines()
    for arg in args:
        s = arg.strip()
        if not s.startswith('#'):
            git, _, commit = s.partition('@')
            commit, _, build = commit.partition(':')
            deps.append({
                'url': git,
                'root': git.split('/')[-1],
                'commit': commit,
                'build': build or 'cmake -DCMAKE_PREFIX_PATH=../../usr/local ..'
            })
    return deps


def build_dep(root, commit, build, jobs=multiprocessing.cpu_count()-1):
    with cd(root):
        if commit:
            run('git checkout', commit)
        run('git pull')
        with cd('_build'):
            run(build)
            run('make -j%d' % jobs)
            run('make DESTDIR=../.. install')


if __name__ == '__main__':
    deps = read_deps(*sys.argv[1:])
    for dep in deps:
        if not os.path.exists(dep['root']):
            run('git', 'clone', dep['url'])
    for dep in deps:
        build_dep(dep['root'], dep['commit'], dep['build'])
