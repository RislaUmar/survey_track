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

* Get one row per psu
keep if SupervisorName != ""

bysort PSU (username): gen interviewers = username[1] + " | " + username[2]
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
keep PSU block
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
tempfile all
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_PERSON_SEX)
gen GHI_ISLAND_CODE = "All"
save `all', replace
restore

preserve
tempfile all_pu_s
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_PERSON_SEX  GHI_ISLAND_CODE)
rename GHI_ISLAND_CODE isl
decode isl, gen(GHI_ISLAND_CODE)
drop isl

append using `all'
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
tempfile all
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_WDAY)
gen GHI_ISLAND_CODE = "All"
save `all', replace
restore

preserve
tempfile all_pu_s
keep if status_tus != 0
gen n = 1
collapse (count) n, by (TU_WDAY  GHI_ISLAND_CODE)
rename GHI_ISLAND_CODE isl
decode isl, gen(GHI_ISLAND_CODE)

drop isl

append using `all'
replace TU_WDAY = trim(TU_WDAY)
merge m:1 TU_WDAY using `all_labels', nogen
save "${DIR_DATA_433FM_YQ}/all_weekday.dta", replace
br
restore

drop TU_PERSON_SEX TU_WDAY

save "${DIR_DATA_433FM_YQ}/progress.dta", replace

* save if completed or not
gen FILE1_STATUS = inlist(file1_status,1,2,3)
gen FILE2_STATUS = inlist(file2_status,1,2,3)
gen TUS_STATUS = inlist(status_tus, 1)

* summary data (island and block level)
preserve
gen all_completed = FILE1_STATUS > 0 & FILE2_STATUS > 0 & TUS_STATUS > 0
collapse (sum) FILE1_STATUS FILE2_STATUS TUS_STATUS all_completed, by(GHI_ISLAND_CODE)
save "${DIR_DATA_433FM_YQ}/completion_island.dta",replace
restore

preserve
collapse (sum) FILE1_STATUS FILE2_STATUS TUS_STATUS , by(GHI_ISLAND_CODE PSU)
// merge 1:m PSU using `teams', keepusing("GHI_BLOCK_CODE")
// assert _merge !=1
// keep if inlist(_merge,1,3)
// drop _merge
save "${DIR_DATA_433FM_YQ}/completion_psu.dta", replace
restore

/******************************************************************
 3. LQ DATA
******************************************************************/
do "${DIR_PROG_433FM_YQ}3. lq_file_cleaning.do"

use "${sample_file}", clear
keep if lq_id != ""

global IDENTIFYING LQ_ID GHI_STRUCTURE DWELLING_ID PSU GHI_ISLAND_CODE GHI_BLOCK_CODE

keep if selection != 2

rename lq_id LQ_ID
keep $IDENTIFYING

merge 1:1 LQ_ID using `"lq_file_cleaned.dta"'

assert _merge == 3
keep if _merge==3
drop _merge

erase "lq_file_cleaned.dta"

save "${DIR_DATA_433FM_YQ}/progress_LQ.dta", replace

merge m:1 GHI_BLOCK_CODE using `teams'
assert _merge!=1
keep if _merge == 3
drop _merge

preserve
collapse (sum) nbslct total_finished completed , by(GHI_ISLAND_CODE)
merge 1:1 GHI_ISLAND_CODE using "${DIR_DATA_433FM_YQ}/completion_island.dta", nogen

local lq_vars nbslct total_finished completed

foreach var of local lq_vars{
	tostring `var', replace
	replace `var' = "-" if missing(`var')
}
order `lq_vars' , last
save "${DIR_DATA_433FM_YQ}/completion_island_all.dta",replace
restore

preserve
collapse (sum) nbslct total_finished completed , by(GHI_ISLAND_CODE PSU)
merge 1:1 GHI_ISLAND_CODE PSU using "${DIR_DATA_433FM_YQ}/completion_psu.dta", nogen
local lq_vars nbslct total_finished completed

foreach var of local lq_vars{
	tostring `var', replace
	replace `var' = "-" if missing(`var')
}

order `lq_vars' , last
merge 1:1 PSU using `psu_block', keep(3) nogen
drop PSU
assert !missing(block)
order block, after(GHI_ISLAND_CODE)
save "${DIR_DATA_433FM_YQ}/completion_psu_all.dta",replace
restore
