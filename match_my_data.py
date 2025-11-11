# %% SETUP
# -*- coding: utf-8 -*-
"""
Just trying to use the Ben Miroglio software pymatch to optimize 1:1 group 
matching by age +/- handedness for a structural MRI study. 

Kevin J. Black, M.D., Sept. 5, 2025

"""

import pandas as pd
import numpy as np
import sys

# Which group is cases
case_group = 'PTD'
control_group = 'TS'
# case_group = 'TS'
# control_group = 'none'

# %% FIRST: just link the data from scan and scan_day to the list of kids,
# limited to the 4th MRI-sequence group in Suppl. Table 1

# %% Set constants like file names

DEBUG = False

age_close_enough_epsilon = 0.05 # detecting nearly-the-same dates like screening visit
    # and scan visit; value is in years (0.05 -> 18+ days, or similar to half of the rounded 
    # age accuracy, i.e. 0.1) )
how_close_years = 1.01  # How close a control has to be to a case, in years 
    # This is for the actual matching.

nt_fs_filenameroot = "C:/Users/kevin/src/matching/"

enigma_filename = ("C:/Users/kevin/Box/Black_Lab/projects/TS/ENIGMA-TS/data/" +
                   "ENIGMA-TS_covariates_table_2025-09-11.xlsx")
# sheet_names = ["scan_day", "scan"]
# Alternatively:
# data = pd.read_excel(enigma_filename,sheet_name=[*sheet_names])
# That returns a dictionary of two pandas DataFrames,
# accessed e.g. data['scan'].columns
# But that's a little silly and cumbersome for my limited use here.

one_scan_per_subject_filename = (nt_fs_filenameroot + "one_scan_per_subject.csv")
ready_to_match_filename = (nt_fs_filenameroot + "ready_to_match.csv")

# %% Read in needed variables from the "scan_day" and "scan" sheets.
try:
    scan_day = pd.read_excel(enigma_filename, sheet_name="scan_day",
                             usecols=['session_ID',
                                      'scanner_make_model', 'scanner_identifier',
                                      'age_at_scan', 'study_subject_ID',
                                      'tic_diagnosis_current'])
except Exception as e:
    print(f"An error occurred while reading {enigma_filename}: {e}")
    sys.exit(1)
# 1371 rows

try:
    scan = pd.read_excel(enigma_filename, sheet_name="scan",
                         usecols=['session_ID', 'transmit_coil', 'receive_coil',
                                  'pulse_sequence', 'TR', 'TE', 'TI', 'flip_angle',
                                  'bandwidth', 'FoV', 'matrix', 'voxel_size',
                                  'partial_Fourier', 'phase_resolution',
                                  'slice_resolution', 'average',
                                  'study_subject_ID'])
except Exception as e:
    print(f"An error occurred while reading {enigma_filename}: {e}")
    sys.exit(1)
# 1371 rows

# %% THIS TIME GET "boys" AND "girls" SHEETS FROM cleaned_data_2025-11-10.xlsx

boygirl_filenameroot = "C:/Users/kevin/Box/Black_Lab/projects/TS/New_Tics_R01/papers/2024_screening_FS_vs_ctls/"
boygirlfile = (boygirl_filenameroot + "cleaned_data_2025-11-10.xlsx")
boy_filename = nt_fs_filenameroot + "boys.csv"
girl_filename = nt_fs_filenameroot + "girls.csv"

try:
    who1 = pd.read_excel(boygirlfile, sheet_name="all_data",
                usecols = ['participant_ID','study_subject_ID','tic_dx','sex_at_birth','handedness',
                    'age_at_scan','best_ygtss_impairment','best_ygtss_tts','duration_of_tics_(days)'])
except Exception as e:
    print(f"An error occurred while reading {boygirlfile}: {e}")
    sys.exit(1)
# Nrows should be 392

who1.rename(columns={'tic_dx': 'dx_group'}, inplace=True)  
# I checked & in "cleaned_data_....xlsx", the only diagnoses listed are 'PTD', 'none', and 'TS'.

# Output the boys file and the girls file (because that's what the rows below expect). 

who2 = who1.loc[(who1['dx_group']==case_group) | (who1['dx_group']==control_group)]


try:
    who2.loc[who2['sex_at_birth']=='M'].to_csv(boy_filename, index=False)
