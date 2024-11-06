import os
import yaml
import pandas as pd
from tabulate import tabulate

# Define the directory to scan
directory_to_scan = "/OSIR/OSIR/configs/modules"

# List to hold the extracted data
data = []

# Recursively scan the directory for .yml files
for root, dirs, files in os.walk(directory_to_scan):
    for file in files:
        if file.endswith(".yml"):
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as yml_file:
                try:
                    content = yaml.safe_load(yml_file)
                    # Extract the required fields
                    filename = file
                    description = content.get('description', '')
                    author = content.get('author', '')
                    version = content.get('version', '')
                    processor_type = ', '.join(content.get('processor_type', []))
                    tool_path = content.get('tool', {}).get('path', '')
                    os_field = content.get('os', '')

                    # Append the extracted data to the list
                    data.append([os_field, filename, description, author, version, processor_type, tool_path])
                except yaml.YAMLError as exc:
                    print(f"Error parsing {file_path}: {exc}")

# Create a DataFrame from the extracted data
df = pd.DataFrame(data, columns=['OS', 'Filename', 'Description', 'Author', 'Version', 'Processor Type', 'Tool Path'])

# Sort the DataFrame by OS first and then alphabetically by Filename
df = df.sort_values(by=['OS', 'Filename'])

# Replace '|' characters with a space in all string entries of the DataFrame
df = df.replace(r'\|', ' ', regex=True)


# Convert the DataFrame to an RST table
def df_to_rst_table(df):
    rst_table = []
    rst_table.append("Supported Modules")
    rst_table.append("=================")
    rst_table.append("")
    rst_table.append(".. list-table:: Extracted Module Information")
    rst_table.append("   :header-rows: 1")
    rst_table.append("")

    # Append the header
    header = "   * - " + "\n     - ".join(df.columns)
    rst_table.append(header)

    # Append the rows
    for row in df.itertuples(index=False, name=None):
        row_str = "   * - " + "\n     - ".join(str(item) if item else "" for item in row)
        rst_table.append(row_str)

    return "\n".join(rst_table)


rst_table = df_to_rst_table(df)

# Save the RST table to a file
output_file = "source/extracted_module_info.rst"
with open(output_file, 'w') as f:
    f.write(rst_table)

print(f"RST table saved to {output_file}")


# Generate Markdown table
def df_to_markdown_table(df):
    markdown_lines = []
    markdown_lines.append("# Supported Modules")
    markdown_lines.append("")
    markdown_lines.append(tabulate(df, headers='keys', tablefmt='pipe', showindex=False))
    return "\n".join(markdown_lines)


markdown_table = df_to_markdown_table(df)

# Save the Markdown table to a file
output_md_file = "source/extracted_module_info.md"
with open(output_md_file, 'w') as f:
    f.write(markdown_table)

print(f"Markdown table saved to {output_md_file}")
