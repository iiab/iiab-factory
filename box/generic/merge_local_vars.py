#!/usr/bin/python3
# Takes one and optionally two paramters:
#   full path and name of file to merge with local_vars
#   -p flag to preserve local_vars values

# normal behavior is that the merge file takes precedence over local_vars
# if the -p flag is present local_vars takes precedence over the merge file

import sys, yaml, os.path, argparse

local_vars = {}
merge_vars = {}
delta_vars = {}

var_path = '/etc/iiab/'
iiab_local_vars_file = var_path + 'local_vars.yml'
default_vars_file = '/opt/iiab/iiab/vars/default_vars.yml'

def main():
    parser = argparse.ArgumentParser(description="Merge a file with local_vars")
    parser.add_argument("file_path", help="the full path to the file you want to merge")
    parser.add_argument("-p", "--preserve", help="preserve local_var values", action="store_true")
    parser.add_argument("-c", "--nocomment", help="don't copy comments", action="store_true")
    parser.add_argument("-d", "--nodefault", help="don't copy values same as default", action="store_true")

    args = parser.parse_args()

    merge_file = args.file_path

    if not os.path.isfile(merge_file):
        print("File " + merge_file + " not found.")
        sys.exit(1)

    try:
        local_vars = read_yaml(iiab_local_vars_file)
    except:
        pass # OK if local_vars does not exist

    if  type(local_vars) == type(None):
        local_vars = {}

    if args.preserve:
        print("preserving values in local_vars")
    else:
        print("overriding values in local_vars with " + merge_file)

    try:
        merge_vars = read_yaml(merge_file)

        for key in merge_vars:
            if key not in local_vars: # local vars values take precedence
                delta_vars[key] = merge_vars[key]
            else:
                 if not args.preserve: # merge vars values take precedence
                     delta_vars[key] = merge_vars[key]
    except:
        print("Merge unsuccessful; error:", sys.exc_info()[0])
        sys.exit(1)

    write_iiab_local_vars(delta_vars, strip_comments=args.nocomment, strip_defaults=args.nodefault)

    print("File " + merge_file + " merged into local_vars.")

# from adm_lib
def write_iiab_local_vars(delta_vars, strip_comments=False, strip_defaults=False):
    output_lines = merge_local_vars(delta_vars, strip_comments=strip_comments, strip_defaults=strip_defaults)
    with open(iiab_local_vars_file, 'w') as f:
        for line in output_lines:
            f.write(line)

def merge_local_vars(delta_vars, strip_comments=False, strip_defaults=False):
    local_vars_lines = []
    output_lines = []
    local_vars = {}
    default_vars = {}
    defined = {}
    undefined = {}
    defaults_to_skip = []
    separator_found = False

    local_vars = read_yaml(iiab_local_vars_file)
    with open(iiab_local_vars_file) as f:
        local_vars_lines = f.readlines()

    default_vars = read_yaml(default_vars_file)
    if strip_defaults:
        for key in local_vars:
            if local_vars[key] == default_vars.get(key, None):
                defaults_to_skip.append(key) # any keys where local = default

    for key in delta_vars:
        if strip_defaults: # remove any keys that have default value
            if delta_vars[key] == default_vars.get(key, None):
                if key not in defaults_to_skip:
                    defaults_to_skip.append(key) # any keys where delta = default
                continue
        if key in local_vars:
           defined[key] = delta_vars[key]
           if key in defaults_to_skip:
               defaults_to_skip.remove(key) # any keys where local = default, but delta != default
        else:
           undefined[key] = delta_vars[key]

    for line in local_vars_lines:
        hash_pos = line.find('#')
        if hash_pos == 0:
            if not strip_comments:
                output_lines.append(line)
            if line.startswith("# IIAB -- following variables"):
                separator_found = True
            continue

        for key in defined:
            key_pos = line.find(key)
            if key_pos < 0:
                continue
            else:
                if hash_pos != -1 and hash_pos < key_pos: # key is commented
                    continue
                else: # substitute delta value
                    line = line.replace(str(local_vars[key]), str(defined[key]))
        # at this point substitutions are done

        copy_line = True
        if strip_comments and line == '\n':
            copy_line = False
        if strip_comments and hash_pos > 0 and line[:hash_pos].isspace(): # indented comment line
            copy_line = False
        if copy_line: # still not rid of this line?
            for key in defaults_to_skip: # skip keys marked for removal
                key_pos = line.find(key)
                if key_pos < 0:
                    continue
                else:
                    copy_line = False
                    break

        if copy_line:
            output_lines.append(line)

    if not separator_found:
        output_lines.append("\n\n############################################################################\n")
        output_lines.append("# IIAB -- following variables are first set by browser via the Admin Console\n")
        output_lines.append("#  They may be changed via text editor, or by the Admin Console.\n\n")

    for key in undefined:
        line = str(key) + ': ' + str(undefined[key])
        line += '\n'
        output_lines.append(line)

    return output_lines

# from adm_lib
def read_yaml(file_name, loader=yaml.SafeLoader):
    try:
        with open(file_name, 'r') as f:
            y = yaml.load(f, Loader=loader)
            return y
    except:
        raise

if __name__ == "__main__":
     main()