except Exception as e:
    print(f"An error occurred while writing {boy_filename}: {e}")
    sys.exit(1)
try:
    who2.loc[who2['sex_at_birth']=='F'].to_csv(girl_filename, index=False)
except Exception as e:
    print(f"An error occurred while writing {girl_filename}: {e}")
    sys.exit(1)



# %% Read in the "boys" and "girls" sheets and concatenate them into "who"
try:
    nt_fs_filename = nt_fs_filenameroot + "boys.csv"
    boys = pd.read_csv(nt_fs_filename)
except Exception as e:
    print(f"An error occurred while reading {nt_fs_filename}: {e}")
    sys.exit(1)
# boys.shape = (177, 10)

try:
    nt_fs_filename = nt_fs_filenameroot + "girls.csv"
    girls = pd.read_csv(nt_fs_filename)
except Exception as e:
    print(f"An error occurred while reading {nt_fs_filename}: {e}")
    sys.exit(1)
# girls.shape = (111, 10)

who = pd.concat([boys, girls], ignore_index=True)
# 288 rows, 10 columns

# %% define close_enough functions


def close_enough_scalar(scalar1, scalar2, epsilon=age_close_enough_epsilon):
    return (np.abs(scalar1-scalar2) <= epsilon)  # Boolean


def close_enough(array, scalar, epsilon=age_close_enough_epsilon):
    """
    Deals with some ages given as years to one decimal point and others
    given as days/365-ish. 

    Parameters
    ----------
    array : numpy array of floats (e.g., ages)
    scalar : float to which each array entry is being compared for 
        approximate equivalence
    epsilon : float, optional : how close one has to be to be considered
        "close enough," e.g. "basically the same age".
        DESCRIPTION. The default is age_close_enough_epsilon, specified above.

    Returns
    -------
    numpy array of boolean values corresponding to entries in age_array that 
        are "basically the same age" as (i.e. within epsilon of) the supplied 
        value age_scalar.
    """
    return (np.abs(array-scalar) <= epsilon)  # Boolean Numpy array


# %% Find which scan_day row for each SSID is the who row with the same SSID

# initially failed because CTS228 & CTS230 == NaN for age_at_scan in scan_day
# temporary fix--also made new Excel tables in same directory as these were
#   read from
scan_day.loc[scan_day['study_subject_ID'].isin(['CTS228', 'CTS230']),
             'age_at_scan'] = [7.7, 10.2]

# And NT897 had wrong data. See emails 2025-09-13 and following. Correcting:
scan_day.loc[scan_day['study_subject_ID']=='NT897', 'age_at_scan'] = 5.8
    # scan was 5 days after screen visit
scan_day.loc[scan_day['study_subject_ID']=='NT897', 
             'session_ID'] = 'ses-screen'  # I checked the file 
    # ENIGMA_scan_sheet_info_from_RIS.csv and it shows same scanner, same
    # parameters for NT897's ses-screen and ses-12mo

# Thanks, gpt.wustl.edu, for the following:
# Join on the study_subject_ID to have both dataframes in one
merged = pd.merge(who, scan_day, on='study_subject_ID',
                  suffixes=('_who', '_scan_day'))
# 432 rows

# Create a column for the absolute difference in ages
merged['age_diff'] = abs(merged['age_at_scan_who'] -
                         merged['age_at_scan_scan_day'])

# Find the row with the smallest age difference for each study_subject_ID
idx = merged.groupby('study_subject_ID')['age_diff'].idxmin()
# 288 rows

# Subset the dataframe to these rows
closest_visit = merged.loc[idx]
"""
closest_visit.shape
    Out[134]: (288, 17)
closest_visit['age_diff'].max()
    Out[135]: 0.10000000000000142
"""

closest_visit['case_control'] = \
    closest_visit['dx_group'].case_when([(closest_visit['dx_group'].eq(case_group), 'case'),
                                         (closest_visit['dx_group'].eq(control_group), 'control'),
                                         (np.full(len(closest_visit), True), None),
                                        ],
                                       )

# Output the new, improved file with all the variables we need and only one
# scan session per participant

try:
    closest_visit.to_csv(one_scan_per_subject_filename, index=False)
except Exception as e:
    print(f"An error occurred while writing {one_scan_per_subject_filename}: {e}")
    sys.exit(1)

