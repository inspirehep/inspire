
package Astrlist::Input;
use Astrlist;

use vars qw(@ISA);
@ISA = qw(Astrlist);

my @listAffsandGuesses;

sub allAffsandGuesses {
		my $self   = shift;
		my @return = ();
		my %seen   = ();
		foreach $aff (@listAffsandGuesses){
			push( @return, $aff ) unless $seen{$aff}++;
		}
		foreach my $astr ( @{ $self->astrs } ) {
			foreach my $aff ( @{ $astr->aff } ) {
				push( @return, $aff ) unless $seen{$aff}++;
			}
		}
		foreach my $affarr ( values %{ $self->guess } ) {
			foreach $aff (@$affarr) {
				push( @return, $aff ) unless $seen{$aff}++;
			}
		}
		@listAffsandGuesses=@return;
		return (@return);

	}


sub guessAff {
		my $self   = shift;
		my $author = shift;
		my $spi    = $self->spi;
		my @return = @{ $self->guess($author) };
		if (@return) { return (@return) }
		my $spi = $self->spi;
		return (()) unless $author =~ m/(\w+),/;
		$lname = $1;

		if ( $spi->number("find ea $author") < 2 ) {

			if ( $spi->number("find a $author") < 2 ) {
				return (());
			}
			elsif ( $spi->number("also aff occ > 0 and a occ <10") < 1 ) {
				return (());
			}

		}
		elsif ( $spi->number("also aff occ > 0 and a occ <10") < 1 ) {
			if ( $spi->number("find a $author") < 2 ) {
				return (());
			}
			elsif ( $spi->number("also aff occ > 0 and a occ <10") < 1 ) {
				return (());
			}
		}

		#have a result here
		$spi->ask( "set fil for astr where a str $lname", "seq ds(d)" );
		@affs   = $spi->element('affiliation');
		@return = @{ $affs[0] };
		$self->guess( $author, [@return] );
		return (@return);
	}    #guessAff



	package Inputter::Authors;

	use Inputter;
	use vars qw(@ISA);
	@ISA = qw(Inputter);

	sub dump {
		my $self = shift;
		use Data::Dumper;
		warn Dumper($self);

	}


	sub clearlist{
		my $self=shift;
		my $list = Astrlist::Input->new( "astrIdx" => "-1", 'spi' => $self->{spi} );
		$self->{astrlist} = $list;
		return($list);
	}

	sub new {
		my $classname = shift;    # What class are we constructing?
		my %args      = @_;

		my $self = $classname->SUPER::new(%args);
		my $list = Astrlist::Input->new( "astrIdx" => "-1", 'spi' => $self->{spi} );
		$self->{astrlist} = $list;
		return ($self);
	}



	sub astrlist {
		my $self = shift;
		my $list=shift;
		if ($list){ return ( $self->{astrlist}=$list ); }
		return ( $self->{astrlist} );
	}

=pod

=item checkAuth



