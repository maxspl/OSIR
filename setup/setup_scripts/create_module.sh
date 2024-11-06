#!/bin/bash

# Color variables
ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)

MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MODULE_PY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/src/modules/" &> /dev/null && pwd)
MODULE_YAML=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/configs/modules/" &> /dev/null && pwd)
MODULE_YAML_UNIX=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/configs/modules/unix" &> /dev/null && pwd)
MODULE_YAML_WINDOWS=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/configs/modules/windows" &> /dev/null && pwd)
MODULE_PY_WINDOWS=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/src/modules/windows" &> /dev/null && pwd)
MODULE_PY_UNIX=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )/../../OSIR/src/modules/linux" &> /dev/null && pwd)

# Function to check if a required input is empty and re-ask if needed
function check_input() {
    local input_value="$1"
    local prompt_message="$2"
    while [ -z "$input_value" ]; do
        echo >&2 "${ERROR} The previous value is mandatory."
        read -p "$prompt_message" input_value
    done
    echo "$input_value"
}

# Ask for module type
read -p "${USERINPUT} Do you want a Short or Long creation process ? (short/long): " module_type

if [ "$module_type" == "long" ]; then

    # Collect module details and ensure mandatory fields are filled
    read -p "${USERINPUT} Enter module name: " module_name
    module_name=$(check_input "$module_name" "${USERINPUT} Enter module name: ")

    read -p "${USERINPUT} (OPTIONAL) Enter a description for the module: " module_description
    read -p "${USERINPUT} (OPTIONAL) Enter the processor type (process/pre-process/post-process): " module_processor_type
    read -p "${USERINPUT} The module is processed by a command (external), a custom plugin (internal), or both? (internal/external/both): " module_scope
    module_scope=$(check_input "$module_scope" "${USERINPUT} The module is processed by (internal/external/both): ")

    if [[ "$module_scope" == "external" || "$module_scope" == "both" ]]; then
        read -p "${USERINPUT} Enter the binary name: " module_tool_name
        module_tool_name=$(check_input "$module_tool_name" "${USERINPUT} Enter the binary name: ")
        read -p "${USERINPUT} Enter the argument of the binary: " module_tool_argument
        module_tool_argument=$(check_input "$module_tool_argument" "${USERINPUT} Enter the argument of the binary: ")
    fi  

    read -p "${USERINPUT} The module processes a file or a dir (file/dir): " module_input_type
    module_input_type=$(check_input "$module_input_type" "${USERINPUT} The module processes a file or a dir (file/dir): ")

    read -p "${USERINPUT} Enter the input file/dir path: " module_input_regex
    module_input_regex=$(check_input "$module_input_regex" "${USERINPUT} Enter the input file/dir path: ")

    if [ "$module_input_type" == "file" ]; then
        read -p "${USERINPUT} Enter the input file regex: " module_input_file_regex
        module_input_file_regex=$(check_input "$module_input_file_regex" "${USERINPUT} Enter the input file regex: ")
    fi

    read -p "${USERINPUT} Enter the output type (single_file, multiples_files): " module_output_type
    module_output_type=$(check_input "$module_output_type" "${USERINPUT} Enter the output type (single_file, multiples_files): ")

    if [[ "$module_scope" == "internal" || "$module_scope" == "both" ]]; then
        read -p "${USERINPUT} (OPTIONAL) Enter the output format (json/txt): " module_output_format
    fi

    read -p "${USERINPUT} Enter the output file name, you can refer to the doc to see exposed variable: " module_output_name
    module_output_name=$(check_input "$module_output_name" "${USERINPUT} Enter the output file name: ")

    read -p "${USERINPUT} Enter the endpoint regex, this regex is applied to the input file/dir path: " module_endpoint_regex
    module_endpoint_regex=$(check_input "$module_endpoint_regex" "${USERINPUT} Enter the endpoint regex: ")

    if [[ "$module_scope" == "external" || "$module_scope" == "both" ]]; then
        read -p "${USERINPUT} The module binary must be processed by (windows/unix): " processing_os
        processing_os=$(check_input "$processing_os" "${USERINPUT} The module binary must be processed by (windows/linux): ")
    else
        # Si le module n'est pas external ou both, processing_os par défaut est "linux"
        processing_os="unix"
    fi


    # Integrate the Python code and link each Bash variable to its Python variable
    python3 <<EOF
import os
import yaml
from collections import OrderedDict

module_name = "${module_name}"
module_description = "${module_description}"
module_scope = "${module_scope}"
processing_os = "${processing_os}"
module_input_type = "${module_input_type}"
module_input_regex = "${module_input_regex}"
module_input_file_regex = "${module_input_file_regex}"
module_output_type = "${module_output_type}"
module_output_format = "${module_output_format}"
module_output_name = "${module_output_name}"
module_endpoint_regex = "${module_endpoint_regex}"
module_processor_type = "${module_processor_type}"
module_tool_name = "${module_tool_name}"
module_tool_argument = "${module_tool_argument}"
module_yaml_unix = "${MODULE_YAML_UNIX}"
module_yaml_windows = "${MODULE_YAML_WINDOWS}"
module_py = "${MODULE_PY}"
module_py_unix = "${MODULE_PY_UNIX}"
module_py_windows = "${MODULE_PY_WINDOWS}"
master_dir = "${MASTER_DIR}"

