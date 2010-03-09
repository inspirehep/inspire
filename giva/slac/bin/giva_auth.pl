#!/usr/local/bin/perl

use arxiv;
use Giva;
use Inputter::Authors;

use SPIRES::Record::addtohep;
use Expect::Spires;

use Data::Dumper;
use Getopt::Std;
use Mail::Mailer;


=pod

=head1 SYNOPSIS

 giva_auth.pl -vh -i<irn> -b<eprint> -e<irn or eprint> -f<filetoextract> -c<hepcut> -r<name of extractor>

Typical example:

 giva_auth.pl -b'arXiv:0705.0432'

Extracts authors from specified paper (or file) using a collection of routines.  Interactive with user to choose routines and
and check authors and affiliations.

=head2 Options

=over

-v verbose

-h help

-i irn of record

-b eprint number (old or new style)

-e takes either i or b

-f file to extract from if you've already downloaded it

-c hepcut - in author checking it will ask user to check authors that appear less than this number of times in HEP  default is 5

-r extractor name  default is to let the user choose until they get one that works

=back

=head1  DETAILS

=head2 Extractors

Uses Extractors written as perl modules in Giva::Extractor::<module>

These are all subclasses of Giva::Extractor  which provides basic mthods for getting the paper and dealing
with the results.

The extractor module needs only to define the extract method  which reads from $self->file and calls $self->foundAuth
$self->foundAff methods when needed.  When done it should return $self->extracted.   Of course
you can override any of these methods yourself in the extractor, but you don't need to.  See the Giva::Extractor docs for details

At the moment you have to explicitly add your extractor here, however, we should make that more modular.

=cut






my $home = $ENV{'HOME'};

my @TEXROUTINES=qw(Coll Babar Coll2);

my $spi= Expect::Spires->new();
my $procauth = Expect::Spires->new(database=>'process.authors');
my $hep  = Expect::Spires->new(database=>'hep');

$procauth->ask("set supermax 128K");
$hep->ask("set supermax 128K");
my $user = Inputter::Authors->new( spi => $procauth );
my %args=();
getopts('vhr:i:b:e:f:c:',\%args);

die(pod2usage(verbose=>1)) if $args{h};

#Find Paper and get info
(my $irn,$lanl)=$user->findPaper(bull=>$args{b},irn=>$args{i},either=>$args{e});


my $hepcut = $args{c}||5;  # (Number of HEP papers required in order to pass the author no checks  set to 0 not allow any through (i.e. 0=1million...))


##
# Check for expt/colln  and get a similar paper
#

use Date::Calc qw(This_Year Date_to_Text Today);

if (!($hep->number("find irn $irn"))){
	$user->die("No record found in HEP for $irn");
}
$user->die("Record locked, consider looking by hand") unless $hep->number("also not hn str lots.of.authors.lock");

my $pakey=$lanl||$irn;

my $date=Date_to_Text(Today);

$hep->merge("HN(1000)=lots.of.authors.lock by ".$ENV{'USER'}." on $date;");

my $simauths={};
my $simaffs=[];
my $hepadded=0;
my $simirn=0;
my $resp='re-extract';  #default is to extract


while(1){

	$procauth->ask('sel process.authors');
    if ($procauth->number("find r $pakey")){
      #
      # We have a set so we need to get ready to act on existing set
      $user->clearlist;
	  $user->astrlist->fromSPIRES;
      compareSimilar($hepcut, $spi, $user, $simauths,$simaffs);
	  $resp=$user->menu(prompt=>"You have an authorset",choicelist=>["Add to Hep", "Check Authors", "Check/Add Affils", "Re-extract",'Edit'],done=>"\n",vertical=>1);
    }
	last unless $resp; #to remove lock and move on...nneed to eventually change so we can remove note.
	if ($resp=~/re-extract/i){
		$user->clearlist;
		my $giva=useGiva('user'=>$user, 'irn'=> $irn ,'routine'=>$routine);

		if ($giva>0){
		    compareSimilar($hepcut, $spi, $user,$simauths,$simaffs);
			$user->editAstr("BULL = $pakey","process.authors");
		}
		elsif($giva<0){  #want to quit extracting
			$resp=0;
			next;   # we will loop back. If existing set, further options, if not, this will send exit
		}
		next;
	}

	if ($resp=~/Edit/i){
		$user->editAstr("BULL = $pakey","process.authors");
		next;
	}



	#
	#  Check for similar paper.  If already found, just use that one.
	#
    if (!$simirn){($simirn, $simauths,$simaffs) = checkSimilar($user, $irn);}
    compareSimilar($hepcut, $spi, $user, $simauths,$simaffs);


	if ($resp=~/Add to Hep/i){
		if ($user->editAstr("BULL = $pakey","process.authors") && $user->astrlist->mergetoSPIRES($irn,'hep')){
			$hepadded=1;
			$user->print("Added to HEP");
			last;
		}
		else{
			user->print("Not added to hep  check process.authors under find r $pakey");
			last;
		}
	}
	if ($resp=~/Check.Add Aff/i){
		 if($user->checkAffList($simaffs)){
		 	 $user->saveAstr("BULL=$pakey","process.authors");
		 }
   		else{
  			 $user->print("Nothing Changed, affiliations correct");
   		}
	}
	if ($resp=~/Check Authors/i){
		 if($user->checkNames($simauths,$hepcut)){
  				 $user->saveAstr("BULL=$pakey","process.authors");
   		}
   		else{
  			 $user->print("Nothing Changed, authors correct");
   		}
   		next;
	}


}




