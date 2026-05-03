*==========================================================================*
* Get the summary data
* - Household form
* - LQ Form
* - TUS
*===========================================================================*

/******************************************************************
 1. GET TEAMS 
******************************************************************/
* Load google sheet and get teams sheet
local GOOGLE_SHEET_ID "1-Ym7pDg2e8FbDLFhSKSS3UeePYSN06AKII7OirSmIHM"
local DATA "${DIR_DATA_433FM_YQ}hies_progress2025.xlsx"
copy "https://docs.google.com/spreadsheets/d/`GOOGLE_SHEET_ID'/export?format=xlsx" ///
     "`DATA'", replace

import excel using "`DATA'", sheet("teams") firstrow clear
gen tab_no = substr(username, 5, 2)

* Get one row per psu
keep if SupervisorName != ""

bysort PSU (username): gen interviewers = "Tab " + tab_no[1] + " / " + tab_no[2]
bysort PSU: keep if _n == 1

* edit island code
destring IslandCode , replace
levelsof IslandCode, local(codes)

foreach c of local codes {
    preserve
    keep if IslandCode == `c'
    local name = IslandName[1]
    restore
    label define island_lbl `c' "`name'", add
}

label values IslandCode island_lbl
rename IslandCode GHI_ISLAND_CODE

* edit block code
replace block = subinstr(block, ", ", ",", .)
split block, parse(",") gen(_block)

// one row per block
gen obs_id = _n
reshape long _block, i(obs_id) j(n)
drop if missing(_block)
drop n obs_id

// include ward name in the block code
gen GHI_BLOCK_CODE = _block
replace _block = _block + "( " + ward_name + ") " if !missing(ward_name)

// label GHI_BLOCK_CODE
destring GHI_BLOCK_CODE , replace
levelsof GHI_BLOCK_CODE, local(codes)

foreach c of local codes {
    preserve
    keep if GHI_BLOCK_CODE == `c'
    local name = _block[1]
    restore
    label define block_lbl `c' "`name'", add
}

label values GHI_BLOCK_CODE block_lbl

* order
keep interviewers supervisor GHI_ISLAND_CODE PSU GHI_BLOCK_CODE block
order interviewers supervisor GHI_ISLAND_CODE PSU GHI_BLOCK_CODE block

* save
tempfile teams
save `teams', replace
erase "`DATA'"

tempfile psu_block
keep PSU block interviewers supervisor
bysort PSU block : keep if _n == 1
save `psu_block', replace
/******************************************************************
 2. HOUSEHOLD DATA
******************************************************************/
tempfile hies_file

global IDENTIFYING GHI_ISLAND_CODE PSU GHI_BLOCK_CODE GHI_STRUCTURE DWELLING_ID SELECTION HOUSEHOLD_HD_ID HOUSEHOLD_KEY file status selectedName_1 selectedAge_1 gender_str

* Read hies data
use "${HIES_FILE}", clear

* Keep only the identifying column
keep $IDENTIFYING
* drop if status missing
keep if !missing(status)

* rename TUS variables
rename selectedName_1 PERSON_NAME  
rename selectedAge_1 PERSON_AGE
rename gender_str PERSON_SEX

* Regenerate the household key
replace HOUSEHOLD_KEY = regexs(1) if regexm(HOUSEHOLD_HD_ID,"\((.*)\)")

* save tus details
tempfile tus_dets
preserve
keep if file==1
keep HOUSEHOLD_KEY PERSON_NAME PERSON_AGE PERSON_SEX
save `tus_dets'
restore

drop PERSON_NAME PERSON_AGE PERSON_SEX

* reshape status wide format
reshape wide status , i(HOUSEHOLD_KEY ) j(file)

rename status1 file1_status
rename status2 file2_status

* Check for uniqueness
isid HOUSEHOLD_HD_ID
isid HOUSEHOLD_KEY

merge 1:1 HOUSEHOLD_KEY using `tus_dets' , keep(1 3) nogen

* merge with tus data
rename HOUSEHOLD_KEY TIMEUSE_ID
merge 1:1 TIMEUSE_ID using "${TUS_FILE}", keepusing(status_tus TU_PERSON_SEX TU_WDAY)

list TIMEUSE_ID if _merge==2
// assert _merge != 2

keep if  inlist(_merge,1,3)
drop _merge

rename TIMEUSE_ID HOUSEHOLD_KEY
save `hies_file'


/******************************************************************
 MERGE WITH SMAPLE DATA
******************************************************************/
use "${sample_file}", clear

preserve
tempfile targets
bysort GHI_ISLAND_CODE: egen no_psus = nvals(PSU)
bysort GHI_ISLAND_CODE no_psus : keep if _n==1
gen target = no_psus * 16
keep GHI_ISLAND_CODE target
save `targets', replace
restore

keep if lq_id == ""

global IDENTIFYING HOUSEHOLD_HD_ID HOUSEHOLD_KEY GHI_STRUCTURE DWELLING_ID SELECTION PSU GHI_ISLAND_CODE GHI_BLOCK_CODE

gen HOUSEHOLD_KEY = regexs(1) if regexm(HOUSEHOLD_HD_ID,"\((.*)\)")

rename selection SELECTION

keep  $IDENTIFYING

merge 1:1 HOUSEHOLD_HD_ID using `hies_file'

// assert _merge != 2

// keep if inlist(_merge,1,3)
drop _merge

* update status labels
replace status_tus = 0 if missing(status_tus)
label define lbl 0 "Status Pending", add

replace file1_status = -1 if missing(file1_status)
replace file2_status = -1 if missing(file2_status)

label define status -1 "Status Pending", add