# Définir un Dumper personnalisé pour représenter OrderedDict comme un mapping normal
class OrderedDumper(yaml.SafeDumper):
    pass

def ordered_dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

OrderedDumper.add_representer(OrderedDict, ordered_dict_representer)

# Création du contenu YAML en utilisant OrderedDict pour conserver l'ordre
yaml_content = OrderedDict()
yaml_content['version'] = '1.0'
yaml_content['author'] = 'Show your name !'
yaml_content['module'] = module_name
if module_description:
    yaml_content['description'] = module_description
if processing_os:
    yaml_content['os'] = processing_os
    yaml_content['processing_os'] = processing_os
if module_scope:
    if module_scope == 'both':
        yaml_content['processor_type'] = ['internal','external']
    else:
        yaml_content['processor_type'] = [module_scope]
yaml_content['disk_only'] = False
yaml_content['no_multithread'] = False
if module_processor_type:
    yaml_content['type'] = module_processor_type
yaml_content['processor_os'] = 'unix'

if module_tool_name and module_tool_argument:
    yaml_content['tool'] = OrderedDict()
    yaml_content['tool']['path'] = module_tool_name
    yaml_content['tool']['cmd'] = module_tool_argument

if module_input_type or module_input_regex or module_input_file_regex:
    yaml_content['input'] = OrderedDict()
    if module_input_type:
        yaml_content['input']['type'] = module_input_type
    if module_input_regex:
        yaml_content['input']['path'] = module_input_regex
    if module_input_file_regex:
        yaml_content['input']['name'] = module_input_file_regex

if module_output_type or module_output_format or module_output_name:
    yaml_content['output'] = OrderedDict()
    if module_output_type:
        yaml_content['output']['type'] = module_output_type
    if module_output_format:
        yaml_content['output']['format'] = module_output_format
    if module_output_name:
        yaml_content['output']['output_file'] = module_output_name

if module_endpoint_regex:
    yaml_content['endpoint'] = module_endpoint_regex

# Supprimer les sous-dictionnaires vides
for key in ['tool', 'input', 'output']:
    if key in yaml_content and not yaml_content[key]:
        del yaml_content[key]

# Écriture du fichier YAML en utilisant le Dumper personnalisé
if processing_os == 'unix':
    output_file_path = os.path.join(module_yaml_unix, f"{module_name}.yml")
else:
    output_file_path = os.path.join(module_yaml_windows, f"{module_name}.yml")

with open(output_file_path, 'w') as yaml_file:
    yaml.dump(
        yaml_content, 
        yaml_file, 
        default_flow_style=False, 
        sort_keys=False, 
        Dumper=OrderedDumper
    )

if module_scope == 'both' or module_scope == 'internal':
    if processing_os == 'unix':
        output_file_path = os.path.join(module_py_unix, f"{module_name}.py")
    else:
        output_file_path = os.path.join(module_py_windows, f"{module_name}.py")

    with open(os.path.join(module_py, "sample.py"), 'r') as py_file:
        sample_py = py_file.read()
    
    sample_py = sample_py.replace("MODULE_NAME", f"{module_name}")

    with open(output_file_path, 'w') as py_file_o:
        py_file_o.write(sample_py)

EOF
    if [[ "$processing_os" == "unix" ]]; then
        echo "${GOODTOGO} Your config for the module is at this path: $MODULE_YAML_UNIX/${module_name}.yml"
        if [[ "$module_scope" == "internal" || "$module_scope" == "both" ]]; then
            echo "${GOODTOGO} Your internal module is at this path: $MODULE_PY_UNIX/${module_name}.py"
        fi
    fi
    if [[ "$processing_os" == "windows" ]]; then
        echo "${GOODTOGO} Your config for the module is at this path: $MODULE_YAML_WINDOWS/${module_name}.yml"
        if [[ "$module_scope" == "internal" || "$module_scope" == "both" ]]; then
            echo "${GOODTOGO} Your internal module is at this path: $MODULE_PY_WINDOWS/${module_name}.py"
        fi
    fi

    echo "${GOODTOGO} Everything done! You can test your module in the Web app! See you! ${GOODTOGO}"
else
    read -p "${USERINPUT} Enter module name: " module_name
    module_name=$(check_input "$module_name" "${USERINPUT} Enter module name: ")
    python3 <<EOF
import os
import yaml

module_name = "${module_name}"
module_py = "${MODULE_PY}"
module_yaml = "${MODULE_YAML}"

output_file_path = os.path.join(module_yaml, f"{module_name}.yml")

with open(os.path.join(module_yaml, "sample.yml"), 'r') as yml_file:
    sample_yml = yml_file.read()

sample_yml = sample_yml.replace("module_name", f"{module_name}")

with open(output_file_path, 'w') as yml_file_o:
    yml_file_o.write(sample_yml)

output_file_path = os.path.join(module_py, f"{module_name}.py")

with open(os.path.join(module_py, "sample.py"), 'r') as py_file:
    sample_py = py_file.read()

sample_py = sample_py.replace("MODULE_NAME", f"{module_name}")

with open(output_file_path, 'w') as py_file_o:
    py_file_o.write(sample_py)

EOF
    echo "${GOODTOGO} Your config for the module is at this path: $MODULE_YAML/${module_name}.yml"
    echo "${GOODTOGO} Your internal module is at this path: $MODULE_PY/${module_name}.py"
fi
