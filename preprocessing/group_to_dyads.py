from pprint import pprint
import re
import os
from pathlib import Path
from itertools import combinations
import shutil

# -------
# HELPERS
# -------
def parse_filename(filename):
    """
    Parses a filename using a predefined regular expression pattern and extracts named substrings.
    Args:
        filename (str): The filename to be parsed.
    Returns:
        dict: A dictionary containing the named substrings extracted from the filename if the pattern matches, otherwise empty dict.
    """
    pattern = re.compile(NAMING_PATTERN)
    match = pattern.match(filename)
    if match:
        return match.groupdict()
    else:
        return {}
def find_dict_by_field(dicts, field, value):
    return next((d for d in dicts if d.get(field) == value), None)

# ----------------------------------------
# I/O DATA - SET INPUT & OUTPUT PATHS HERE
# ----------------------------------------
# group data directory: one subdirectory per subject with files per condition
# [path relative to script location]
INPUT_DIR_GROUP = Path('../data/groups/3003')
# output directory: one subdirectory for each possible dyad for each condition with one file per subject
OUTPUT_DIR = Path('../data/groups/dyads_3003')

# the structure of the xlsx files in the input directory
NAMING_PATTERN = r'(?P<type>[^_]+)_(?P<group>[^_]+)_(?P<subject>[^.]+)_(?P<condition>[^.]+)\.xlsx'

# ----------------
# PREPARE I/O DIRS
# ----------------
input_dir_group_abs = Path(__file__).parent / INPUT_DIR_GROUP
input_dir_group_abs = input_dir_group_abs.resolve()
output_dir_abs = Path(__file__).parent / OUTPUT_DIR
output_dir_abs = output_dir_abs.resolve()
# Remove the entire output directory if it exists, then recreate it as empty
if output_dir_abs.exists():
    for item in output_dir_abs.iterdir():
        if item.is_dir():
            for subitem in item.iterdir():
                subitem.unlink()
            item.rmdir()
        else:
            item.unlink()
else:
    output_dir_abs.mkdir(parents=True)

# ---------------
# PARSE INPUT DIR
# ---------------
# get list of per-subject directories
subject_ids = [subdir for subdir in os.listdir(input_dir_group_abs) if os.path.isdir(os.path.join(input_dir_group_abs, subdir))]
subjects = [{'id': subject_id, 'dir': Path.joinpath(input_dir_group_abs, subject_id)} for subject_id in subject_ids]

# append information about per-condition files to subject data
for subject in subjects:
    xlsx_files = [f for f in os.listdir(subject['dir']) if f.endswith('.xlsx')]
    xlsx_files_info = [{'path': Path.joinpath(subject['dir'], f), **parse_filename(f)} for f in xlsx_files]
    subject['conditions'] = [{'condition': d['condition'], 'path': d['path']} for d in xlsx_files_info]

# ---------------------
# MAKE AND EXPORT DYADS
# ---------------------
# dyads: all possible combinations of subjcts
dyads = list(combinations([s for s in subjects], 2))

# for each dyad , for each condition, create a subdirectory in the output dir with two xlsx files 
for (subject_0, subject_1) in dyads:
    conditions_sub_0 = [c['condition'] for c in subject_0['conditions']]
    conditions_sub_1 = [c['condition'] for c in subject_1['conditions']]
    common_conditions = set(conditions_sub_0) & set(conditions_sub_1)
    for condition in common_conditions:
        # get xlsx files for current condition
        subject_0_xlsx_path = find_dict_by_field(subject_0['conditions'], 'condition', condition)['path']
        subject_1_xlsx_path = find_dict_by_field(subject_1['conditions'], 'condition', condition)['path']

        # make output subdir
        output_subdir = f"dyad_{subject_0['id']}_{subject_1['id']}_{condition}"
        output_subdir_path = Path.joinpath(output_dir_abs, output_subdir)
        output_subdir_path.mkdir(parents=True, exist_ok=True)
        dest_0 = output_subdir_path / Path(subject_0_xlsx_path).name
        dest_1 = output_subdir_path / Path(subject_1_xlsx_path).name
        shutil.copy(subject_0_xlsx_path, dest_0)
        shutil.copy(subject_1_xlsx_path, dest_1)