merge m:1 GHI_BLOCK_CODE using `teams'
assert _merge!=1
keep if _merge == 3
drop _merge


order interviewers supervisor $IDENTIFYING
order file1_status file2_status status_tus, last

* create tus summaries
* person sex
preserve
tempfile all_pu_s
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_PERSON_SEX  GHI_ISLAND_CODE)
rename GHI_ISLAND_CODE isl
decode isl, gen(GHI_ISLAND_CODE)
drop isl

save "${DIR_DATA_433FM_YQ}/all_person_s.dta", replace
restore

* weekday
preserve
clear
tempfile all_labels 
input str10 TU_WDAY
"Sunday"
"Monday"
"Tuesday"
"Wednesday"
"Thursday"
"Friday"
"Saturday"
end
save `all_labels', replace
restore

preserve
tempfile all_pu_s
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_WDAY  GHI_ISLAND_CODE)
rename GHI_ISLAND_CODE isl
decode isl, gen(GHI_ISLAND_CODE)

drop isl

replace TU_WDAY = trim(TU_WDAY)
merge m:1 TU_WDAY using `all_labels', nogen
save "${DIR_DATA_433FM_YQ}/all_weekday.dta", replace
restore

drop TU_PERSON_SEX TU_WDAY

save "${DIR_DATA_433FM_YQ}/progress.dta", replace

* save if completed or not
gen FILE1_STATUS = inlist(file1_status,1,2,3)
gen FILE2_STATUS = inlist(file2_status,1,2,3)
gen TUS_STATUS = inlist(status_tus, 1)

* summary data (island and block level)
preserve
gen completed_HH = FILE1_STATUS > 0 & FILE2_STATUS > 0
collapse (sum) FILE1_STATUS FILE2_STATUS TUS_STATUS completed_HH, by(GHI_ISLAND_CODE)
save "${DIR_DATA_433FM_YQ}/completion_island.dta",replace
restore

preserve
gen completed_HH = FILE1_STATUS > 0 & FILE2_STATUS > 0
collapse (sum) FILE1_STATUS FILE2_STATUS TUS_STATUS completed_HH, by(GHI_ISLAND_CODE PSU interviewers supervisor)
rename interviewers TAB
rename supervisor SUP
save "${DIR_DATA_433FM_YQ}/completion_psu.dta", replace
restore

/******************************************************************
 3. LQ DATA
******************************************************************/
* lq progress
do "${DIR_PROG_433FM_YQ}3. lq_file_cleaning.do"

use "${sample_file}", clear
keep if lq_id != ""

global IDENTIFYING LQ_ID GHI_STRUCTURE DWELLING_ID PSU GHI_ISLAND_CODE GHI_BLOCK_CODE

keep if selection != 2

rename lq_id LQ_ID
keep $IDENTIFYING

merge 1:1 LQ_ID using `"lq_file_cleaned.dta"'

assert _merge != 2
keep if _merge==3
drop _merge

erase "lq_file_cleaned.dta"

save "${DIR_DATA_433FM_YQ}/progress_LQ.dta", replace

preserve
append using "${DIR_DATA_433FM_YQ}/progress.dta"
order GHI_ISLAND_CODE PSU GHI_BLOCK_CODE block GHI_STRUCTURE DWELLING_ID SELECTION  HOUSEHOLD_HD_ID HOUSEHOLD_KEY LQ_ID file1_status file2_status status_tus completed_LQ nbslct total_ind_finished PERSON_NAME PERSON_AGE PERSON_SEX interviewers supervisor

merge m:1 PSU using `psu_block', keep(3) keepusing(PSU block) nogen

save "${DIR_DATA_433FM_YQ}/progress_all.dta" , replace
restore

* get team information
merge m:1 GHI_BLOCK_CODE using `teams'
assert _merge!=1
keep if _merge == 3
drop _merge

* totals for island level
preserve
collapse (sum) nbslct total_ind_finished completed_LQ , by(GHI_ISLAND_CODE)
merge 1:1 GHI_ISLAND_CODE using "${DIR_DATA_433FM_YQ}/completion_island.dta", nogen

local lq_vars nbslct completed_LQ total_ind_finished

foreach var of local lq_vars{
	replace `var' = 0 if missing(`var')
}
order `lq_vars' , last

gen total_completed = completed_LQ + completed_HH
merge 1:1 GHI_ISLAND_CODE using `targets', nogen
gen completion_rate = (total_completed / target) * 100
format completion_rate %9.2f
order GHI_ISLAND_CODE total_completed target , first
save "${DIR_DATA_433FM_YQ}/completion_island_all.dta",replace
restore

* totals for block level
preserve
collapse (sum) nbslct completed_LQ total_ind_finished , by(GHI_ISLAND_CODE PSU)
merge 1:1 GHI_ISLAND_CODE PSU using "${DIR_DATA_433FM_YQ}/completion_psu.dta", nogen
local lq_vars nbslct completed_LQ total_ind_finished

foreach var of local lq_vars{
	replace `var' = 0 if missing(`var')
}

gen total_completed = completed_LQ + completed_HH
gen target = 16
gen completion_rate = (total_completed / target) * 100
format completion_rate %9.2f

order `lq_vars' , last
order GHI_ISLAND_CODE
merge 1:1 PSU using `psu_block', keep(3) keepusing(PSU block) nogen
drop PSU
assert !missing(block)
order block, after(GHI_ISLAND_CODE)
order GHI_ISLAND_CODE block total_completed target , first

merge 1:1 block using `psu_block', keep(1 3) keepusing(supervisor interviewers)  nogen
save "${DIR_DATA_433FM_YQ}/completion_psu_all.dta",replace
restore
