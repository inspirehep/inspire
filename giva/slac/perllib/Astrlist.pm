	package astr;

	use Inputter;
	use Class::Struct;

	struct astr => {
		auth => '@',
		aff  => '@',
	};

	sub addAff {
		my $self = shift;
		my $aff  = shift;
		push @{ $self->aff }, $aff;
		return $self;
	}

	sub addAuth {
		my $self = shift;
		my $auth = shift;
		push @{ $self->auth }, $auth;
		return $self;
	}

	sub toSPIRES {
		my $self   = shift;
		my $return = " ASTR;\n";
		foreach ( @{ $self->auth } ) {
			s/^\s*//;
			s/\s*$//;
			$return .= "  A = $_;\n";
		}
		foreach ( @{ $self->aff } ) {
			s/^\s*//;
			s/\s*$//;
			$return .= "    AFF = $_;\n";
		}
		return('') if $return !~ m/AF?F? =/;
		return ($return);
	}

=pod

=head1 Astrlist

A package with several convenience methods for dealing with author lists, should eventually rely on a SPIRES Record
structure class...

=cut

	package Astrlist;
	use Class::Struct;

	struct Astrlist => {
		guess   => '%',
		astrs   => '@',
		astrIdx => '$',
		spi     => '$',
		verbose => '$',
	};

=head2 Data Members

Uses Class::Struct get/set accessors and initialization

(init via

Astrlist->new(spi=>$spi,guess=>%guesses)

or similar)

my $idx=$astrlist->astrIdx;
$astrlist->astrIdx(3);



=over

=item guess

A hash that contains guessed affiliations for authors in the astrlist.  Useful only in Inputting

=item astrs

Array contains astr objects:

=over

=item auth

Array of authors

=item aff

Array of affs

=item addAuth/addAff

Appends an auth or aff to the astr

=item toSPIRES

Prints a SPIRES-like record of the astr

=back

=item astrIdx

Number denoting the current astr.  Most adding methods default to this astr.

=item spi

An Expect::Spires object used for lookups.


=back

=head2 Methods


=item astrIdx_incr

Moves the astrIdx counter up by one, and returns the new index.

=cut

	sub astrIdx_incr {
		my $self = shift;
		return $self->astrIdx( ( $self->astrIdx ) + 1 );

	}


=item allAffs

Prints all affiliations in flat list  Returns array.  List is unique

=cut

	sub allAffs {
		my $self   = shift;
		my @return = ();
		my %seen   = ();
		foreach $astr ( @{ $self->astrs } ) {
			foreach $a ( @{ $astr->aff } ) {
				push( @return, $a ) unless $seen{$a}++;
			}
		}
		return (@return);
	}


=item allAuths

Prints all affiliations in flat list  Returns array.  List is unique

=cut

	sub allAuths {
		my $self   = shift;
		my @return = ();
		my %seen   = ();
		foreach $astr ( @{ $self->astrs } ) {
			foreach $a ( @{ $astr->auth } ) {
				push( @return, $a ) unless $seen{$a}++;
			}
		}
		return (@return);
	}

=item addAff

astrlist->addAff(aff,<astr index>)

Appends aff to the specified astr, defaults to current astr.

=cut

	sub addAff {
		my $self = shift;
		my $aff  = shift;
		my $idx  = shift || $self->astrIdx;
		$self->astrs($idx)->addAff($aff);
		return ($self);
	}

=item addAuth

astrlist->addAuth(auth,<astr index>)

Appends auth to the specified astr, defaults to current astr.

=cut

	sub addAuth {
		my $self = shift;
		my $auth = shift;
		my $idx  = shift || $self->astrIdx;
		$self->astrs($idx)->addAuth($auth);
		return ($self);

	}

	sub auth {
		my $self = shift;
		my $auth = shift;
		my $idx  = shift || $self->astrIdx;
		return @{ $self->astrs($idx)->auth } if wantarray;
		return $self->astrs($idx)->auth->[0];
	}

=item addAstr

astrlist->addAstr(<%astr>)

Call with no arg to create a new empty astr

Can take a hash arg

auth=>\@auths,

aff=>\@affs

