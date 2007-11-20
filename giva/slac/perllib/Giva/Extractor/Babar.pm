package Giva::Extractor::Babar;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract {
	my $self = shift;
	return (0) unless $self->ext eq 'auths';
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
	my $clean     = '';

	warn "extracting from tex file " . $self->file . "\n" if $self->verbose;
	if ( !( open( TEX, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}
	while (<TEX>) {
		chomp;
		s/\%.*$//g unless (m/\%\% author/);    #LaTeX comments
		s/\\\\/\n/g;
		s/\\&/ and /g;
		s/--/-/g;

		if ( !(m/\w/) ) {
			$_ = "$_\n";
		}
		$clean .= "$_\n";
	}
	close(TEX);
	$foundauth = 0;
	$foundaff  = 0;
	foreach ( split /\n/, $clean ) {
		print "$_\n" if $self->verbose;
		$foundauth = 0;

		if (/\%\% author list/) {
			$bibKey = 2;    #second babar style names and \inst
		}
		if (/The \\babar\\ Collaboration\,/) {
			$bibKey = 2;
		}
		if (/\\author\{/) {
			$bibKey = 1;    #first babar style \author \affiliation
		}
		if (/\\begin\{abstract/i) {
			$bibKey = 0;
		}
		if ( $bibKey == 1 ) {
			s/~/ /g;
			s/\s+/ /g;
			s/\\[^\w]\{([^\}]+)\}/$1/g;
			s/\\[^\w]//g;
			s/\\([A-z])/$1/g;
			s/\;//g;
			if (
/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/
			  )
			{
				$auth      = "$5, $1 $2 $3 $4";
				$foundauth = 1;
			}
			elsif (
/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/
			  )
			{
				$auth      = "$4, $1 $2 $3";
				$foundauth = 1;
			}
			elsif (/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/)
			{
				$auth      = "$3, $1 $2";
				$foundauth = 1;
			}
			elsif (/author\{([$namechars]+\.)\s*([^\}]+)\}/) {
				$auth      = "$2, $1";
				$foundauth = 1;
			}
			elsif (/affiliation\{([^\}]+)\}/) {
				$aff      = "$1";
				$foundaff = 1;
			}
		}
		if ( $bibKey == 2 ) {
			s/^\\inst\{/\#\#AFFIL\{/g;
			s/\\foot note[^\s]*//g;
			s/~/ /g;
			s/\\.{1}\{([^\}]{1,2})\}/$1/g;
			s/\s+/ /g;
			s/\\[^\w]//g;
			s/\\([A-z])/$1/g;
			s/\;//g;

			if (/\{([$namechars\.\s]+\.)\s([$namechars\s]+)\,?\s*\}/) {

				$auth      = "$2, $1";
				$foundauth = 1;
			}
			elsif (
/^([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\,]+)/
			  )
			{
				$auth      = "$5, $1 $2 $3 $4";
				$foundauth = 1;
			}
			elsif (
/^([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\,]+)/
			  )
			{
				$auth      = "$4, $1 $2 $3";
				$foundauth = 1;
			}
			elsif (/^([$namechars]+\.)\s*([$namechars]+\.)\s*([^\,]+)/) {
				$auth      = "$3, $1 $2";
				$foundauth = 1;
			}
			elsif (/^([$namechars]+\.)\s*([^\,]+)/) {
				$auth      = "$2, $1";
				$foundauth = 1;
			}
			elsif (/^\#\#AFFIL\{([^\}]+)\}/) {
				$aff      = "$1";
				$foundaff = 1;
			}
			else    #found nothing don't write it
			{
				next;
			}
		}
		if ($foundauth) {
     		$self->foundAuth($auth);
		}
		if ($foundaff) {
			$self->foundAff($aff);
			$foundaff = 0;
		}
	}

	print "EXTRACTED = ".$self->extracted."\n" if $self->verbose;
	return($self->extracted);

}


1;