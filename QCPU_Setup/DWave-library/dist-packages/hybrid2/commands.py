import os.path
import os
import shutil
import sys

from pkg_resources import resource_filename, resource_isdir, \
            resource_listdir, resource_string
from .util import is_valid_name, makedirs, COLOR

def show_and_exit(msg, exitcode=1, color=COLOR["red"]):
    print("%s%s\033[0m" % (color, msg))
    exit(exitcode)

def show_subcommands(exitcode=0, color=COLOR["green"]):
    subcommands = "\n".join([" "*4+attr[12:] for attr in 
        dir(_DispatchCommand) if attr.startswith('_subcommand_') and 
        callable(getattr(_DispatchCommand, attr))])
    show_and_exit(
"""Available subcommands:
[hybrid]
%s""" % subcommands, exitcode, color)

def copy_skeleton(base, to):
    if not resource_isdir(__name__, base):
        shutil.copy2(resource_filename(__name__, base), to)
        return
    for ele in resource_listdir(__name__, base):
        if not resource_isdir(__name__, base+'/'+ele):
            copy_skeleton(base+'/'+ele, to)
            continue
        os.makedirs(os.path.join(to, ele))
        copy_skeleton(base+'/'+ele, os.path.join(to, ele))

class _DispatchCommand:
    def __init__(self, args):
        if not args:
            show_subcommands()
        self._subcommand = args[0]
        self._args       = args[1:]

    def execute(self):
        subcommand_name = '_subcommand_' + self._subcommand
        if not hasattr(self, subcommand_name) or \
            not callable(getattr(self, subcommand_name)):
            show_and_exit(
"""Unknown command: '%s'
Type '%s help' for usage.""" % (self._subcommand, os.path.basename(__file__)))
        getattr(self, subcommand_name)()

    def _subcommand_help(self):
        show_subcommands()

    def _subcommand_startproject(self):
        if not self._args:
            show_and_exit("you must provide a project name")
        if not is_valid_name(self._args[0]):
            show_and_exit("'%s' is not a valid project name. "
"Please make sure the name begins with a letter or underscore." % self._args[0])
        basedir = os.path.join(self._args[0], self._args[0])
        result = makedirs(basedir)
        if result:
            show_and_exit(result)
        copy_skeleton('skeleton/project', basedir)
        with open(os.path.join(self._args[0], 'test_server.py'), 'wb') as fd:
            fd.write(resource_string(__name__, "skeleton/test_server.py.tmpl") % self._args[0])
        makedirs(os.path.join(self._args[0], 'tests/'))

    def _subcommand_linecount(self):
        if len(self._args) < 1 or not os.path.isdir(self._args[0]) or \
            not os.access(self._args[0], os.R_OK):
            show_and_exit("you must provide a directory with read permission")
        total_count = 0 
        for dir, subdirs, files in os.walk(self._args[0]):
            for file in files:
                file = os.path.join(dir, file)
                if os.path.splitext(file)[1] != ".py":
                    continue
                current_count = self.__get_line_count(file)
                print("%s %d" % (file, current_count))
                total_count = total_count + current_count
        print("total count %d" % total_count)

    def __get_line_count(self, filename):
        line_count = 0 
        with open(filename) as fd: 
            for line in fd: 
                if line.strip() and not line.strip().startswith("#"):
                    line_count = line_count + 1 
        return line_count

main = lambda args=None: _DispatchCommand(args or sys.argv[1:]).execute()

