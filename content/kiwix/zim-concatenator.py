#!/opt/iiab/admin/venv/bin/python2

import sys

from os.path import expanduser
from os.path import exists
from os.path import isdir
from os.path import abspath
from os.path import join
from os.path import walk
from pipes import quote

from re import search
from re import compile

import subprocess
import argparse
import logging

class Concatenator(object):
    def __init__(self, path, logger, matching_regex_exp=r'^(?P<prefix>[\w\-\_\s]+\.zim)(?P<suffix>\w+)$'):
        self.logger = logger
        self.logger.debug('init concatenator')
        self.path = path
        self.resolved_path = abspath(expanduser(self.path))
        if not exists(self.resolved_path) or not isdir(self.resolved_path):
            return
        self.matching_regex = compile(matching_regex_exp)
        self.groups_by_prefix = {}

    def group_by_prefix(self, arg, dirname, files):
        if len(files) <= 1:
            return

        for file in files:
            m = search(self.matching_regex, file)
            if not m:
                continue

            m_dict = m.groupdict()
            prefix = m_dict['prefix']
            suffix = m_dict['suffix']
            new_file = join(dirname, prefix)
            already_there = self.groups_by_prefix.get(new_file)

            if not already_there:
                already_there = []
                self.groups_by_prefix[new_file] = already_there

            already_there.append(join(dirname, prefix + suffix))

    def concatenate(self):
        self.logger.debug('concatenate')
        for new_file, filenames in self.groups_by_prefix.items():
            filenames.sort()
            filenames = map(lambda f: quote(f), filenames)
            file_names_args = ' '.join(filenames)
            cmd = 'cat {}'.format(file_names_args)
            self.logger.debug('Going to create `%s` as a concatenation of `%s`', new_file, file_names_args)

            # TODO(cesarn): Sanitize `new_file` so that it is a valid filename
            with open(new_file, 'wb') as f:
                try:
                    output = subprocess.check_output([cmd], shell=True)
                    f.write(output)
                except subprocess.CalledProcessError as e:
                    self.logger.error(e)
                    sys.exit(-1)

    def run(self):
        self.logger.debug('run')
        walk(self.resolved_path, self.group_by_prefix, '')
        self.concatenate()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Concatenate several `zim` files.')
    parser.add_argument('--path', '-path', required=True, dest='path', help='The path of the directory that will be used to recursively search for `zim` files that are chunked')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    logger = logging.getLogger('zim-concatenator')
    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose == 2:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h.setFormatter(formatter)
    logger.addHandler(h)

    concatenator = Concatenator(path=args.path, logger=logger)
    concatenator.run()
