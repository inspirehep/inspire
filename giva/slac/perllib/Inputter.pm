
package Inputter;

$ENV{'PERL_READLINE_NOWARN'}=1;
use Term::ReadLine;


sub new {
	my $class  = shift;    # What class are we constructing?
	my %args       = @_;

	my $self = bless( {}, ref($class) || $class );
	for (keys %args){
		$self->{$_}=$args{$_};   # just initialize everything for now  'spi' is only known
	}
	$self->{term}=new Term::ReadLine 'Simple Perl';
	$self->{output}=$self->term->OUT || \*STDOUT;
	return ($self);

}



	sub spi {
		my $self = shift;
		return ( $self->{spi} );
	}

=pod

menu takes a paramhash

=over

=item choicelist=> req'd list of choices to be displayed-in order

=item options=> list of abbreviations for choices to type/disply (defaults to numbers)

=item done=> option for done  (when this is entered, method returns false) defaults to none (a choice must be entered)

=item vertical=> if true prints one item per line, otherwise all on one line(default)

=item default=> The default choice (specified as the element of choicelist to return by default ie 0 or 4 etc )defaults to none)

menu will allow multiple selections (comma separated) if it is called in array context,
and returns the choice items (not the options) in the order selected.
If called in scalar context it will only allow one selection, and return that one.

=back

=cut

sub menu {
	my $self    = shift;
	my %args    = @_;
	my $multi   = wantarray ? 1 : 0;
	my %choices = ();
	my @options = ();
	my $default='';
	if (defined $args{'default'}){
	   $default = ${$args{'choicelist'}}[$args{'default'}] || '';
	}
	else{
		undef($default);
	}
	my %extra   = %{$args{'extra'}};
	my $i;
	my $done    = $args{"done"};
	foreach $choice ( @{ $args{'choicelist'} } ) {
		my $opt = @{ $args{'options'} }->[$i] || ( $i + 1 );
		$opt = '<cr>' if $opt eq "\n";
		if (defined($default) && $args{'vertical'} ){
			if ( $choice eq $default){$dispopt{$opt} = '<cr> '.$opt}
			else{ $dispopt{$opt} = '     '.$opt}
		}
		elsif (defined($default) &&  $choice eq $default){$dispopt{$opt} = $opt.'(<cr>)'}
		else {$dispopt{$opt} = $opt}
		push @options, $opt;
		$choices{ $options[$i] } = $choice;
		$i++;
	}
	my $sep = $args{'vertical'} ? "\n" : ',';
	if ($args{'prompt'}){
		$self->print($args{'prompt'});
	}
	while (1) {
		foreach $option (@options) {
			my $disp=$choices{$option}.$sep;
			$disp.=' '.$extra{$choices{$option}}.$sep if $extra{$choices{$option}};


			print "$dispopt{$option}) $disp";
		}
		$done='<cr>' if $done eq "\n";
		print "($done=done) $sep" if $done;
		$prompt= $multi
		  ? 'Choices (' . $options[0] . ',' . $options[1] . "):"
		  : "Choice:";
		$input = $self->term->readline($prompt);
		 $self->term->addhistory($input);
		 $input='<cr>' if $input eq '';
		if ( $done && ( uc($input) eq uc($done) ) ) { return (0); }
		if (defined($default) && $input eq '<cr>' ){return($default);}
		if ($multi) {
			my @return = ();
			@input = split /,/, $input;
			my $num=@input;
			foreach $input (@input) {
				foreach $option (@options) {
					if ( lc($option) eq lc($input) ) {
						push @return, $choices{$option};
					}
				}
			}
			unless (@return==$num){
				$self->print("Unrecognized input");
				@return=$self->menu(%args);
			}
			return (@return);
		}
		else {    # scalar
			my $return='';
			foreach $option (@options) {
				if ( lc($option) eq lc($input) ) {
					$return = $choices{$option};
					last;
				}
			}
			if ($return eq ''){
				$self->print("Unrecognized input");
				$return=$self->menu(%args);
			}
			return ($return);
		}
	}
}

=pod

question  -takes paramhash ans asks a yes no question returns 1 or 0

=over

=item prompt  The question to be asked

=item default the default answer (defaults to null)

=back

=cut

	sub question {
		my $self = shift;
		my %args = @_;
		while (1) {
			$prompt= $args{'prompt'}.' ';
			if ( uc( $args{'default'} ) eq 'Y' ) {
				$prompt.= "Y(=<cr>)/N:";
			}
			elsif ( uc( $args{'default'} ) eq 'N' ) {
				$prompt.= "Y/N(=<cr>):";
			}
			else {
				$prompt.= "Y/N:";
			}
			$input = $self->term->readline($prompt);
			if ( $input !~ /\S/ ) { $input = $args{'default'}; }
			$input =~ s/\s+//;
		    $self->term->addhistory($input);
			return (1) if $input =~ m/^y/i;
			return (0) if $input =~ m/^n/i;
		}
	}

=pod

checkedit  -takes paramhash asks user to check a value and edit if incorrect  returns value

returns value

=over

=item value the value to be checked, can be null

=item name the name of the value, for user info

=item prompt appears above value (defaults to "Please edit $name \n")

=item del  an input value to cause the value to be deleted defaults to "-"  This value
is still returned, no special action is taken, it is just included in prompt.
Only used if a value is also passed.  This may stil work, but since we use readline now, it is easier to just delete the value

=item db alternatively pass a SPIRES::Expect object with a single result as db and and element name as...

=item element- the name of the element you want to change in the record in db  note that element and db must be used together and cannot be used with value

