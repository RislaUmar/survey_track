
use "\\fileserver\ICT&DM\DPDM\HIES\HIES2025\HIES_GSBPM\PROG\433_FIELDWORK_MONITORING\data\completion_psu_all.dta" , clear

gen obs = 0

replace obs = 1 if inlist(PSU, "235","236","237","238","239","240","241","242","243")
replace obs = 1 if inlist(PSU, "244","245","246","247","248","249","250","251","252")


keep if obs == 1


levelsof SUP, local(unique_sups)

foreach s of local unique_sups {
	preserve
	
	keep if SUP == "`s'"
	sort PSU
	keep GHI_ISLAND_CODE block total_completed completed_HH completed_LQ SUP
	order GHI_ISLAND_CODE block  completed_HH completed_LQ total_completed SUP
	
	export excel using "completion_`s'.xlsx", firstrow(variables) replace
	restore
}



sort PSU

keep GHI_ISLAND_CODE block total_completed completed_HH completed_LQ SUP
order GHI_ISLAND_CODE block  completed_HH completed_LQ total_completed SUP

export excel using "completion.xlsx", firstrow(variables) replace
