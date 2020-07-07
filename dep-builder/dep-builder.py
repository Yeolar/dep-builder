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


TYPE_GIT = 0
TYPE_ZIP = 1
TYPE_GZ = 2

def get_type(url):
    if url.lower().endswith('.tar.gz'):
        return TYPE_GZ
    if url.lower().endswith('.zip'):
        return TYPE_ZIP
    return TYPE_GIT


def read_deps(f, *args):
    deps = []
    if f != '-':
        with open(f) as fp:
            args = fp.readlines()
    for arg in args:
        s = arg.strip()
        if not s.startswith('#'):
            url, _, commit = s.partition('@')
            type = get_type(url)
            commit, _, build = commit.partition(':')
            deps.append({
                'raw': s,
                'type': type,
                'url': url,
                'root': url.split('/')[-1],
                'commit': commit,
                'build': build or 'cmake ..'
            })
    return deps


def build_dep(root, commit, build, jobs=multiprocessing.cpu_count()-1):
    path = os.path.join(os.getcwd(), 'usr', 'local')
    with cd(root):
        if commit is not None:
            if commit:
                run('git checkout', commit)
            run('git pull')
        if build.startswith('cmake'):
            with cd('_build'):
                build = 'cmake -DCMAKE_PREFIX_PATH=' + path + build[5:]
                run(build)
                run('make -j%d' % jobs)
                run('make DESTDIR=../.. install')
        else:
            run(build)
            run('make -j%d' % jobs)
            run('make DESTDIR=.. install')


if __name__ == '__main__':
    deps = read_deps(*sys.argv[1:])
    for dep in deps:
        if not os.path.exists(dep['root']):
            print 'fetch', white(dep['raw'], True)
            if dep['type'] == TYPE_GIT:
                run('git', 'clone', dep['url'])
            else:
                run('wget', dep['url'])
    for dep in deps:
        if dep['type'] != TYPE_GIT and not os.path.exists(dep['commit']):
            print 'unzip', white(dep['raw'], True)
            if dep['type'] == TYPE_GZ:
                run('tar', 'xzf', dep['root'])
            if dep['type'] == TYPE_ZIP:
                run('unzip', dep['root'])
    for dep in deps:
        print 'build', white(dep['raw'], True)
        if dep['type'] == TYPE_GIT:
            build_dep(dep['root'], dep['commit'], dep['build'])
        else:
            build_dep(dep['commit'], None, dep['build'])
