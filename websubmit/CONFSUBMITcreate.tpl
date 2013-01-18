START::DEFP()---<record>
001::REP(EOL,)---<controlfield tag="001"><:SN::SN:></controlfield>
270::REP(EOL,)::MINLW(82)---<datafield tag="270" ind1=" " ind2=" "><subfield code="m"><:CONFSUBMIT_EMAI::CONFSUBMIT_EMAI:></subfield><subfield code="p"><:CONFSUBMIT_CONT::CONFSUBMIT_CONT:></subfield></datafield>
8564u::REP(EOL,)::MINLW(82)---<datafield tag="856" ind1="4" ind2=" "><subfield code="u"><:CONFSUBMIT_URL::CONFSUBMIT_URL:></subfield></datafield>
111_start::REP(EOL,)::DEFP()---<datafield tag="111" ind1=" " ind2=" ">
111a::REP(EOL,)::MINLW(31)---<subfield code="a"><:CONFSUBMIT_TITL::CONFSUBMIT_TITL:></subfield>
111x::REP(EOL,)::MINLW(33)---<subfield code="x"><:CONFSUBMIT_SDAT::year:>-<:CONFSUBMIT_SDAT::mm:>-<:CONFSUBMIT_SDAT::dd:></subfield>
111y::REP(EOL,)::MINLW(33)---<subfield code="y"><:CONFSUBMIT_FDAT::year:>-<:CONFSUBMIT_FDAT::mm:>-<:CONFSUBMIT_FDAT::dd:></subfield>
111c::REP(EOL,)::RANGE(1,1)::IFDEFP(CONFSUBMIT_STAT,,0)---<subfield code="c"><:CONFSUBMIT_CITY::CONFSUBMIT_CITY:>, <:CONFSUBMIT_STAT::CONFSUBMIT_STAT:>, <:CONFSUBMIT_CNTR::CONFSUBMIT_CNTR:></subfield>
111c_stat::REP(EOL,)::RANGE(1,1)::IFDEFP(CONFSUBMIT_STAT,,1)---<subfield code="c"><:CONFSUBMIT_CITY::CONFSUBMIT_CITY:>, <:CONFSUBMIT_CNTR::CONFSUBMIT_CNTR:></subfield>
111g::REP(EOL,)::MINLW(31)---<subfield code="g"><:CONFSUBMIT_CNUM::CONFSUBMIT_CNUM:></subfield>
111_end::DEFP()---</datafield>
411a::REP(EOL,)::IFDEFP(CONFSUBMIT_SNAM,,0)---<datafield tag="411" ind1=" " ind2=" "><subfield code="a"><:CONFSUBMIT_SNAM::CONFSUBMIT_SNAM:></subfield>
411n::REP(EOL,)::IFDEFP(CONFSUBMIT_SNR,,0)---<subfield code="n"><:CONFSUBMIT_SNR::CONFSUBMIT_SNR:></subfield>
411_end::REP(EOL,)::IFDEFP(CONFSUBMIT_SNAM,,0)---</datafield>
65017a::REP(EOL,)::MINLW(82)---<datafield tag="650" ind1="1" ind2="7"><subfield code="a"><:CONFSUBMIT_FIEL*::CONFSUBMIT_FIEL:></subfield></datafield>
6531a::DEFP()::SHAPE()::MINLW(121)---<datafield tag="653" ind1="1" ind2=" "><subfield code="9">submitter</subfield><subfield code="a"><:CONFSUBMIT_FREE*::CONFSUBMIT_FREE:></subfield></datafield>
520a::REP(EOL,)::MINLW(82)---<datafield tag="520" ind1=" " ind2=" "><subfield code="a"><:CONFSUBMIT_ABST::CONFSUBMIT_ABST:></subfield></datafield>
500a::REP(EOL,)::MINLW(82)---<datafield tag="500" ind1=" " ind2=" "><subfield code="a"><:CONFSUBMIT_ADD::CONFSUBMIT_ADD:></subfield></datafield>
500a::REP(EOL,)::IFDEFP(CONFSUBMIT_PROC_RADIO,1,1)---<datafield tag="500" ind1=" " ind2=" "><subfield code="a">Published in: <:CONFSUBMIT_PROC_TEXT::CONFSUBMIT_PROC_TEXT:></subfield></datafield>
500a::REP(EOL,)::IFDEFP(CONFSUBMIT_PROC_RADIO,2,1)---<datafield tag="500" ind1=" " ind2=" "><subfield code="a">Will be published in: <:CONFSUBMIT_PROC_TEXT::CONFSUBMIT_PROC_TEXT:></subfield></datafield>
980::DEFP()---<datafield tag="980" ind1=" " ind2=" "><subfield code="a">CONFERENCES</subfield></datafield>
FFT::REP(EOL,)---<datafield tag="FFT" ind1=" " ind2=" "><subfield code="a">
<:curdir::curdir:>/files/CONFSUBMIT_FILE/<:CONFSUBMIT_FILE::CONFSUBMIT_FILE:></subfield><subfield code="n"><:CONFSUBMIT_IRN::CONFSUBMIT_IRN:></subfield></datafield>
END::DEFP()---</record>