=cut

	sub checkAuth {

		#print "Next Author is: $auth\n";
		my $self = shift;
		my $auth = shift;
		$auth = $self->checkedit( value => $auth, name => 'Author' );
		return (0) if $auth eq '-';
		if ($auth=~m/^Q$/i){
			return(-1) if $self->question(prompt=>"Exit");
		}
		if ($auth =~ /[^\w\,\'\-\s\.]/ ) {

			#can add DB lookups here
			$self->print("This does not look like an author. Are you sure?");
			$auth = $self->checkedit( value => $auth, name => 'Author' );
		}
		return ($auth);
	}

	sub newInst {
		my $self = shift;
		my $aff  = shift;

		if ($aff) {
			push @{ $self->{newInst} }, $aff;
			return $aff;
		}
		elsif (wantarray) {
			return @{ $self->{newInst} };
		}
		else {
			return @#{ $self->{newInst} };
		}

	}

	sub checkAff {
		my $self = shift;
		my $aff  = shift;
		$self->spi->ask('sel inst');
		if ($self->spi->number("find icncp $aff") == 1){
	 		my $icn=$self->spi->list('icn');
	 		return($icn) if $icn eq $aff;
	 	}
		return (0);
	}

	sub getAffs {
		my $self = shift;
		my $list = $self->astrlist;
		my $auth = $list->auth( $list->astrIdx );
		my @affs = @_ ;
		@affs=$list->guessAff($auth) unless @affs;
		my $done=0;
		while ( ! $done ) {
			$done = $self->checkAffs(@affs);
			@affs = ();
		}
		return (1);
	}

	sub newAff {
		my $MAXRES = 7;
		my $max    = $MAXRES;
		my $self   = shift;
		my $aff = shift;
		my $auto++ if ($aff);
		if (!$aff){
		    $aff = $self->checkedit(
			prompt => "Inst search <cr> to exit: find inst ",
		);
		}
		return (0) unless $aff;
		my $tmp=$self->checkAff($aff);
		return ($tmp) if $tmp;
		my $spi = $self->spi;
        my %seen = ();
		my @icns = ();
		$spi->ask( "sel inst", "set format inst.lookup" );
		if ( $spi->number( "find icncp $aff not tag DEAD", 'seq pcnt(d)' ) > 0 ) {
			foreach ( $spi->element('icn') ) {
				$icn = $_->[0];
				push @icns, $icn unless $seen{$icn}++;
			}
		}
		elsif ( $spi->number( "find add $aff not tag DEAD", "seq pcnt(d)" ) > 0 ) {
			foreach ( $spi->element('icn') ) {
				$icn = $_->[0];
				push @icns, $icn unless $seen{$icn}++;
			}

		}
		my $i = 0;
		return($self->newAff()) if ($auto && @icns ==0);
		$self->print("Here are some possible matches");

		while () {
			%info = {};
			my @menu = ();
			for ( $i ; $i < $max ; $i++ ) {
				last unless $_ = $icns[$i];
				$spi->ask( "find icncp $_", 'set format inst.lookup' );
				$xtra = $spi->ask("typ");
				$info{$_} = $xtra;
				$xtra =~ s/^\s*\n\d+\)[^\n]+\n//;
				$xtra =~ s/\n\s*$//;
				$info{$_} = $xtra;
				push @menu, $_;
			}
			push @menu, 'NEWINST';
			push @menu, 'More Results' if @icns > $max;
			$aff = $self->menu(
				choicelist => \@menu,
				extra      => \%info,
				vertical   => 'true',
				done       => "\n",
			);
			chomp($aff);
			last unless $aff eq 'More Results';
			$max += $MAXRES;
		}
		$aff = $self->newAff unless $aff;
		if ( $aff eq 'NEWINST' ) {
			$aff = $self->checkedit(
				prompt =>
				  "Enter Best New Name for NEWINST, inst manager will check it",
				name => 'New Name'
			);
			$self->newInst($aff);
		}
		return ($aff);
	}

	sub error {
		my $self     = shift;
		my $msg      = shift;
		my $dump     = shift||$self->astrlist->toSPIRES;
		my $dumpfile = "$ENV{HOME}/authorfile.dump.$$";
		if ( open( TMP, ">$dumpfile" ) ) {

			print TMP  $dump;

			$self->print("Your work thus far has been saved in $dumpfile");
			$self->print(
"You can \n    use $dumpfile\n then edit and merge the corrections by hand"
			);
		}
		else {
			$self->print("Cannot open file:perhaps you need to klog?");
			$self->print(
				"Your work thus far has *NOT* been saved, but a copy is below");
			print $self->astrlist->toSPIRES;
		}
		$self->SUPER::error($msg);
	}

	sub checkAffs {
		my $self = shift;
		my @affs = @_;
		my $list = $self->astrlist;
		my $idx  = $list->astrIdx;
		my $auth = $list->auth($idx);
		if (@affs){
		   $list->astrs($idx)->aff( [] );
		}
		else{
			@affs=@{$list->astrs($idx)->aff()};
			 $list->astrs($idx)->aff( [] );

		}

		my %seen = ();
		my @menu = ();my @extra=();
		my $guess=join "\n              ", @affs;
		push @menu, "Current:\n              $guess\n";
		push @menu, 'Not on List';
		foreach my $aff (@affs) {
			push @menu, $aff unless $seen{$aff}++;

		}
		foreach my $aff ( $list->allAffsandGuesses ) {
			warn "$aff\n";
			push @menu, $aff unless $seen{$aff}++;
		}
		@affs = $self->menu(
			choicelist => \@menu,
			vertical   => 1,
			default => 0,
		);

		if ($affs[0]=~/Current:/ && ! $affs[1]){
			foreach (split /\n/, $guess) {
				chomp;
				$list->addAff($_);
			}
			return (1);
		}
		foreach (@affs) {
			if (m/Current:/){
				foreach (split /\n/, $guess) {
					chomp;
					$list->addAff($_);
				}
				next;
			}
			if ( !m/^Not on List$/ ) {
				$list->addAff($_);
				next;
			}
			else {
				my $new=0;
				while (!$new){
					$self->print( $self->astrlist->toSPIRES );
					$self->print('AFF=???;');
					$new = $self->newAff;
					if ($new) {
						$list->addAff($new);
					}
					else{
						last if $self->question(
							prompt  => "\nGive up on this Aff?",
							default => 'N',
						);

					}
				}
			}
		}

		return(0);
	}

	sub checkIn{

	my $self=shift;
	my %args=@_;
	my $rec=$args{'rec'};
	my $fa=$args{'fa'};
	my $noBull=$args{'eprint'};
	my $spi=$self->spi;
	$spi->ask('sel hep');
	my $title=$rec->title;
	$title=~s/\w+\-\w+//g;
	$title=~ s/\w*[^\w\s]+\w*//g;
	 $title=~s/^/\"/;
	 $title=~s/$/\"/;


	my $irn=$rec->irn;
	my $date=$rec->date;
	$date=m/(\d{4})/;my $year=$1;
	my $search="find fa $fa and t $title";
	my $notSelf=" and not irn $irn";
#	warn "Checking dupes:\n$search\n";
	if (($num=$spi->number($search.$notSelf))==0){
		return(0);
	}
	$noBull=$noBull?'also bb occ =0':'show result';
	if (($num=$spi->number($noBull))==0){
		return(0);
	}


	while ($num>10){
		$self->print("$num duplicates found using search:\n\n   $search\n\n");
		$search=$self->checkedit(name=>'find ',prompt=>'Enter a better search <cr> to quit inputting this paper');
		$self->die("You've chosen to leave, since too many duplicates were found") unless $search;
		$search="find $search";
		$spi->number($search.$notSelf);
		$num=$spi->number($noBull);
	}
	@titles=$spi->list('title');
	@irns=$spi->list('irn');
	@fas=$spi->list('fa');

	for(my $i=0;$i<$num;$i++){
		$extra{$irns[$i]}="First Author: $fas[$i]\nTitle: $titles[$i]";
	}
	unshift @irns, "No Duplicate";
	$self->print("Choose a duplicate?");
	my $choice=$self->menu(
			choicelist=>\@irns,
			vertical=>1,
			extra=>\%extra,
		);
	if ($choice > 1)
	{
		$choice=~s/^(\d+)\s.*$/$1/m;
		return($choice);
	}
	return(0)

	}



	sub checkAffList {
	my $newaff = '';
	my $idx    = 0;
	my $self=shift;
	my $simaffs=shift;

	foreach $aff ( $self->astrlist->allAffs ) {
		if ( !$self->checkAff($aff) ) {
			my @new = ();
			$idx = $self->astrlist->findAstr( aff => $aff );
			$self->print(
				"\nWrong aff:\n$aff\n\nWhat should it be?<cr> will delete\n");
			while ( !@new ) {
				while ( $newaff = $self->newAff() ) {
					push @new, $newaff;
					$self->print("For \n$aff\n\nYou have:\n");
					map { $self->print("$_\n") } @new;
					$self->print("\n\n Add another or <cr> to go on\n");
				}
				if (
						!@new && $self->question(
								prompt  => "Delete this aff without replacing?",
								default => 'N'
						)
					){
						last;
					}
			}


			if ($self->astrlist->repAff(old=>$aff,new=>\@new)){
				map {print "  $_ ... Changed\n"} @new;
			}
			else{
				$self->print("Affiliation Change Failed-check by hand when done\n\n");
			}
		}
		else {
			print "  $aff ... Correct\n";
		}
	}
	map {$self->print("$_\n")} $self->astrlist->allAffs;
	$self->print("To start from scratch, say \"N\", go to edit, then delete affs and come back here");
	if($self->question(
		prompt=> "Append more affils to above list?",
		default => 'N',

	)){

		@append=();
		while ( $newaff = $self->newAff() ) {
					push @append, $newaff;
					$self->print("For \n$aff\n\nYou have:\n");
					map { $self->print("$_\n") } @append;
					$self->print("\n\n Add another or <cr> to go on\n");
				}

		#
		#Determine where these appended astrs go.  astr(1) if only one astr, otherwise create a new one at the end
		#
		my $numAstrs= scalar(@{$self->astrlist->astrs});
		print "I have " .$numAstrs. " astrs\n";
		if ($numAstrs>1){
			print "ready to add";
			map {print} @append;
			$self->astrlist->addAstr('auth'=>[],'aff'=>\@append);
			$self->astrlist->dump;
		}
		else{
			foreach $aff (@append){
				$self->astrlist->addAff($aff,0);
			}
		}
	}
	push @new, @append;
    return (\@new);
}