# %% select rows in "scan" matching 2500/2.9/1070, 64-channel, 1x1x1
scan_matching_params = scan[close_enough(scan['TR'], 2500, epsilon=5) &
                            close_enough(scan['TE'], 2.9, .03) &
                            close_enough(scan['TI'], 1070, 20) &
                            scan['receive_coil'].str.contains("64") &
                            (scan['voxel_size'] == "1x1x1")]
# Out: df with 247 rows x 17 columns

# %% merge the results from the 2 cells above, so we only have one row per 
#    participant and only those scans that use the scanner and the MPRAGE sequence 
#    parameters in the largest such scanner-sequence group.  
#    Then print this merged dataframe to disk as a .CSV file.

ready_to_match = pd.merge(closest_visit, scan_matching_params, how='inner',
                            on = ['study_subject_ID', 'session_ID'])

try:
    ready_to_match.to_csv(ready_to_match_filename, index=False)
except Exception as e:
    print(f"An error occurred while writing {ready_to_match_filename}: {e}")
    sys.exit(1)



# %% End of program  (temporarily)

# TODO: save or print the matching: SSID, sex, age, case/control
sys.exit(0)

# ===================================================================== #


# %% Create the variable “total controls per case”
# https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-021-01256-3#citeas
# I'm not positive what those variables mean even after working through the paper: 
"""
The variable “total controls per case” depicts the total pool of controls available 
for **each case**, whereas the variable “frequency of controls” depicts how many times 
a control was assigned to a case. Both variables were essential for constructing the 
algorithm. The variable “total controls per case” was necessary in order to assign 
the control to the case that had the least number of controls to pool from. The 
“frequency of controls” variable was required, since the controls with the lowest 
frequency were matched first, leaving the controls with the highest frequency 
available for the next cases.
"""
# I think "each case" means the total_cont_per_case variable must be an array. 
# Ah, here it is: 
# "@param total_cont_per_case total number of controls that are available for each case"
# And Fig. 1 shows Tot_Con means what I thought, i.e. for each case, it's the number
# of controls that are close enough to that case.

# thanks to gpt.wustl.edu for help with the following code:

def cont_per_case_group(data, group, age_tolerance):
    """ return a data series with # of age-matched controls for each case in data[group],
        where group defines a subset of rows of data. Age matching is done within 
        age_tolerance years.
    """
    # use rule "group" to select cases that define this group
    df = data[group]

    # Initialize cont_per_case as a series with None values
    cont_per_case = pd.Series([None] * len(df), index=df.index)

    # Compute cont_per_case
    for i, row in df.iterrows():
        if row['case_control'] == 'case':
            case_age = row['age_at_scan_scan_day']
            count = len(
                df[
                    (df['case_control'] == 'control') &
                    (np.abs(df['age_at_scan_scan_day'] - case_age) <= how_close_years)
                ]
            )
            cont_per_case[i] = count
            # or df[i,'cont_per_case'] = count

    return(cont_per_case)


# %% Create the variable “frequency of controls”, then sort by it
# The freq_controls is apparently similar to cont_per_case, but counted by the 
# controls, not the cases.






# %% Now do the matching, per Mamouris et al 2021:
# Thanks gpt.wustl.edu for translating this R code into Python:
# TODO: In their original, iterations_per_round() was an independent function, defined first (q.v.)

