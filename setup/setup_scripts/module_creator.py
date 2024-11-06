import sys
import os
import yaml
from collections import OrderedDict

# Si vous testez, vous pouvez assigner des valeurs directement
module_name = sys.argv[1]
module_description = sys.argv[2]
module_scope = sys.argv[3]
processing_os = sys.argv[4]
module_input_type = sys.argv[5]
module_input_regex = sys.argv[6]
module_input_file_regex = sys.argv[7]
module_output_type = sys.argv[8]
module_output_format = sys.argv[9]
module_output_name = sys.argv[10]
module_endpoint_regex = sys.argv[11]
module_processor_type = sys.argv[12]
module_tool_name = sys.argv[13]
module_tool_argument = sys.argv[14]
module_yaml_unix = sys.argv[15]
module_yaml_windows = sys.argv[16]
module_py_unix = sys.argv[17]
module_py_windows = sys.argv[18]
master_dir = sys.argv[19]

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
if module_scope:
    yaml_content['type'] = [module_processor_type]
yaml_content['disk_only'] = False
yaml_content['no_multithread'] = False
if module_processor_type:
    yaml_content['processor_type'] = [module_scope]
yaml_content['processor_os'] = 'unix'

if module_tool_name and module_tool_argument:
    yaml_content['tool'] = OrderedDict()
    yaml_content['tool']['path'] = module_tool_name
    yaml_content['tool']['cmd'] = module_tool_argument

yaml_content['input'] = OrderedDict()
if module_input_type:
    yaml_content['input']['type'] = module_input_type
if module_input_regex:
    yaml_content['input']['path'] = module_input_regex
if module_input_file_regex:
    yaml_content['input']['name'] = module_input_file_regex

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
output_file_path = os.path.join(master_dir, f"{module_name}_module.yml")
with open(output_file_path, 'w') as yaml_file:
    yaml.dump(
        yaml_content, 
        yaml_file, 
        default_flow_style=False, 
        sort_keys=False, 
        Dumper=OrderedDumper
    )

print(f"YAML file created at: {output_file_path}")
