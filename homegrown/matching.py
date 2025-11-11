# -*- coding: utf-8 -*-
"""
This program is meant to match two groups, cases and controls, where using 
every case is the priority, and controls are matched without replacement.

A data file as CSV should be given as a command-line argument.
As written (ca. lines 70-72), cases are those lines in the input file with 
'dx_group' == 'PTD', and controls are those with 'dx_group' == 'none'.

Saved on Fri Sep  5 18:50:58 2025

@author: Kevin J. Black
"""

import sys
import numpy as np
import pandas as pd

DEBUG = False
VERBOSE = False
# TODO: make these optional command-line parameters

epsilon = 0.0001  # Adjust for your own data. To deal with machine issues like
    # "this variable holds 0.99999999999 and I'm looking for values==1.0."
def close_enough(anarray, target, epsilon, absval=False):
    """Find elements of an array that are "close enough" to the target value. 

    Parameters:
        anarray (numpy array): array whose elements are to be tested to see
            if they are "close enough" to target
        target (int or float): Value being tested in the array
        epsilon (int or float): How close is "close enough". 
            Must be non-negative.
        absval (boolean): if True, success not only if the array value
            is close enough to target, but also if |array value| is close
            enough to |target|. E.g. counts -3 and 3 as close enough to -3.

    Returns:a tuple of arrays, one for each dimension of the input array, 
        containing the indices where elements of array are within epsilon of
        target. E.g. (array([ 4, 16]), array([ 0, 43])) means that elements 
        [4,0] and [16,43] in a 2-D input array are close enough to target.
        
    """
    assert epsilon >= 0, "epsilon must be nonnegative"
    if absval:
        return np.where(np.abs(np.abs(anarray) - np.abs(target)) <= epsilon)
    return np.where(np.abs(anarray - target) <= epsilon)

# Read CSV filename from command line arguments
if len(sys.argv) < 2:
    print("Please provide the CSV file name as a command line argument.")
    sys.exit(1)

file_name = sys.argv[1]

try:
    # Attempt to load CSV data
    data = pd.read_csv(file_name)
except FileNotFoundError:
    print(f"no file: {file_name}")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"empty data or header in {file_name}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred while reading {file_name}: {e}")
    sys.exit(1)

if VERBOSE:
    print(f"Successfully loaded file: {file_name}")

# Separate data into cases and controls
cases = data[data['dx_group'] == 'PTD']
controls = data[data['dx_group'] == 'none']
# TODO: let user supply these 3 header field names to this program

ncase = len(cases)
nctrl = len(controls)

age_cases = cases['age_at_scan'].values
age_controls = controls['age_at_scan'].values
# pandas documentation says "We recommend using DataFrame.to_numpy() instead."

# Step 1: Create ncase x nctrl difference array
diff_age = np.zeros((ncase, nctrl))
for i in range(ncase):
    for j in range(nctrl):
        diff_age[i, j] = age_controls[j] - age_cases[i]

# Create a copy of the array called "working"
working = diff_age.copy()

# Step 2: Create a 1 x ncase array "match" with all values set to np.nan
match = np.full(ncase, np.nan)  # Setting as NaN makes match a float type

# Step 3: Perform matching
paths = 1   # An upper bound on the number of paths through the data, i.e.
            # if there are 3 pairs distance 0.0 and 2 pairs distance 0.1,,
            # and no other ties, then there are at most 3 x 2 = 6 ways
            # for us to cross out case & control pairs.
for _ in range(ncase):
    # Step 3.1: Find the index (i, j) for the smallest absolute difference in the working array
    min_value = np.nanmin(np.abs(working))
    # min_indices = np.where(np.abs(working) == min_value)
    min_indices = close_enough(working, min_value, epsilon, absval=True)
    minlength = len(min_indices[0])
    
    if minlength > 1:
        if VERBOSE:
            print(f"Multiple minima: min_value=={min_value:.4f}, min_indices=={min_indices}")
        paths *= minlength
        #for idx in range(minlength):
            #i, j = min_indices[0][idx], min_indices[1][idx]
            #print(f"abs(diff_age[{i},{j}]): {np.abs(diff_age[i,j]):.2f}")

    i, j = min_indices[0][0], min_indices[1][0]
    # TODO: test all (sequentially) or a random one of these pairs, not 
    #    just the first one (...[0])
    
    # Step 3.2: Match case i with control j
    match[i] = j

    # Step 3.3: Now block out case i and ctrl j from future searches
    working[i, :] = np.nan
    working[:, j] = np.nan
    
# Print the resulting match array
print("Match array:", match)

# Step 4: Print requested rows with participant details
if VERBOSE:
    for i in range(ncase):
        j = int(match[i])
        print(f"{cases['participant_ID'].iloc[i]}, {cases['handedness'].iloc[i]}, {round(age_cases[i], 1)} | {round(age_controls[j], 1)}, {controls['handedness'].iloc[j]}, {controls['participant_ID'].iloc[j]}")

# Calculations for step 5
residual_differences = age_controls[match.astype(int)] - age_cases
residual_diff_avg = np.mean(residual_differences)
residual_diff_avg_abs = np.mean(np.abs(residual_differences))
residual_diff_max_abs = np.max(np.abs(residual_differences))
different_handedness_count = np.sum(cases['handedness'].values != controls['handedness'].values[match.astype(int)])
# TODO: count only (R or blank) vs not-R as different

print(f"\nAverage Residual Difference: {residual_diff_avg:.4f}")
print(f"Average Absolute Residual Difference: {residual_diff_avg_abs:.4f}")
print(f"Maximum Absolute Residual Difference: {residual_diff_max_abs:.4f}")
if VERBOSE:
    print(f"Pairs with difference > 1.0: {np.count_nonzero(residual_differences>1.0)}")
    print(f"Pairs with difference > 2.0: {np.count_nonzero(residual_differences>2.0)}")
    print("Number with Different Handedness:", different_handedness_count)
    print("Paths = product of number of elements in each tie:", paths)

sys.exit(0)
