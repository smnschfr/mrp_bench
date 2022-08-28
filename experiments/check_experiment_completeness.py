# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file or the repository https://github.com/boschresearch/mrp-bench.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
# import seaborn as sb
import argparse
import os
import yaml
import pandas as pd
import pprint


# converts yaml to flattened pandas dataframe
def get_df_from_file(file):
    with open(file, 'r') as stream:
        try:
            d = yaml.safe_load(stream) # d for dict
        except yaml.YAMLError as exc:
            print(exc)

    # flatten nested config
    df = pd.json_normalize(d, sep='.')
    return df

# pass folder as arg
if __name__ == "__main__":
    # check args
    help = '''
    Checks which parameters differ across scenarios and which range they encompass.
    Outputs information about these ranges so that experiment composition can be analyzed.
    Note: the script does not check if the setting in question is actually used in the specific configuration.
    For example, the suboptimality factor setting for some algorithm does not matter if is not the algorithm being used.
    '''
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('--folder', '-f', type=str, required=True,
                        help='Relative or absolute path to the folder containing experiment yamls.')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    path_to_folder = args.folder
    print(f'Checking {path_to_folder}.')

    files = next(os.walk(path_to_folder), (None, None, []))[2]
    files = [os.path.join(path_to_folder, file) for file in files if file.endswith('yaml')]

    if len(files) < 2:
        print(f'{len(files)} YAMLs found in {path_to_folder}. At least 2 are needed.')
        exit(1)
        
    print(f'Total number of experiments: {len(files)}')

    params = {}
    # iterate over the list
    for file in files[:]:
        # update dict where necessary
        df = get_df_from_file(file)
        for key, value in zip(list(df), df.values.tolist()[0]):
            # ignore metrics, we only check the configs
            # also maps and paths
            if (not key.startswith('metric') 
            and not key.startswith('config.maps') 
            and not 'pathto' in key.lower()):

                # add param if necessary
                if not key in params:
                    params[key] = {}
                # add value of param (or increase counter)
                if value in params[key]:
                    params[key][value] += 1
                else:
                    params[key][value] = 1

    # identify interesting params
    params_filtered = {}
    for param, values in params.items():
        if len(values) > 1:
            params_filtered[param] = values


    pprint.pprint(params_filtered)