and appends to the auth list, also increments the astrIdx


=cut

	sub addAstr {
		my $self  = shift;
		my %astr  = @_;
		my @auths = @{ $astr{auth} };
		my @affs  = @{ $astr{aff} };

		my $add = astr->new( auth => [@auths], aff => [@affs] );

		push @{ $self->astrs }, $add;
		$self->astrIdx_incr;
		return (1);
	}


=item findAstr

 astrlist->findAstr(auth=><auth>,aff=><aff>)

takes hash arg with either <auth> or <aff> specified

for now, args must match exactly (perl 'eq')

returns (and sets) Idx to this astr

=cut


	sub findAstr {
		my $self  = shift;
		my %args=@_;
		if ($args{aff}){$get='aff'}
		elsif ($args{auth}){$get='auth'}
		my $match=0;
		$self->astrIdx(0);
		foreach $astr (@{$self->astrs}){
			foreach $val(@{$astr->$get} ){

				if ($val eq $args{$get}){
					$match++;
					last;

				}
			}
			last if $match;
			$self->astrIdx_incr;
		}
		return($self->astrIdx) if $match;
		return(-1);
	}


=pod

=item repAuth

astrlist->repAuth(old=>"old",new=>["new1","new2"])

Call with no "new" to delete an auth  otherwise replaces

returns 1 if it thinks it succeeded


=cut

  sub repAuth {
		my $self  = shift;
		my %args  = @_;
		@new=@{$args{new}};
		@new=() unless $new[0];
		return(0) unless $args{old};
		$idx=$self->findAstr(
			auth=>$args{old}
		);
		if ($idx==-1){
			carp("Nothing found matching $args{old}");
			return(0);
		}
		while ($idx > -1){
			my @newauths=();
			my $astr=$self->astrs->[$idx];
			my @auths = @{$astr->auth};
			my @affs  = @{$astr->aff};
			foreach $auth (@auths){

				if($auth ne $args{old}){
					push @newauths,$auth
				}
				elsif (@new){
					push @newauths, @{$args{new}}
				};

			}
		    $self->repAstr($idx,auth=>\@newauths,aff=>\@affs);
			$idx=$self->findAstr(
				auth=>$args{old}
			);

		}

		return (1);
	}



=item repAff

astrlist->repAff(old=>"old",new=>["new1","new2"])

Call with no "new" (or new[0]=false) to delete an aff  otherwise replaces

returns 1 if it thinks it succeeded


=cut
		sub repAff {
		my $self  = shift;
		my %args  = @_;
		@new=@{$args{new}};
		@new=() unless $new[0];
		return(0) unless $args{old};
		$idx=$self->findAstr(
			aff=>$args{old}
		);
		if ($idx==-1){
			carp("Nothing found matching $args{old}");
			return(0);
		}
		while ($idx > -1){
			my @newaffs=();
			my $astr=$self->astrs->[$idx];
			my @auths = @{$astr->auth};
			my @affs  = @{$astr->aff};
			foreach $aff (@affs){

				if($aff ne $args{old}){
					push @newaffs,$aff
				}
				elsif (@new){
					push @newaffs, @new;
				};

			}
		    $self->repAstr($idx,auth=>\@auths,aff=>\@newaffs);
			$idx=$self->findAstr(
				aff=>$args{old}
			);

		}

		return (1);
	}

=item repAstr

astrlist->repAstr(idx,<%astr>)

Call with no arg to blank an astr

Can take a hash arg

auth=>\@auths,

aff=>\@affs

and replaces in the auth list


=cut
		sub repAstr {
		my $self  = shift;
		my $idx=shift;
		my %astr  = @_;

		my @auths = @{ $astr{auth} };
		my @affs  = @{ $astr{aff} };

		my $add = astr->new( auth => [@auths], aff => [@affs] );

		$self->astrs->[$idx]=$add;

		return (1);
	}



=item mergeDupAff

Checks current astr for duplication in affs with previous.
If all affs are the same appends current auths to previous,
blanks the current astr and returns 1
otherwise returns 0