sub editAstr {
    my $user=shift;
	my $spi    = $user->spi;
	my $key  = shift;
	my $db=shift||"Process.authors";

	my $bat =
	  "addupd;\n" . $key . ";\n" . $user->astrlist->toSPIRES . "\n;\n";

	$bat = $user->edittext($bat) || $bat;
	while (1) {
	my $choice = $user->menu(
			vertical   => 1,
			choicelist => [
				'Save These','Edit Again','Run a regexp search/replace','Give up on these'],prompt=>'What would you like to do?');
 	if ($choice=~/edit again/i){
    	$bat=$user->edittext($bat)||$bat;
 	}
	elsif($choice=~/regexp/i){
    	$bat=$user->regexp($bat)||$bat;
	}
    elsif($choice=~/save these/i){
    	if($spi->batch($bat,$db)){
        	$user->print("Merged to $db\n");
 			$success=1;
   			last;
    	}
   		else{
   			$user->print("Error merging");
   		}
    }
    elsif($choice=~/give up/i){
    	$success=0;
    	last;
    }
  }
    return ($success);
}


sub checkNames {
	my $self     = shift;
	my $spi      = $self->spi;
	my $simauths = shift;
    my $hepcut   = shift||5;
    my $changes=0;
	$spi->ask('sel hep');
    foreach $author ($self->astrlist->allAuths){
   		if ($simauths->{$author}){
	   		print "$author ... Matches Similar \n";
   		}
   		elsif ($hepcut && $spi->number("find ea $author and not note temporary")>$hepcut){
   			print "$author ... In HEP\n";
   		}
   		else {
   			my $newauthor=$self->checkAuth($author);
   			last if ($newauthor==-1);
   			if ($newauthor ne $author){
   				 $self->astrlist->repAuth(old=>$author,new=>[$newauthor]);
   				 $changes++;
   			}

   		}

    }
    return ($changes);
}


sub saveAstr {
	my $user  = shift;

	my $key = shift;
    my $db=shift||"process.authors";
	$bat =
	  "addupd;\n". $key . ";\n" . $user->astrlist->toSPIRES . "\n;\n";
	print $bat;
	if (
		$user->spi->batch(
			$bat, $db)){
        	$user->print("Merged to $db\n");
        	return(1);
   		}
   		else{
	   		$user->error("Cannot merge to $db\n");
	   		return(0);
   		}

}


	1;
