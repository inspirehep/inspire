
package Giva::Extractor;


=pod

=head Giva::Extractor

This is a base class that is meant to be subclessed with a specific method for extracting things.

It should probably have a $user data as well to mediate interaction with user, but this isn't done yet.

The base class provides the following data with standard get/set:

=over

=item file

The file name of the file to use to extract from

=item ext

What you want to extract (currently "auths" or "refs")

=item spi

An Expect::Spires object for doing lookups

=item refs

An array of references extracted

=item Astrlist

An Astrlist object to contain the extracted list of auths

=item verbose

1 for verbose, 0 for silence

=item extracted

Count of objects extracted


=over

=head  Base Class Methods






=cut


use Class::Struct;
use Expect::Spires;
use Astrlist;
use Inputter::Authors;

struct Giva::Extractor {
	file     => '$',
	ext      => '$',
	spi      => 'Expect::Spires',
	refs     => '@',
	Astrlist => 'Astrlist::Input',
	verbose  => '$',
	extracted=> '$',
};

=item foundAff

The method can be called by the extractor whenever an affiliation is found.  It takes care of adding to the
Astrlist

  $self->foundAff($aff)

It calls the following Astrlist methods

	addAff
	parseAddAff
	mergeDupAff
	addAstr

This should take care of a basic attempt at parsing affiliations out of $aff, adding them to the Astrlist, and
making sure that 2 astrs with the same affs are merged.  If you don't like the basic parsing, try to parse it yourself before using
foundAff, then pass a valid ICN as $aff.

Prints a "+" so that inputter can see that things are moving along...


=cut


sub foundAff {
	my $self=shift;
	my $aff=shift;
	chomp($aff);
			$aff =~ s/\s+$//g;
			$self->Astrlist->addAff($aff)
			  unless ($aff && $self->Astrlist->parseAddAff($aff));
			if ( $aff && $self->Astrlist->mergeDupAff ) {
				print "added to prev astr\n" if $self->verbose;
			}
			else {
				$self->Astrlist->addAstr();
				print "added new astr\n" if $self->verbose;

			}
			$self->extracted($self->extracted + 1);
			print $self->extracted if $self->verbose;
			print "+";
}

=item foundAuth

The method can be called by the extractor whenever an author is found.  It takes care of adding to the
Astrlist

  $self->foundAuth($auth)

It calls the following Astrlist methods

	addAstr
	addAusth

This takes care of adding the author to the list, incrementing the $self->extracted count, and does some basic
text munging on the author name.  (removes {}, spaces, newlines, attempts to reposition name around commas ***Needs work here)

If you trim all this and take care of it before passing then it won't do anything (if a name contains a "," it doesn't touch it.)

Prints a "+" so that inputter can see that things are moving along...


=cut

sub foundAuth {
	my $self=shift;
	my $auth=shift;
            $self->Astrlist->addAstr() if $self->Astrlist->astrIdx < 0;
	$auth =~ s/\{//g;
	$auth =~ s/\}//g;
	chomp($auth);
	$auth =~ s/\s+$//;
	$auth =~ s/\s+\,/\,/g;
	if ( $auth !~ m/\,/ ) {
	   $auth =~ s/(\w+)\s+(.+)/$2,$1/;
	}
	$self->Astrlist->addAuth($auth);

	$self->extracted($self->extracted + 1);
	print $self->extracted if $self->verbose;

	print '+';
	}

	sub useTeXrefs{
		my $self=shift;
		use lanl;
		my $tmpname=$self->file;
		system('cp', $self->file, "$tmpname.tex");
		$extracted=&lanl::ExtractTexFile("$tmpname.tex");
		print "Found $extracted refs in $tmpname.extract\n" if $self->verbose;
		if ($extracted && (-e "$tmpname.extract"))
		{
   		 	open(EXTRACT,"< $tmpname.extract") || warn "Can't open extracted refs:$!";
			my @lines=<EXTRACT>;
			map {print "extracted: $_\n"} @lines if $self->verbose;
			$self->refs(\@lines);
			close(EXTRACT);
		}
		else
	{
    	warn "Givapdf Failed to extract\n";
    	$extracted=0;
	}
	unlink "$tmpname.tex" unless $self->verbose;
	unlink "$tmpname.extract" unless $self->verbose;
	return($extracted);

	}

=pod

=head Methods for subclasses

A subclass should at the least, supply an extract method which returns the number extracted, and modifies
$self->Astrlist $self->refs as appropriate.


=cut




package Giva::Extractor::Paste;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract {
	my $self = shift;
	return($self->ext_auths) if $self->ext eq 'auths';
	return($self->ext_refs) if $self->ext eq 'refs';
}