=cut

	sub mergeDupAff{
		my $self=shift;
		my $idx=$self->astrIdx;
		return(0) unless $idx>0;
		my $lastIdx=$idx -1;
		my @lastaffs=@{$self->astrs->[$lastIdx]->aff};
		my @affs=@{$self->astrs->[$idx]->aff};
		my $diff=0;
		for (my $i=0;$i<= @lastaffs;$i++){
				print "comparing $lastaffs[$i] ne $affs[$i]\n" if $self->verbose;
				if ($lastaffs[$i] ne $affs[$i]){$diff=1;last;}
		}
		$diff=1 unless @lastaffs==@affs;
		if ($diff){
			return(0);
		}
		foreach (@{$self->astrs->[$idx]->auth}){
		   $self->addAuth($_,$lastIdx);
		}
		$self->repAstr($idx);
		return(1);
	}

=item dump

Uses Data::Dumper  to dump the list

=cut

	sub dump {
		my $self = shift;
		use Data::Dumper;
		warn Dumper($self);

	}

=item toSPIRES

Prints a SPIRES-like list of all the astrs.  Ready for spires input.

=cut

	sub toSPIRES {
		my $self   = shift;
		my $return = '';
		foreach ( @{ $self->astrs } ) {
			$return .= $_->toSPIRES;

		}
		return ($return);

	}

=item fromSPIRES

reads SPIRES-like list of all the astrs.  reads from $self->spi current first result, unless a string=><string>
or spi=>spi is given.

=cut

	sub fromSPIRES {
		my $self   = shift;
		my $args = @_;
		my $string = $args{'string'};

		my $spi = $args{'spi'} ||$self->spi;
 		$self->addAstr();
 		$self->astrIdx(0);
		if (! $string){
			return(0) unless $spi->number('sho res');
			$string=($spi->ask('set elem astr','for res','dis','endf'))[2];
		}
		return(0) unless $string;
		@lines=split /;/, $string;
		my $count=0;
		foreach (@lines){
			chomp;
			if (m/astr/i){
				$self->addAstr() if $count;;
				$count++;
			}
			if (m/author = (.*);?/i){

				$self->addAuth($1);
				$count++;
			}
			if (m/affiliation = (.*);?/i){
				$self->addAff($1);
				$count++;
			}
		}
		return($count);

	}

=item addupdtoSPIRES

addupdtoSPIRES(key,<db>)

merges the astrlist to record irn in database db  (defaults to HEP)

uses the spi object and the toSPIRES output.

=cut

	sub addupdtoSPIRES {
		my $self = shift;
		my $irn  = shift;
		my $db   = shift || 'hep';
		return ( $self->spi->batch( 'addupd;' . "key=$irn" . $self->toSPIRES ."\n;\n", $db) );
	}



=item mergetoSPIRES

mergetoSPIRES(irn,<db>)

merges the astrlist to record irn in database db  (defaults to HEP)

kills any existing astrlist

uses the spi object and the toSPIRES output.

=cut

	sub mergetoSPIRES {
		my $self = shift;
		my $irn  = shift;
		my $db   = shift || 'hep';
		$self->spi->ask("sel $db");
		return ( $self->spi->merge( 'astr(-0);' . $self->toSPIRES, $irn ) );
	}

=item parseAff

parseAff(string)

uses the spi object and some other logic to parse a valid affiliation out of a string
returns array of affs found in the string;

Does not return anything if no match found