######
#
#   Tidy up, remove lock
#






 $user->print("Removing lock, moving on...");
 $new='hn(-0);';
 $spi->ask('sel hep');
 if( $spi->number("find irn $irn")){
 foreach ($spi->list('hn')){
 	   $new.= "hn=$_;" unless m/lots\.of\.authors\.lock/;
 }
 if ($hepadded){
 	$new.='note(-0);';
  	foreach ($spi->list('note')){
 	   	$new.= "note=$_;" unless m/Long Author List - awaiting/i;

 	}
 	$new.="HN=Authors obtained from Giva on $date by ".$ENV{'USER'}.";";
 }
 $spi->merge($new);
 }





sub useGiva {
	my %args=@_;
	my $routine     = $args{'routine'};
	my $user        = $args{'user'};
	my $irn         = $args{'irn'};
	my $spi         = Expect::Spires->new();

	my $modules='/afs/slac/g/library/perllib/Giva/Extractor/*.pm';
	my @routines=('Paste');
	push @routines, split /\n/, `ls $modules`;
	foreach (@routines) {s<^.*/(\w+)\.pm><$1>;}


	my %extra = (
		"Coll"  => "Generic collaborations",
		"Babar" => "BaBar EPRINTS-might work for others",
		"Paste" => "cut and paste using web browser",
		"Coll2" => "very experimental (hoc\'s routine)",
	);

	if ( !$routine ) {
		$routine = $user->menu(
			prompt => 'Choose a routine to use to extract authors',choicelist=>\@routines,extra=>\%extra,done=>"\n",vertical=>1);
    }
   return(-1) unless $routine;
my $giva = Giva->new(
	input=>$user,
	spi=>$spi,
	verbose=>$args{v},
	irn=>$irn,
	eprint=>$lanl,
	method=>$routine,
	ext=>'auths',
	flatfile=>$args{f},
	);


$giva->file('tex');
$giva->file('pdf') if $routine =~m/pdf/i;
$giva->file('paste') if $routine =~/paste/i;



##
# See what we got
#

if (my $auths=$giva->extract){
   $user->astrlist($auths);
   $user->print("Extraction Succeeded");
   return(1);

}
else{
  	warn "extraction failed\n";
  	return(0);
}

}


sub checkSimilar {


	my $user     = shift;
	my $irn      = shift;
	my @simauths = ();
	my @simaffs  = ();
	my $simirn   = 0;

my $spi=Expect::Spires->new('database'=>'hep');
$spi->ask("find irn $irn");

my $cn=$spi->list("cn");
my $exp=$spi->list("exp");


$cn=~s/\bthe\b//gi;
$cn=~s/\bcollaboration\b//gi;
my $year=This_Year;
$year--;
	$user->checkedit( element => "Collaboration", db => $spi );
	$cn = $spi->element("cn");
	if ( $cn && !$exp ) {
		$spi->ask(
			'sel exp');
	if ($spi->number("find k $cn")>0){
		$spi->number("also cn str $cn");
		$spi->ask("seq ds(d)");
		$exp=$spi->list("exp");
	}
}
if ($exp){
	$spi->ask('sel exp',"find exp $exp");
	$exptitle=$spi->list('title');
	$expon=$spi->list('on');
	$expcol=$spi->list('cn');
}
$spi->ask('sel hep',"find irn $irn");

$user->print("My best guess is\nExperiment is:$exp\nTitle:$exptitle\n(aka: $expon)\nCol:$expcol\n\n");
$spi->merge("exp=$exp;") if $exp;
$user->checkedit(element=>"Experiment",db=>$spi);


$user->print("Finding a similar paper for comparison, takes a moment...\n");

$spi->ask('sel hep');
if ($spi->number("find (exp $exp or cn $cn) and date >= $year")>2 && $spi->number("and not irn $irn and not note str temporary and not note str awaiting")> 0
 	&& $spi->number("also a occ > 9")> 0
 	){
	$spi->ask("seq ds(d)","set for matchdesyplus");
	$simirn=$spi->list('irn');
	$spi->ask("find irn $simirn");
	$user->print($spi->ask("typ"));
	if($user->question(prompt=>"Is this a recent similar paper",default=>'Y')){
		$user->print("OK I will use this paper for comparison\n");
		 @simauths=$spi->list('a');
		 @simaffs=$spi->list('aff');
		 foreach (@simauths){
   		    $simauths->{$_}++;

   }


	}
	else {$user->print("OK I won\'t try to compare to anything.  No problem\n")}
}
else{$user->print("No similar papers could be found.  No problem\n")}


    return ( $simirn, $simauths, \@simaffs);
}

sub compareSimilar {

	my $hepcut   = shift;
	my $spi      = shift;
	my $user     = shift;
	my $simauths = shift;
	my $simaffs=shift;  #not yet used


	my $numAffs   = 0;
	my $numAuths  = 0;
	my $goodAffs  = 0;
	my $goodAuths = 0;
	foreach my $aff ( $user->astrlist->allAffs ) {
		$numAffs++;
		$goodAffs++ if ( $user->checkAff($aff) );
	}
	$spi->ask(
		'sel hep');
foreach my $auth( $user->astrlist->allAuths){
	$numAuths++;
    $goodAuths++	if ($simauths->{$auth} || ($hepcut && $spi->number("find ea $auth and not note temporary")>$hepcut));

}

my $badAuths=$numAuths-$goodAuths;
my $badAffs=$numAffs-$goodAffs;

$user->print("  Authors:  found  $numAuths   ($badAuths need checking)");
$user->print("     Affs:  found  $numAffs   ($badAffs need checking)");


}


