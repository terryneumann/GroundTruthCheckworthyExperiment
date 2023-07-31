#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:50:59 2023

@author: tdn897
"""

import csv
import os

os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/data_splits/qualtrics/')
splits = 4
infile = 'output/split_0.csv'
outfile = 'output/qualtrics_survey_split_0.txt'


html_code = '''
<h1 style='color:#CC4415; font-family:Georgia;'>FACT-CHECKING SURVEY</h1>\n\n\n
<p>You will read claims that are currently or have recently been trending on social media. These claims could be verified as either being true or false by fact-checkers.
    We are curious about your opinions regarding the assertions made in these claims; please read each claim carefully and answer honestly. Your opinions matter! They will help inform better fact-checking systems.</p>\n\n\n
<p>We intend to create a dataset of true or false news/news-like content as well as annotations about the content. If you do not consent to your annotations (anonymized) being included in the released dataset, then you are not eligible to participate in this study. 
  Please read the following <a href='https://docs.google.com/document/d/15xDvYUYNH4XEE6je_j3GI75-GBVqHREvZreFIcwYygk/view'>CONSENT RELEASE FORM</a>. By continuing with the experiment, you consent to your data being collected and released. If you do not consent, please release the survey now.</p>\n\n\n
<p><strong><u>WORK WILL BE MONITORED FOR QUALITY. WORKERS SUBMITTING POOR QUALITY WORK WILL BE BARRED FROM FUTURE WORK.</u></strong></p>
  
  
[[PageBreak]]


<h2>First, please fill out this optional demographic survey.</h2>


<h3>Select your gender.</h3>
<select name="demog-gender" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Male</option>
  <option>Female</option>
  <option>Non-Binary</option>
  <option>Other</option>
</select>


<h3>Select your race.</h3>
<select name="demog-race" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Asian</option>
  <option>White</option>
  <option>Black</option>
  <option>Hispanic</option>
  <option>Other</option>
</select>


<h3>Select your age range.</h3>
<select name="demog-age" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Less than 20 years old</option>
  <option>21-30 years old</option>
  <option>31-40 years old</option>
  <option>41-50 years old</option>
  <option>51-60 years old</option>
  <option>More than 60 years old</option>
</select>


<h3>Select your highest educational attainment.</h3>
<select name="demog-educ" style="font-size: large">
  <option value="">(Please select)</option>
  <option>No High School</option>
  <option>High School Diploma</option>
  <option>Some College</option>
  <option>Bachelor's Degree</option>
  <option>Master's Degree</option>
  <option>PhD or other doctorate</option>
</select>


<h3>Select your sexual orientation.</h3>
<select name="demog-sexual" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Heterosexual</option>
  <option>Homosexual</option>
  <option>Bisexual</option>
  <option>Asexual</option>
  <option>Other</option>
</select>


<h2>Fake News Headline Challenge</h2>
<p>How good are you at spotting fake news headlines? Please examine the following news headlines and categorize them as either Fake/Deceptive or Real/Factual.</p>


<h3>Certain Vaccines are Loaded with Dangerous Chemicals and Toxins</h3>
<select name="identification-fake-1" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>Global Warming Age Gap: Younger Americans Most Worried</h3>
<select name="identification-real-1" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>New Study: Left-Wingers Are More Likely to Lie to Get a Higher Salary</h3>
<select name="identification-fake-2" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>The Government Is Knowingly Spreading Disease Through the Airwaves and Food Supply</h3>
<select name="identification-fake-3" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>Attitudes Toward EU Are Largely Positive, Both Within Europe and Outside It</h3>
<select name="identification-real-2" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>Hyatt Will Remove Small Bottles from Hotel Bathrooms by 2021</h3>
<select name="identification-real-3" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>Government Officials Have Manipulated Stock Prices to Hide Scandals</h3>
<select name="identification-fake-4" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>


<h3>Republicans Divided in Views of Trump’s Conduct, Democrats Are Broadly Critical</h3>
<select name="identification-real-4" style="font-size: large">
  <option value="">(Please select)</option>
  <option>Real/Actual</option>
  <option>Fake/Deceptive</option>
</select>'''

# Split the HTML code by lines
lines = html_code.split('\n')








with open(infile, 'r') as csv_file, open(outfile, 'w') as txt_file:
    reader = csv.DictReader(csv_file)
    gold = 1
    normal = 1
    txt_file.write('[[Block: Demographic Survey]]\n\n')
    for i in range(len(lines)):
        txt_file.write(lines[i]  +'\n')
    for i, row in enumerate(reader, start=1):
        if 'Gold' in row['topic']:
            txt_file.write(f'[[Block:Gold Block {gold}]]\n\n')
            gold += 1
        else:
            txt_file.write(f'[[Block:Normal Block {normal}]]\n\n')
            normal += 1
        txt_file.write(f'Q{i}a. <h2 style="font-family:Georgia; border-width:10px; border-style:solid; border-color:#CC4415; padding: 1em;">{row["source"]}</h2>\n\n')
        txt_file.write('Considering that fact-checkers have limited time to check claims, should this claim be prioritized for fact-checking?\n')
        txt_file.write('Does the claim appear to be completely false?\n')
        txt_file.write('Will this claim be of interest to the general public?\n')
        txt_file.write('Will this claim harm certain demographic groups more than others if it is left unverified?\n\n')
        txt_file.write('1 - Definitely Not\n2 - Probably Not\n3 - Maybe Not\n4 - Maybe Yes\n5 - Probably Yes\n6 - Definitely Yes\n\n\n')
        txt_file.write(f'Q{i}b. If you believe this claim could harm certain demographic groups if left unverified, please select which groups from the list below. If you don\'t believe the claim would disproportionately harm certain groups, choose "N/A".\n')
        txt_file.write('[[MultipleAnswer]]\n\n')
        txt_file.write('<strong style="color:green">RACE</strong> - White\n<strong style="color:green">RACE</strong> - African American\n<strong style="color:green">RACE</strong> - Hispanic\n<strong style="color:green">RACE</strong> - East or South Asian\n<strong style="color:orange">SEXUAL ORIENTATION</strong> - LGBTQ\n<strong style="color:orange">SEXUAL ORIENTATION</strong> - Heterosexual\n<strong style="color:blue">GENDER</strong> - Men\n<strong style="color:blue">GENDER</strong> - Women\n<strong style="color:blue">GENDER</strong> - Non-binary\n<strong>N/A</strong>\n\n\n')