def optimal_matching(total_database, n_con, cluster_var, Id_Patient, total_cont_per_case, case_control, with_replacement=False):
    if n_con > total_database[total_cont_per_case].max():
        raise ValueError(f"Number of controls (n_con) should be less than or equal to the total number of controls per case ({total_database[total_cont_per_case].max()}).")

    if with_replacement:
        final_data = total_database.groupby(cluster_var).head(n_con + 1)
        return final_data
    else:
        def iterations_per_round(dataset):
            one_to_one = dataset.groupby(cluster_var).head(2)
            dup_con = one_to_one.drop_duplicates().groupby(Id_Patient).filter(lambda x: len(x) > 1)
            dup_con = dup_con.sort_values(by=[Id_Patient, total_cont_per_case]).groupby(Id_Patient).head(1)
            
            if len(dup_con) > 0:
                one_to_one = pd.concat([one_to_one[~one_to_one[Id_Patient].isin(dup_con[Id_Patient])], dup_con]).sort_values(by=[cluster_var, case_control])
                one_to_one['mat_per_case'] = one_to_one.groupby(cluster_var)[cluster_var].transform('count') - 1
                case_cntrl_1st_wave = one_to_one[one_to_one['mat_per_case'] == 1].drop(columns='mat_per_case')
                dataset = dataset[~dataset[cluster_var].isin(case_cntrl_1st_wave[cluster_var])]
                dataset = dataset[~dataset[Id_Patient].isin(case_cntrl_1st_wave[Id_Patient])]
            else:
                one_to_one['mat_per_case'] = one_to_one.groupby(cluster_var)[cluster_var].transform('count') - 1
                case_cntrl_1st_wave = one_to_one[one_to_one['mat_per_case'] == 1].drop(columns='mat_per_case')
                dataset = None
                
            return {"case_cntrl_1st_wave": case_cntrl_1st_wave, "dataset": dataset, "dup_con": dup_con}
        
        dup_con = 1
        wave_data = []
        counter = 0
        tmp_database = total_database.copy()
        waves_round = []

        while dup_con > 0:
            counter += 1
            datasets = iterations_per_round(tmp_database)
            wave_data.append(datasets["case_cntrl_1st_wave"])
            tmp_database = datasets["dataset"]
            dup_con = len(datasets["dup_con"])

        waves_round.append(pd.concat(wave_data))

        if n_con > 1:
            waves_round_cont = []
            for i_con in range(2, n_con + 1):
                for i_wave in range(len(waves_round)):
                    tmp_waves_round = waves_round[i_wave]
                    waves_round_cont.append(tmp_waves_round[tmp_waves_round[case_control] == "control"])
                waves_round_merge = pd.concat(waves_round_cont)
                tmp_database = total_database.copy()
                tmp_database = tmp_database[~tmp_database[Id_Patient].isin(waves_round_merge[Id_Patient])]
                tmp_database[total_cont_per_case] = tmp_database.groupby(cluster_var)[total_cont_per_case].transform('count') - 1
                dup_con = 1
                wave_data = []
                counter = 0

                while dup_con > 0:
                    counter += 1
                    datasets = iterations_per_round(tmp_database)
                    wave_data.append(datasets["case_cntrl_1st_wave"])
                    tmp_database = datasets["dataset"]
                    dup_con = len(datasets["dup_con"])

                waves_round.append(pd.concat(wave_data))

            final_data = waves_round[0]
            for I_add_con in range(2, n_con + 1):
                tmp_waves_round = waves_round[I_add_con - 1]
                final_data = pd.concat([final_data, tmp_waves_round[tmp_waves_round[case_control] == "control"]])
        else:
            final_data = waves_round[0]

        return final_data

# Example usage:

# Load your dataset
# total_database = pd.read_csv("your_file.csv")

# Example usage of the function:
# final_data = optimal_matching(total_database, n_con=2, cluster_var='cluster_case', Id_Patient='Patient_Id', 
#                               total_cont_per_case='total_control_per_case', case_control='case_control')

"""
**Function Explanation:**

1. **Input Checks and Initial Setup:**
    - Initial validation to ensure `n_con` does not exceed the maximum number of controls available per case.
    - If `with_replacement` is `True`, it simply groups by `cluster_var` and selects the first `n_con + 1` cases.
    - Otherwise, it proceeds with the matching process without replacement.

2. **Iterations Per Round:**
    - This function performs data manipulation and filtering to match cases and controls iteratively.
    - It computes `one_to_one`, identifies duplicated controls (`dup_con`), and appropriately updates the dataset by removing matched controls in each iteration.
 
3. **Main Matching Logic:**
    - Uses a `while` loop to perform the matching until there are no duplicated controls left.
    - Stores matched results of each round in `wave_data`.
    - If more than one control is needed (`n_con > 1`), it performs multiple rounds and filters controls for each round.
    - Combines the results of all rounds into `final_data`.

4. **Return:**
    - Returns the final matched dataset containing cases and corresponding controls.

Make sure to adjust the script based on the actual column names and your specific data requirements.
"""

# %% End of program

# TODO: save or print the matching: SSID, sex, age, case/control
sys.exit(0)

# ===================================================================== #
