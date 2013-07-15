#!/usr/bin/env python

import os
import sys
from optparse import OptionParser

import cc
import re


COMMANDS = ['all', 'complexity', ]
USAGE = 'usage: pygenie command [directories|files|packages]'


class CommandParser(object):

    def __init__ (self, optparser, commands):
        self.commands = commands or []
        self.optparser = optparser

    def parse_args(self, args=None, values=None):
        args = args or sys.argv[1:]
        if len(args) < 1:
            self.optparser.error('please provide a valid command')

        command = args[0]
        if command not in self.commands:
            self.optparser.error("'%s' is not a valid command" % command)

        options, values = self.optparser.parse_args(args[1:], values)
        return command, options, values

def should_exclude(path, options):
    if options.exclude_pattern:
        return path.find(options.exclude_pattern)!=-1 or re.match(options.exclude_pattern, path)

def find_module(fqn, options):
    join = os.path.join
    exists = os.path.exists
    partial_path = fqn.replace('.', os.path.sep)
    for p in sys.path:
        if should_exclude(p, options):
            continue
        path = join(p, partial_path, '__init__.py')
        if exists(path):
            return path
        path = join(p, partial_path + '.py')
        if exists(path):
            return path
    raise Exception('invalid module')

def add_files_from_dir(items, dirname, options):
    for name in os.listdir(dirname):
        f = os.path.join(dirname, name)
        if should_exclude(f, options):
            continue
        if name.endswith('.py'):
            if os.path.isfile(f):
                items.add(os.path.abspath(f))
        elif options.recursive and os.path.isdir(f):
            add_files_from_dir(items, f, options)

def main():
    from optparse import OptionParser

    parser = OptionParser(usage='./cc.py command [options] *.py')
    parser.add_option('-v', '--verbose',
            dest='verbose', action='store_true', default=False,
            help='print detailed statistics to stdout')
    parser.add_option('-r', '--recursive',
            dest='recursive', action='store_true', default=False,
            help='analyse directories recursively')
    parser.add_option('-e', '--exclude-pattern',
            dest='exclude_pattern', action='store', default=None,
            help='pattern to exclude files and directories')
    
    parser = CommandParser(parser, COMMANDS)
    command, options, args = parser.parse_args()

    items = set()
    for arg in args:
        if os.path.isdir(arg):
            add_files_from_dir(items, arg, options)
        elif os.path.isfile(arg):
            items.add(os.path.abspath(arg))
        else:
            # this should be a package'
            items.add(find_module(arg, options))

    for item in items:
        code = open(item).read()
        if command in ('all', 'complexity'):
            stats = cc.measure_complexity(code, item)
            pp = cc.PrettyPrinter(sys.stdout, verbose=options.verbose)
            pp.pprint(item, stats)

if __name__ == '__main__':
    main()