=cut

	sub parseAff {
		my $self        = shift;
		my $aff         = shift;
		my @return      = ();
		my $affOriginal = $aff;
		$aff =~ s/\(//g;
		$aff =~ s/\)//g;
		$aff =~ s/\// /g;
		$aff =~ s/ [uU]\.?[sS]\.?[sS]\.?[rR]\.?//;
		$aff =~ s/;$//;
		$aff =~ s/\[/ /g;
		$aff =~ s/\]/ /g;
		$aff =~ s/ at / /g;
		$aff =~ s/ and / /g;

		#    print "$aff\n";
		undef $icn;
		my $universityTag = 0;
		my $institution;
		my @institutions = qw(CERN DESY Rutherford Fermilab SLAC TRIUMF
		  Brookhaven Livermore Argonne);
		push @institutions, "Jefferson Lab";
		push @institutions, "Los Alamos";
		foreach $institution (@institutions) {

			if ( grep /$institution/, $aff ) {
				$aff = "$institution";
			}
		}
		$aff =~ s/^Livermore$/LLNL, Livermore/;
		$aff =~ s/.*Stanford Linear Accelerator Center.*/SLAC/;
		$aff =~ s/^Fermi National Accelerator Laboratory/Fermilab/;
		$aff =~ s/ [tT][hH][eE] / /g;
		$aff =~ s/ [aA][nN][dD] / /g;
		undef $icn;
		$self->spi->ask('sel inst');
		my $search;
		my $result = 0;
		my $iTag   = 0;

		while ( ( $result != 1 ) && ( $iTag < 8 ) ) {
			if ( $iTag == 0 ) {
				$search = "icncp";
			}
			$result = $self->spi->number("find $search $aff");

			#      print "  iTag=$iTag : find $search $aff : $result\n";
			$iTag++;
			if ( $result == 1 ) {
				$icn = $self->spi->element("icn");

				#        print "    iTag = $iTag : ICN = $icn\n";
			}
			if (   $result > 1
				&& $iTag == 3
				&& $aff =~ /Pasadena/
				&& $aff =~ /Cal/ )
			{
				if ( ( $aff =~ /Jet/i ) || ( $aff =~ /JPL/i ) ) {
					$aff = "Caltech, JPL";
				}
				else {
					$aff = Caltech;
				}
				$iTag = 0;
			}
			if ( $iTag == 1 ) {
				$search = "inst";
			}
			if ( $iTag == 2 ) {
				$search = "add";
			}
			if ( $iTag == 3 ) {
				$aff = "$aff#";
			}
			if ( $iTag == 4 ) {
				$search = "type TOP500 or type hep200 and add";
			}
			if ( $iTag == 5 ) {
				$search = "type ppf and add";
			}
			if ( $iTag == 6 ) {
				$aff =~ s/[Dd]ep[artment\.]+ of [A-Z][a-z\.]+//;
				$search = "add";
			}
			if ( $iTag == 7 && $universityTag == 0 ) {
				$aff           = $self->parseUniversity($aff);
				$universityTag = 1;
				$iTag          = 0;
			}

			#      $iTag++;
		}
		if ($icn) {
			push @return, $icn;
			print "Found $icn from $affOriginal\n" if $self->verbose;
		}

	return (@return);
	}

sub parseUniversity {
	  my $self   = shift;
	  my $aff    = shift;
	  my @cities = qw(Seattle Madison Urbana Chicago);
	  if (   $aff =~ /([A-Za-z\s-]+) Univ\w+/
		  || $aff =~ /Univ[a-z]+ of ([A-Za-z\s\-]+)/
		  || $aff =~ /Univ[a-z]+ ([A-Za-z\s\-]+)/
		  || $aff =~ /([A-Za-z\s-]+) U\./ )
	  {
		  my $name         = $1;
		  my $compoundName = 0;
		  foreach $city (@cities) {
			  if ( $aff =~ /$city/ && ( $name ne $city ) ) {
				  $aff          = "$name U., $city";
				  $compoundName = 1;
			  }
		  }
		  if ( $compoundName == 0 ) {
			  $aff = "$name U.";
			  if ( $name =~ /Cornell/ ) {
				  $aff = "$name U., Phys. Dept.";
			  }
			  if ( $name =~ /Stanford/ ) {
				  $aff = "$name U., Phys. Dept.";
			  }
		  }
	  }
	  return "$aff";
}

=item parseAddAff

parseAddAff(string, <idx>)

Just adds the parsed affs to the idx (default to current)

Returns number added

=cut

sub parseAddAff {
	  my $self   = shift;
	  my $string = shift;
	  my $idx    = shift;
	  my $num    = 0;
	  foreach ( $self->parseAff($string) ) {
		  $self->addAff( $_, $idx );
		  print "Parsed+added $_ to $idx\n" if $self->verbose;
		  $num++;
	  }
	  return ($num);

}

=over

=cut

1;

