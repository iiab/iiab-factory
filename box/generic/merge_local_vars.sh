#!/usr/bin/python
# Takes one and optionally two paramters:
#   full path and name of file to merge with local_vars
#   -p flag to preserve local_vars values

# normal behavior is that the merge file takes precedence over local_vars
# if the -p flag is present local_vars takes precedence over the merge file

import sys, yaml, os.path, argparse

local_vars = {}
merged_vars = {}

var_path = '/opt/iiab/iiab/vars/'

parser = argparse.ArgumentParser(description="Merge a file with local_vars")
parser.add_argument("file_path", help="the full path to the file you want to merge")
parser.add_argument("-p", "--preserve", help="preserve local_var values", action="store_true")

args = parser.parse_args()

merge_file = args.file_path

if not os.path.isfile(merge_file):
    print "File " + merge_file + " not found."
    sys.exit(1)

try:
    f = open(var_path + 'local_vars.yml')
    local_vars = yaml.load(f)
    f.close

except:
    pass # OK if local_vars does not exist

if  type(local_vars) == type(None):
    local_vars = {}

try:
    f = open(merge_file)
    file_vars = yaml.load(f)
    f.close

    if args.preserve:
        merged_vars = file_vars.copy()
        merged_vars.update(local_vars)
        print "preserving values in local_vars"
    else:
        merged_vars = local_vars.copy()
        merged_vars.update(file_vars)
        print "overriding values in local_vars with " + merge_file

    with open(var_path + 'local_vars.yml', 'w') as outfile:
        yaml.dump(merged_vars, outfile, default_flow_style=False)

except:
    print("Merge unsuccessful; error:", sys.exc_info()[0])
    sys.exit(1)

print "File " + merge_file + " merged into local_vars."
