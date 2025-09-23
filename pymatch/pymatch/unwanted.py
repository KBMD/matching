# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:22:22 2025

@author: Kevin J. Black

#######
HISTORY OR OTHER UNWANTED CODE from match_my_data.py
#######

"""




# %% OOPS, NT897 is NOT working right ((see last row of table below))

"""
closest_matches[closest_matches['age_diff']> .08].sort_values('age_diff')[
['study_subject_ID','age_at_scan_who', 'age_at_scan_scan_day', 'age_diff'] ]
Out[103]: 
    study_subject_ID  age_at_scan_who  age_at_scan_scan_day  age_diff
330           CTS231              7.9                   8.0       0.1
295            NT802              5.8                   5.7       0.1
317           WUE029              7.5                   7.6       0.1
306           WUE044              6.4                   6.5       0.1
387           WUE049              9.8                   9.9       0.1
103           CTS209              5.8                   5.9       0.1
314           CTS235              7.3                   7.4       0.1
405           WUE006             10.2                  10.3       0.1
225           WUE037             10.2                  10.3       0.1
265            NT897              5.8                   8.5       2.7  # <=====
"""



"""
# read in the most used scan_day variables
session_ID = scan_day['session_ID'].values
scanner    = scan_day['scanner_make_model'].values
scannerID  = scan_day['scanner_identifier'].values
ages       = scan_day['age_at_scan'].values
SSIDs      = scan_day['study_subject_ID'].values
"""

# initially failed because CTS228 & CTS230 == NaN for age_at_scan in scan_day
# temporary fix--also made new Excel tables in same directory as these were
#   read from
scan_day.loc[scan_day['study_subject_ID'].isin(['CTS228', 'CTS230']),
             'age_at_scan'] = [7.7, 10.2]
# CHECK
"""
with pd.option_context('display.float_format', '{:.1f}'.format):
    with pd.option_context('display.max_columns', None):
        print(closest_matches.loc[closest_matches['study_subject_ID'].str.contains('CTS'),[
            'study_subject_ID','age_at_scan_who','age_at_scan_scan_day']])            
            
    study_subject_ID  age_at_scan_who  age_at_scan_scan_day
158           CTS201              8.7                   8.7
118           CTS208              6.8                   6.8
103           CTS209              5.8                   5.9
204           CTS211              9.9                   9.9
153           CTS226              8.5                   8.5
135           CTS228              7.7                   7.7
404           CTS230             10.2                  10.2
330           CTS231              7.9                   8.0  <=====
314           CTS235              7.3                   7.4  <=====
242           CTS238             10.6                  10.6
"""
# NOTICE: different values in CTS231, CTS235



# scan_day_in_who = pd.merge(scan_day, who, on=['study_subject_ID'])




deleteme = pd.DataFrame({'num_legs': [4, 2], 'num_wings': [0, 2]},
                  index=['dog', 'hawk'])
deleteme
"""
Out[428]: 
      num_legs  num_wings
dog          4          0
hawk         2          2
"""

for i in range(2):
    if deleteme.iloc[i]['num_legs'] == 2: print(i, deleteme.iloc[i])
"""
Out:
1 num_legs     2
num_wings    2
Name: hawk, dtype: int64
"""

# HOORAY! See below! <===================================

"""
keep = np.full(len(deleteme),False)

for i in range(2):
    if deleteme.iloc[i]['num_legs'] == 2: 
        keep[i] = True 
    else: 
        keep[i] = False
deleteme['keep'] = keep


deleteme
Out[435]: 
      num_legs  num_wings   keep
dog          4          0  False
hawk         2          2   True
"""





subset2 = pd.merge(scan_day_in_who, scan_matching_params, 
                   on = [['study_subject_ID', 'session_ID']])
# [55 rows x 30 columns], all with scanner_identifier == 67064
# includes 4 sessions from MSCPI12
# but lots of NTs also have 2 sessions, ses-screen & ses-12mo
# subset2[subset2['study_subject_ID'].str.contains("NT")]
# Out: 33 rows
# whatever, I can do that by hand
# Alternatively, keep only one scan per SSID:
# Yup a quick check of the girls & boys data shows no duplicate SSIDs.
# BUT! subset2 as above includes 2 ages: age_at_scan_x  age_at_scan_y
# That's not what I want.

subset2a = subset2.drop_duplicates(subset=['study_subject_ID'], keep='first')
# Ay ay, down to only 25 rows. WAAH.
# subset2a['tic_dx'].value_counts()
# Out:
# tic_dx
# PTD     16
# none     9

# subset2a[['study_subject_ID', 'session_ID', 'tic_dx']]
# Out:
"""
   study_subject_ID  session_ID tic_dx