sub ext_auths{
	my $self=shift;
	$self->Astrlist(
		Astrlist::Input->new(
			spi     => $self->spi,
			astrIdx => -1,
			verbose => $self->verbose
		)
	);
	warn "Starting extraction\n" if $self->verbose;
	my $bibKey    = 0;
	my $namechars = "A-z\-";
	my $extracted = 0;
	my @lines     = ();
	local $/;    #read whole file
	warn "extracting from paste file " . $self->file . "\n" if $self->verbose;

	if ( !( open( TEXT, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
	while (<TEXT>) {
		s/\n/ /g;
		s/,/\n/g;
		s/\d+/\n/g;
		@lines = split /^/;
	}
	close(TEXT);
	$foundauth = 0;
	$foundaff  = 0;
	foreach my $word (@lines) {

		chomp($word);

	#  $word =~ s/(\s)[a-z\?](\W)/$1,$2/g;#For when there is no comma separation
		$word =~ s/\s+$//;
		$word =~ s/\s\s+/ /g;
		$word =~ s/[^\w\s\,\.\-\&\'\(\)\[\]\?]//g;  # strip everything but these

		#   $word =~ s/\?//g;
		if (   $word =~ /^[\d]+[A-Z]/
			|| $word =~ /univ/i
			|| $word =~ /(institut|laboratory)/i )
		{
			$word =~ s/[0-9]//g;
			if (   $word =~ /([A-Za-z\s-]+) Univ/
				|| $word =~ /Univ[a-z]+ of ([A-Za-z\s-]+)/
				|| $word =~ /Univ[a-z]+ ([A-Za-z\s-]+)/ )
			{
				$word = "$1 U.";
			}
			foreach $institution (@institutions) {
				if ( grep /$institution/, $word ) {
					$word = "$institution";
				}
			}
			$self->foundAff($word);
			next;
		}

		$word =~ s/,\s?,/,/g;
		$word =~ s/\s$//g;
		$word =~ s/,$/;/;
#		$word =~ s/^/ AUTHOR = /;
#		$word =~ s/$/;/;
#		$word =~ s/,/;\n AUTHOR = /g;
#		$word =~ s/ and /;\n AUTHOR = /g;
		$word =~ s/\./\. /g;
		$word =~ s/([A-Z]\.) ([A-Z]\.)/$1$2/g;
		$word =~ s/\s\s+/ /g;
		$word =~ s/\s+;/;/g;
		$word =~ s/;[a-z];/;/g;
		$word =~ s/([a-z])\'([a-z])/$1$2/g;
		$word =~ s/;;/;/g;
		$word =~ s/([A-Za-z\s\.]+) ([Vvaonder\s]+) ([A-Za-z\s]+)/$2 $3, $1/;
		$word =~ s/([A-Za-z\s\.]+) ([DdEela\s]+) ([A-Za-z\s]+)/$2 $3,$1/;
#		$word =~ s/AUTHOR =;/AUTHOR =/;

		$self->foundAuth($word);


	}

	print "EXTRACTED = ".$self->extracted."\n" if $self->verbose;
	return ($self->extracted);


}


sub ext_refs{
	my $self=shift;


### do some init work
	warn "Starting extraction\n" if $self->verbose;
	my $extracted = 0;
	my @lines     = ();


##  Read in the file

#{
#    local $/;    #read whole file
	warn "extracting from paste file " . $self->file . "\n" if $self->verbose;

	if ( !( open( TEXT, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
    my @tidylines=();
    push @tidylines, 'REFERENCES';
	while (my $info=<TEXT>) {
    	chomp($info);
#should jump to print if one of the newlines match?

     $info =~ s/^(\d+)\. /\[$1\] /g; #converting various
            $info =~ s/^(\d+)\) /\[$1\] /g; #reference numbering
            $info =~ s/^\((\d)\) /\[$1\] /g;#schemes to the usual one.
            $info =~ s/^\((\d{2})\) /\[$1\] /g;
            $info =~ s/^\((\d{3})\) /\[$1\] /g;
            $info =~ s/\[[A-Z][a-z]{2,5}(\d+)[a-z]?\] /\[$1\] /g;
#            $info =~ s/(\((19|20)\d{2}\))\s*(\d+)\./, $3 $1\.\n\n/g;
            $info =~ s/(\((19|20)\d{2}\))\./$1\.\n\n/g;
	        $info =~ s/(\d)\.(?!\d)/$1\n\n\./g;
            $info =~ s/([a-z]+-[a-z]+[\/\s]?\d{7})/\n$1\n/g;
            $info=~ s/(\[\d+\] )/\n\\\\\n$1/g; #insert newlines
            push @tidylines,"$info ";
	}
	close(TEXT);
	if ( !( open( TEXT, ">".$self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
	map {print TEXT  "$_\n";} @tidylines;
	map {print "tidylines: $_\n";} @tidylines if $self->verbose;
	return($self->useTeXrefs);


}



package Giva::Extractor::TeX;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract{
	$self=shift;
	return($self->useTeXrefs);
}


package Giva::Extractor::Text;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract{
	$self=shift;


		my $extracted = 0;
	my @lines     = ();


##  Read in the file

#{
#    local $/;    #read whole file
	warn "extracting from PDF file " . $self->file . "\n" if $self->verbose;

	if ( !( open( TEXT, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}

    my @tidylines=();
    push @tidylines, 'REFERENCES';
    my $textTag=0;
	while ( my $info=<TEXT>) {
    	chomp($info);
#should jump to print if one of the newlines match?
  if ( ($info =~ /References/ || $info =~ /REFERENCES/
				 || $info =~ /Bibliography/
                                 || $info =~ /Literature/)
       )
	#  && !($info =~/[0-9]/) )
      {
          $textTag=1;
      }
      if ($info =~ / \[\d+\] /&& $info !~ /[A-Za-z]/ && $textTag==0)
      {
          $textTag=1;
      }
      if ($info =~ / \[\d+\] [\w\s\.]+\,[\w\s\.\,\(\)]+\d+/ && $textTag==0)
      {
          $textTag=1;
      }
      if ($info =~ /\WFIGURE\W/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($info =~ /\WFIG.\s?1/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($info =~ /\WTABLE\W/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($textTag)
      {
#should jump to print if one of the newlines match?
            $info =~ s/^(\d+)\. /\[$1\] /g; #converting various
            $info =~ s/^(\d+)\) /\[$1\] /g; #reference numbering
            $info =~ s/^\((\d)\) /\[$1\] /g;#schemes to the usual one.
            $info =~ s/^\((\d{2})\) /\[$1\] /g;
            $info =~ s/^\((\d{3})\) /\[$1\] /g;
            $info =~ s/\[[A-Z][a-z]{2,5}(\d+)[a-z]?\] /\[$1\] /g;
            $info =~ s/(\((19|20)\d{2}\))\./$1\.\n\n/g;
	     $info =~ s/(arxiv\:\d{4}\.\d+)/\n$1\n/g;
	     $info =~ s/\((doi\:[^)]+)\)/\n$1\n/g;
	         $info =~ s/[^:\d](\d+)\.(\D)/$1\n\n\.$2/g;


            $info =~ s/([a-z]+-[a-z]+[\/\s]?\d{7})/\n$1\n/g;
            $info=~ s/(\[\d+\] )/\n\\\\\n$1/g; #insert newlines
            push @tidylines,"$info ";
	}
	}
	close(TEXT);
	if ( !( open( TEXT, ">".$self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
	map {print TEXT  "$_\n";} @tidylines;
	map {print "tidylines: $_\n";} @tidylines if $self->verbose;
	return($self->useTeXrefs);

}



package Giva::Extractor::PDF;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract{
	$self=shift;


		my $extracted = 0;
	my @lines     = ();


##  Read in the file

#{
#    local $/;    #read whole file
	warn "extracting from PDF file " . $self->file . "\n" if $self->verbose;

	if ( !( open( TEXT, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}

    my @tidylines=();
    push @tidylines, 'REFERENCES';
    my $textTag=0;
	while ( my $info=<TEXT>) {
    	chomp($info);
#should jump to print if one of the newlines match?
  if ( ($info =~ /References/ || $info =~ /REFERENCES/
				 || $info =~ /Bibliography/
                                 || $info =~ /Literature/)
       )
	#  && !($info =~/[0-9]/) )
      {
          $textTag=1;
      }
      if ($info =~ / \[\d+\] /&& $info !~ /[A-Za-z]/ && $textTag==0)
      {
          $textTag=1;
      }
      if ($info =~ / \[\d+\] [\w\s\.]+\,[\w\s\.\,\(\)]+\d+/ && $textTag==0)
      {
          $textTag=1;
      }
      if ($info =~ /\WFIGURE\W/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($info =~ /\WFIG.\s?1/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($info =~ /\WTABLE\W/i && $textTag==1)
      {
          $textTag=0;
      }
      if ($textTag)
      {
#should jump to print if one of the newlines match?
            $info =~ s/^(\d+)\. /\[$1\] /g; #converting various
            $info =~ s/^(\d+)\) /\[$1\] /g; #reference numbering
            $info =~ s/^\((\d)\) /\[$1\] /g;#schemes to the usual one.
            $info =~ s/^\((\d{2})\) /\[$1\] /g;
            $info =~ s/^\((\d{3})\) /\[$1\] /g;
            $info =~ s/\[[A-Z][a-z]{2,5}(\d+)[a-z]?\] /\[$1\] /g;
            $info =~ s/(\((19|20)\d{2}\))\./$1\.\n\n/g;
	          $info =~ s/([a-z]+-[a-z]+[\/\s]?\d{7})/\n$1\n/g;
	           $info =~ s/(arxiv\:\d{4}\.\d+)/\n$1\n/g;
	         $info =~ s/(\d)\.(\D)/$1\n\n\.$2/g;

            $info=~ s/(\[\d+\] )/\n\\\\\n$1/g; #insert newlines
            push @tidylines,"$info ";
	}
	}
	close(TEXT);
	if ( !( open( TEXT, ">".$self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
	map {print TEXT  "$_\n";} @tidylines;
	map {print "tidylines: $_\n";} @tidylines if $self->verbose;
	return($self->useTeXrefs);

}
1;

