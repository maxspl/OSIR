Specific fields can be reused:
	- {endpoint_name}: required to be specified in preprocessor
	- {input_file_name} : input filename without extension (up to 2 extensions)
	- {input_file} : used in cmd to specify input file
	- {output_file} : used in cmd to specify output file
	- {module}: module name
	- {case_directory}: name of the root directory of file processing
	- processed_files: default directory used for Splunk indexing. Name cannot be modified
	- {output_file_name}: output name given by the parsing tool (particularely useful is output is multiple files)
	- {index}: index created during pre-processing to manage and enrich (eg. Resolve original file path) files to process

Preprocess:
	- Default output is by default in input directory
	- After preprocess: an index must be created 
Input dir name	Profile	Modules	Input	Process_status	Status_details	Output_name	Os 	Os_processor

Process and postprocess:
	- Cannot run if index is not found
	- Update index