0           MSCPI12      ses-01   none
4           MSCPI13      ses-01   none
10          MSCPI17      ses-01   none
15          MSCPI19      ses-01   none
22            NT808    ses-12mo    PTD
23            NT819    ses-12mo    PTD
25            NT820    ses-12mo    PTD
27            NT825    ses-12mo    PTD
29            NT833    ses-12mo    PTD
31            NT842    ses-12mo    PTD
33            NT845  ses-screen   none
34            NT846    ses-12mo    PTD
36            NT864    ses-12mo    PTD
38            NT867    ses-12mo    PTD
40            NT884  ses-screen   none
41            NT886    ses-12mo    PTD
43            NT891  ses-screen   none
44            NT895  ses-screen   none
45            NT897    ses-12mo    PTD
46            NT901    ses-12mo    PTD
48            NT924    ses-12mo    PTD
50            NT933  ses-screen    PTD
51            NT934  ses-screen    PTD
52            NT942    ses-12mo    PTD
54            NT945  ses-screen   none
"""

# subset2a[['age_at_scan_x', 'age_at_scan_y']]
"""
Out[352]: 
    age_at_scan_x  age_at_scan_y
0             9.8           9.80
4             9.7           9.70
10           10.1          10.10
15            9.4           9.40
22           11.6          10.68
23            6.3           5.64
25            6.9           6.22
27            6.5           5.62
29            6.4           5.89
31            9.7           9.49
33            6.2           6.18
34            6.3           6.15  (*** ??)
36            9.4           8.88
38           10.5          10.23  (*** ??)
40            8.2           8.28  (*** ??)
41            9.5           9.14
43            9.2           9.21
44            6.0           6.05
45            8.4           5.80
46            8.0           6.94
48            8.3           7.94
50            9.8           9.89  (*** ??)
51            9.3           9.39  (*** ??)
52           11.2          10.93
54            9.3           9.39  (*** ??)
"""
# AARGH now I have two ages. They're also in subset2.
#  Oh yeah. Try this:
subset2a[close_enough(subset2a['age_at_scan_x'],subset2a['age_at_scan_y'], 
                      epsilon=.05)][['age_at_scan_x', 'age_at_scan_y']]
"""
Out[355]: 
    age_at_scan_x  age_at_scan_y
