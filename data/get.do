
use "\\fileserver\ICT&DM\DPDM\HIES\HIES2025\HIES_GSBPM\PROG\433_FIELDWORK_MONITORING\data\completion_psu_all.dta" , clear

gen obs = 0

replace obs = 1 if inlist(PSU, "204","205","206","207")
replace obs = 1 if inlist(PSU, "001","033","037","065")
replace obs = 1 if inlist(PSU, "001","033","037","065")

replace obs = 1 if inlist(PSU,"103","104","105","106","107","108","109","110","111" )
replace obs = 1 if inlist(PSU,"112","113","114","115","116","117","118","119","120" )
replace obs = 1 if inlist(PSU,"121","122","123","124","125","126","127","128","129" )
replace obs = 1 if inlist(PSU,"130","131","132" )


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