=back

=cut

	sub checkedit {
		my $self = shift;
		my %args = @_;

		#
		# Handle live databse updates
		if (my $db=$args{'db'}){
			$self->error("System Error:checkedit incorrectly called with db but no element") unless $elem=$args{'element'};
			return(0) unless $elem;
			$self->error("System Error:Cannot handle multiple results") unless ($db->number()==1);
			@vals=$db->list($elem);
			delete($args{'db'});
			delete($args{'element'});
			$occ=0;

			#
			#  handle multiple occurences

			foreach $val(@vals){
				$occ++;
				$args{'value'}=$val;
				$args{'prompt'}="Please edit $elem($occ):";

				$val=$self->checkedit(%args);
				my $merge="$elem($occ)=$val;";
				if (! $val){
					$merge="$elem(-$occ);";
					$occ=$occ-1;

				}  #delete this value, and decrement so that the next one goes in the right place
				if (!( $db->merge($merge))){
					$self->error(
							"There appears to be a problem merging to SPIRES\nYour changes may not be saved\nContinue, but be cautious, and check the record"
	  							);
						return(0);
				}

			}
			#
			# Allow user to add more
			$args{'value'}='';
			$occ++;
			$args{'prompt'}="Please add $elem <cr>:No More $elem";
			while($val=$self->checkedit(%args)){

				if (!( $db->merge("$elem($occ)=$val;"))){
						$self->error(
							"There appears to be a problem merging to SPIRES\nYour changes may not be saved\nContinue, but be cautious, and check the record"
	  							);
						return(0);
				}
				$occ++;

			}
			return($occ);
		}
		my $name = $args{'name'} || "value";
		my $del  = $args{'del'}||'-';
		my $del  = '' unless $args{value};
		my $prompt=$args{'prompt'}
		  ? $args{'prompt'}." "
		  : "Please edit $name: ";
		my $preput =$args{'value'}||'';

		$return = $self->term->readline($prompt,$preput)||$del;
		#$return =~ s/(\S+)\n/$1/;   #strips nelwine unless that is all there is
		#if ( $return !~ /\S/ ) { $return = $args{'value'}; }
		return ($return);
	}
=pod

regexp(text)

prompts for a (perl syntax) substitution regexp and runs it on the provided text  returns result
=over

=item text the value to be checked


=back

=cut


	sub regexp{
			my $self=shift;
			my $text=shift;
			return(0) unless $text;
				$re=$self->checkedit(value=>'',prompt=>'perl style regexp (w/ captures and metachars)');
		return(0) unless $re;

		$re.='g';
		$newtext=$text;
		$sub='$newtext=~'.$re;
		eval $sub;
		if ($@){
			warn("Bad regexp given:$re");
			return(0);
		}
		$self->edittext($newtext);
		if ($self->question(prompt=>"Keep this change?",default=>'Y')){
		return($newtext);
		}
		else{return($text);}
	}
=pod

edittext(text,<editor command>)

invokes the editor command or default $EDITOR, or the $EDITOR Environment var, or pico

to edit the text specified.  return 0 if failure, returns edited text otherwise.


=over

=item text the value to be checked, can be null

=item editor command the name of the value, for user info

=back

=cut


	sub edittext{
			my $self=shift;
			my $text=shift;
		use File::Temp qw();
		my $tmp=new File::Temp();
		$tmp->print($text);
		$tmp->close;
		$file=$tmp->filename();
		$self->editfile($file);
		open(TMP,"<$file") || return(0);
		$text='';
		while (<TMP>){$text.=$_;}
		return($text);
	}

=pod

editfile(file,<editor command>)

invokes the editor command or default $EDITOR, or the $EDITOR Environment var, or pico

to edit the file specified.  return 0 if failure, returns edited text otherwise.


=over

=item file the file to be edited, can be null

=item editor command the name of the value, for user info

=back

=cut


	sub editfile{
		my $self=shift;
		my $file=shift;
		my $editor=shift||$EDITOR||$ENV{EDITOR}||"pico";
		system("$editor $file");
		return;
	}

=pod

findPaper(bull=><bull>,irn=><irn>,either=><id>)

finds a paper, or asks the user, returns irn, then lanl.

=over

=item bull bull for bull search

=item irn for irn search

=item either  (if you aren't sure what they wanted tois earch, tries both)


=back

=cut

sub findPaper{
	$self=shift;
	%args=@_;
	my $spi=$self->spi;
	$spi->ask('sel hep');
	if ($args{bull} && $spi->number("find bull $args{bull}")==1){}
    elsif($args{irn} && $spi->number("find irn $args{irn}")==1){}
    elsif(($search=$args{either}) || ($search=$self->checkedit(name=>"", prompt=>"eprint or IRN"))){
		if ($spi->number("find bull $search")==1){}
    	elsif ($spi->number("find irn $search")==1){}
    }
	$irn=$spi->list('irn');
	$lanl=$spi->list('lanl');
    if (!$irn) {$self->die("Can't find paper");}
    return($irn,$lanl);
}



	sub  term{
		return(@_[0]->{term});
	}

	sub print {
		$self=shift;
		$string=shift;
		print "$string\n";
	}

	sub error {
		my $self=shift;
		my $msg=shift;
		chomp $msg;
	    print "*** An error occurred ***\n";
		print "**  $msg  **\n";
	}

	sub die {
		my $self=shift;
		my @args=@_;
		$self->error(@args);
		die ("Inputter Module cannot continue, please start again\n");
	}

	1;