0             9.8           9.80
4             9.7           9.70
10           10.1          10.10
15            9.4           9.40
33            6.2           6.18
43            9.2           9.21
44            6.0           6.05
"""
# No, that's not what I want, either. 


##################################################################




if False:  # was   if DEBUG:
    # check procedure by reporting tic_diagnosis_current from enigma data
    print("CHECKING IDENTIFICATION OF A GIVEN SUBJECT AND SCAN DAY")
    this_subject_indices = (SSIDs == test_SSID)
    this_age_indices     = close_enough(ages, test_age)
    both_indices         = this_subject_indices & this_age_indices
    number               = np.sum(both_indices)
    
    print("number of nonzeros:", number)
    print("who is it?")
    test2 = scan_day[["study_subject_ID","session_ID","tic_diagnosis_current",
                    "age_at_scan"]][both_indices]
    print(test2)

#################################################
# Yay. It works. 
#     study_subject_ID  session_ID tic_diagnosis_current  age_at_scan
# 343            NT825  ses-screen                   PTD          5.6
# 
# Now for reading them all in.
#################################################





# scan_day_subset_1 = scan_day[scan_day['study_subject_ID'].isin(who['study_subject_ID'])]
# len(scan_day_subset_1)   # Out: 173    with 6 columns

scan_day_in_who = pd.merge(scan_day, who, on=['study_subject_ID'])
# len(scan_day_in_who) # Out: 173    with 15 columns
# All are female sex

scan[close_enough(scan['TR'], 2500, epsilon=5) & 
        close_enough(scan['TE'],2.9,.03) & 
        close_enough(scan['TI'],1070,20) &
        scan['receive_coil'].str.contains("64")][
             ['study_subject_ID','session_ID',
              'receive_coil','pulse_sequence',
              'TR','TE','TI', 'voxel_size'] ]
# Out: df with 247 rows x 8 columns
scan_matching_params[scan_matching_params['voxel_size']=="1x1x1"]
# Out: df with 247 rows x 17 columns

scan[scan['voxel_size'].str.contains("x1")]
# Out: df with 1319 rows

scan[scan['voxel_size'] == "1x1x1" ]
# Out: df with 1319 rows

scan[scan['voxel_size'].str.contains("x1") & ~(scan['voxel_size'] == "1x1x1")]
# Out: Empty DataFrame


test[:3]
Out[298]: 
    study_subject_ID session_ID          receive_coil  ...   TE    TI  voxel_size
207          MSCPI05     ses-02  HeadNeck_64HC1-7;NC1  ...  2.9  1070       1x1x1
208          MSCPI05     ses-04  HeadNeck_64HC1-7;NC1  ...  2.9  1070       1x1x1
209          MSCPI05     ses-06  HeadNeck_64HC1-7;NC1  ...  2.9  1070       1x1x1

test.filter(items=[207], axis=0)
test.loc[test.index == 207]
# Either of these contains the MSCPI05 ses-02 row, as desired.
# test.iloc[207] does not -- it tries to return the 207'th row of test.

scan[scan['TR']==2500]
# Out: scan subset with [522 rows x 17 columns]
scan[close_enough(scan['TR'], 2500, epsilon=5)]
# Out: scan subset with [522 rows x 17 columns]
scan[(scan['TR']==2500) & (scan['TE']==2.9) & (scan['TI']==1070)]
# Out: scan subset with [519 rows x 17 columns]
scan[close_enough(scan['TR'], 2500, epsilon=5) & close_enough(scan['TE'],2.9,.01)
     & close_enough(scan['TI'],1070,15)]
# Out: scan subset with [519 rows x 17 columns]
scan[close_enough(scan['TR'], 2500, 5) & 
        (~close_enough(scan['TE'],2.9,.01) | 
         ~close_enough(scan['TI'],1070,15))][
             ['TR','TE','TI','session_ID','study_subject_ID'] ]
# Out:
#          TR    TE    TI  session_ID study_subject_ID
# 323  2500.0  2.88  1060  ses-screen            NT812
# 324  2500.0  2.88  1060  ses-screen            NT813
# 326  2500.0  2.88  1060  ses-screen            NT814

# np.sum(who['study_subject_ID'] == 'NT812') and ditto 813, 814: # Out: 0
# So those 3 are not in  ... wait.  See below the sys.exit(0) call.

# 



"""
with pd.option_context('display.max_columns', None):
    print(scan[close_enough(scan['TR'], 2500, epsilon=5) & 
        (~close_enough(scan['TE'],2.9,.01) | 
         ~close_enough(scan['TI'],1070,15))] )
         
     session_ID transmit_coil      receive_coil  \
323  ses-screen          Body  HeadNeck_64HC1-7   
324  ses-screen          Body  HeadNeck_64HC1-7   
326  ses-screen          Body  HeadNeck_64HC1-7   

                                   pulse_sequence      TR    TE    TI  \
323  tfl3d1_16ns%CustomerSeq%\tfl_mgh_epinav_ABCD  2500.0  2.88  1060   
324  tfl3d1_16ns%CustomerSeq%\tfl_mgh_epinav_ABCD  2500.0  2.88  1060   
326  tfl3d1_16ns%CustomerSeq%\tfl_mgh_epinav_ABCD  2500.0  2.88  1060   

     flip_angle  bandwidth                 FoV       matrix voxel_size  \
323           8        240  (256.0, 256,  256)  (256,  256)      1x1x1   
324           8        240  (256.0, 256,  256)  (256,  256)      1x1x1   
326           8        240  (256.0, 256,  256)  (256,  256)      1x1x1   

     partial_Fourier  phase_resolution  slice_resolution  average  \
323              1.0               1.0               NaN        1   
324              1.0               1.0               NaN        1   
326              1.0               1.0               NaN        1   

    study_subject_ID  
323            NT812  
324            NT813  
326            NT814  

scan_day[scan_day['study_subject_ID'] in ('NT812', 'NT813', 'NT814')]

# So ... these 3 are 64 channel and almost the same TE,TI as the main 
# people in row 4 of Suppl. Table 1.  Also same sequence, vNavs, voxel size.

# Let's check which scanner it is.

with pd.option_context('display.max_columns', None):
    print(scan_day[(scan_day['study_subject_ID']=='NT812') & 
                   (scan_day['session_ID'] == 'ses-screen')]) 
     session_ID scanner_make_model  scanner_identifier  age_at_scan  \
