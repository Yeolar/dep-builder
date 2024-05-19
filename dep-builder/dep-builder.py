#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Yeolar
#

import argparse
import multiprocessing
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CPU_COUNT = multiprocessing.cpu_count()

SHELL_TPL = """#!/bin/sh -x

if [ ! -f %(kfile)s ]; then
    wget %(url)s -O %(kfile)s
fi
rm -rf %(key)s
%(extract)s
cd %(key)s
mkdir -p %(root)s/usr/local/include
mkdir -p %(root)s/usr/local/lib
%(cmds)s
"""

class Dependency(object):

    EXTRACT = dict((
        ('.hpp', 'mkdir %(key)s && cp %(kfile)s %(key)s/%(file)s'),
        ('.zip', 'unzip %(kfile)s'),
        ('.tar.gz', 'tar xzf %(kfile)s'),
    ))

    def __init__(self, first_line):
        self.key, _, url = first_line.partition(':')
        self.sh = self.key + '.sh'
        self.url = url.strip()
        self.file = self.url.split('/')[-1]
        self.kfile = self.key + '__' + self.file
        self.extract = self.EXTRACT[os.path.splitext(self.file)[1]]
        self.root = ROOT
        self._cmds = []

    def __str__(self):
        return self.key + ': ' + self.url

    def add_command(self, cmd):
        cmd = cmd.strip()
        if cmd.startswith('CMAKE'):
            self._cmds.append('mkdir _build && cd _build')
            self._cmds.append('cmake -DCMAKE_PREFIX_PATH=%(root)s/usr/local'
                              + cmd[len('CMAKE'):])
        elif cmd.startswith('MAKE_WITH_INSTALL'):
            self._cmds.append('make -j%d' % CPU_COUNT
                              + cmd[len('MAKE_WITH_INSTALL'):])
            self._cmds.append('make DESTDIR=%(root)s install')
        elif cmd.startswith('MAKE'):
            self._cmds.append('make -j%d' % CPU_COUNT + cmd[len('MAKE'):])
        elif cmd.startswith('CP_INC'):
            self._cmds.append('cp' + cmd[len('CP_INC'):]
                              + ' %(root)s/usr/local/include/')
        elif cmd.startswith('CP_LIB'):
            self._cmds.append('cp' + cmd[len('CP_LIB'):]
                              + ' %(root)s/usr/local/lib/')
        else:
            self._cmds.append(cmd)

    def generate(self):
        self.cmds = '\n'.join(self._cmds)
        return SHELL_TPL % self.__dict__ % self.__dict__


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='C++ dep builder.')
    ap.add_argument('conf', help='dep config file')
    ap.add_argument('--targets', action='store', dest='targets',
                    help='build targets')
    ap.add_argument('--refresh-only', action='store_true', dest='refresh_only',
                    help='refresh sh only')
    args = ap.parse_args()

    deps = []

    with open(args.conf) as fp:
        lines = [line.rstrip() for line in fp.readlines()]

    for line in lines:
        if line.startswith('#'):
            continue
        if len(line) > 0:
            if line[0] != ' ':
                deps.append(Dependency(line))
            else:
                deps[-1].add_command(line)

    targets = args.targets and args.targets.split(',') or []

    for dep in deps:
        if not targets or dep.key in targets:
            with open(os.path.join(dep.root, dep.sh), 'w') as fp:
                fp.write(dep.generate())

    if not args.refresh_only:
        for dep in deps:
            if not targets or dep.key in targets:
                os.system('cd %(root)s && sh -x %(sh)s' % dep.__dict__)
