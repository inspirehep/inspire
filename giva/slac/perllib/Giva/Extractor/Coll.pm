
package Giva::Extractor::Coll;

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
		s/\%.*$//g;    #LaTeX comments
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

		if (/\\author/) {
			$bibKey = 1;    #simple \author commands
		}
		if (/\\begin\{Authlist\}/i) {
			$bibKey  = 1;
			$needEnd = "titlepage";
		}
		if ( ($needEnd) && (m/\\end\{$needEnd\}/) ) {
			$bibKey = 0;
		}

		if (m/\\begin\{abstract/i) {
			$bibKey = 0;    # almost certainly done
		}

		if (/\\end\{titlepage/i) {
			$bibKey = 0;    # almost certainly done
		}

		if (/\\section\{/i) {
			$bibKey = 0;    # almost certainly done
		}

		if ( $bibKey == 1 ) {
			s/\\author[^\{]+\{/\\author\{/g;
			s/\\address[^\{]+\{/\\address\{/g;
			s/\\Instfoot\{[^\}]+\}\{/affiliation\{/;
			if ( !(m/author|affiliation|address/) && m/\\Iref/ ) {
				s/^([^\\]*)\\Iref.*\,/author\{$1\}/;
			}
			s/~/ /g;
			s/\s+/ /g;
			s/\\thanksref\{.*\}//g;
			s/\\[^\w]\{([^\}]+)\}/$1/g;
			s/\\{\[^\w]([^\}]+)\}/$1/g;
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
			elsif (/address\{([^\}]+)\}/) {
				$aff      = "$1";
				$foundaff = 1;
			}

			if ($foundauth) {
				$self->foundAuth($auth);	
			}		
				if ($foundaff) {
					$self->foundAff($aff);
					$foundaff = 0;

				}
			
		}
	}
	if (!$extracted){
		my @auths=();my %aff=();my %num=();
		foreach ( split /\n/, $clean ) {
		print "$_\n" if $self->verbose;
		$foundauth = 0;
	s/\s+/ /g;
			s/\\thanksref\{.*\}//g;
			s/\\[^\w]\{([^\}]+)\}/$1/g;
			s/\\{\[^\w]([^\}]+)\}/$1/g;
			s/\\[^\w]//g;
		if (/\\author/) {
			$bibKey = 1;    #simple \author commands
		}
		if (/\\begin\{Authlist\}/i) {
			$bibKey  = 1;
			$needEnd = "titlepage";
		}
		if ( ($needEnd) && (m/\\end\{$needEnd\}/) ) {
			$bibKey = 0;
		}

		if (m/\\begin\{abstract/i) {
			$bibKey = 0;    # almost certainly done
		}

		if (/\\end\{titlepage/i) {
			$bibKey = 0;    # almost certainly done
		}

		if (/\\section\{/i) {
			$bibKey = 0;    # almost certainly done
		}

		if ( $bibKey == 1 ) {
		print "saw:\n $_\n in second\n" if $self->verbose;
			if (/^([$namechars]+\.+)\~([^\}\,]+),\$\^\{(\d+)/){
				$auth      = "$2, $1";
				push @auths, $auth;
				$num{$auth}=$2;
			}
			elsif (/\\centerline\{\$\^\{(\d+).*\}\$(.*)\}?$/){
				$aff      = "$2";
				$aff{$1}=$aff;
			}
		}
		}
		foreach (@auths){
			print "adding $_ with aff $aff{$num{$_}}";
			$self->foundAuth($_);		
			$self->foundAff($aff{$num{$_}}) if ($aff{$num{$_}});
			
		}
		
	}
	
	
		print "EXTRACTED = ".$self->extracted."\n" if $self->verbose;
	return ($self->extracted);
	

}