323  ses-screen  SiemensPrisma_fit             67064.0          6.4   

    study_subject_ID tic_diagnosis_current  
323            NT812                   TTD  

with pd.option_context('display.max_columns', None):
    print(scan_day[(scan_day['study_subject_ID']=='WUG119') & 
                   (scan_day['session_ID'] == 'ses-01')])
     session_ID scanner_make_model  scanner_identifier  age_at_scan  \
1085     ses-01  SiemensPrisma_fit             67064.0          4.2   

     study_subject_ID tic_diagnosis_current  
1085           WUG119                  none  

# Yup, same scanner. 

# Check exactness of 2.88 vs 2.9 etc.
scan.iloc[322]['TE'] - scan.iloc[323]['TE']
# Out[235]: np.float64(0.020000000000000018)
# OK, say epsilon = 0.021 for those.
scan.iloc[322]['TI'] - scan.iloc[323]['TI']
# Out[236]: np.int64(10)
# OK, can use epsilon=10. (I changed close_enough to use <= epsilon not < .)

# So are they in or not?
who[who['study_subject_ID']=='NT814']
# Out: []

# Same for NT812, NT813. Don't know why.
# OK, turns out that's just because they're boys and I'd only read in girls.

	session_ID	scanner_make_model	scanner_identifier	age_at_scan	study_subject_ID	tic_diagnosis_current
322	ses-12mo	SiemensPrisma_fit	67064.0	7.2	NT812	TTD
323	ses-screen	SiemensPrisma_fit	67064.0	6.4	NT812	TTD
324	ses-screen	SiemensPrisma_fit	67064.0	10.6	NT813	TTD
325	ses-12mo	SiemensPrisma_fit	67064.0	9.1	NT814	TTD
326	ses-screen	SiemensPrisma_fit	67064.0	8.3	NT814	TTD

# THIS IS A PROBLEM! I CHECKED REDCAP AND NT812's DIAGNOSIS AT 12-mo WAS TS !!
# NT813 apparently no return visit at 12 months.
# NT814 diagnosis at 12mo is TS per REDCap !!!!!


who1 = pd.read_csv("C:/Users/kevin/src/matching/" + "boys.csv")
who2 = pd.read_csv("C:/Users/kevin/src/matching/" + "girls.csv")
# (number of X chromosomes)

"""




testdf = pd.merge(scan_day, who, on=['study_subject_ID', 'age_at_scan'])
# len(testdf)  # Out: 84
testdf2 = pd.merge(scan_day, who, on=['study_subject_ID', 'age_at_scan'], how='right')
# len(testdf2) # Out: 113

testdf2 = pd.merge(scan_day, who, on=['study_subject_ID', 'age_at_scan'], how='left')
# testdf2.shape          Out: (1371, 14)
testdf3 = testdf2[(testdf2['age_at_scan'] < 11.0) & (testdf2['age_at_scan'] >= 5.0)]
# testdf3.shape    Out[150]: (647, 14)


# who_subset_2 = who_subset_1[who_subset_1['age_at_scan'].isin()]


who.loc[who['study_subject_ID'] == testid]
Out[66]: 
  participant_ID study_subject_ID  ... duration_of_tics_(days) dx_group
1          NT729            NT729  ...                   128.0      PTD

[1 rows x 10 columns]

testdf2.loc[testdf2['study_subject_ID'] == testid]
Out[67]: 
  session_ID scanner_make_model  ...  duration_of_tics_(days)  dx_group
1        NaN                NaN  ...                    128.0       PTD

[1 rows x 14 columns]

scan_day.loc[scan_day['study_subject_ID'] == testid]
Out[68]: 
     session_ID scanner_make_model  ...  study_subject_ID  tic_diagnosis_current
295  ses-screen     SiemensTrioTim  ...             NT729                    TTD

[1 rows x 6 columns]

scan.loc[scan['study_subject_ID'] == testid]
Out[69]: 
     session_ID transmit_coil  ... average study_subject_ID
295  ses-screen          Body  ...       1            NT729

[1 rows x 17 columns]

testdf.loc[testdf['study_subject_ID'] == testid]
Out[70]: 
Empty DataFrame
Columns: [session_ID, scanner_make_model, scanner_identifier, age_at_scan, study_subject_ID, tic_diagnosis_current, participant_ID, tic_dx, sex_at_birth, handedness, best_ygtss_impairment, best_ygtss_tts, duration_of_tics_(days), dx_group]
Index: []
