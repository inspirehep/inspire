This is (I think) the comprehensive collection of the SLAC Giva routines.
They are designed to be integrated directly with SPIRES, via the
Expect::Spires module (which is included here).   Because of this, there
is not an easy way to run many of these without having Spires readily
available.

However a quick guided tour reveals that the  most interesting parts of
the code are independent of Spires, and reside in the
Giva::Extractor::*.pm modules.   Most of these (and their parent class
Extractor.pm) contain pod.  These do the actual extraction.  Everything
else is management of interface and/or checking the results.

Not also Astrlist.pm which is an object that holds a full author
affiliation listing for a paper and enables many checks and operations on
that listing.

If people are very interested in running this somewhere other than on
sunspi5 here at SLAC for investigative purposes, then one could consider
rewriting Expect::Spires to return dummy results...however this might be
hard.  Easier is looking at it on sunspi5.



