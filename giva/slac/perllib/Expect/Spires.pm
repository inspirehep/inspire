package Expect::Spires;

use Expect;
use Carp;

use vars qw(@ISA);

@ISA = qw(Expect);
$Expect::Log_Stdout = 0;

my %_attr_data=(
		timeout=>'180',
		program=>'/u3/spisys/spires',
		params=>'',
		debug=>'0',
		toflag=>'0',
		);
=head1 NAME

    Expect::Spires.pm - perl interface for UNIX-SPIRES
=head1 SYNOPSIS

A perl module that provides several functions for interacting with SPIRES through perl, and through there, the rest of the UNIX world.

OO interface using Expect.pm

=head1 DESCRIPTION

This class inherits from Expect.pm, so you can also use the object as a
    regular Expect.pm object (see CPAN, or local man pages for further info.)

=head2 Methods

=over

=item new()

Takes a hash argument

 my $spires=Expect::Spires->new(
  timeout=>300,
  program=>'/u3/spisys/spires',
  debug=>'0',
 );

=over

=item timeout

Timeout in seconds for the SPIRES process.  If this timeout is exceeded,
your spires session will be lost.  The default is 300 seconds, which
should be more than enough.

=item program

Program to talk to defaults to '/u3/spisys/spires'

=item debug

debug settings defaults to 0

=item TOflag

true if last "ask" was a timeout,reset to flase on each ask.

=back

Note that height will be set to 0 and set nostop is issued.  Other than
that, all setup is your responsibility via ask

=cut

    my $PROMPT=qr/\r(\-|\+)\>\s*\r?$/;


sub DESTROY{
    return(SUPER::DESTROY);
}

sub AUTOLOAD {
    my $self = shift;
    my $attr = our $AUTOLOAD;
    $attr =~ s/.*:://;
    if (defined($_attr_data{lc $attr})) {


	$attr=lc $attr;
	${*$self}{$attr} = shift if @_;
	${*$self}{$attr} = $_attr_data{$attr} unless defined(${*$self}{$attr});
        return ${*$self}{$attr};
    } else {
        my $superior = "SUPER::$attr";
        $self->$superior(@_);
    }
}


sub new {
    my $classname  = shift;         # What class are we constructing?
    my %args=@_;
    my %init_args=();
    $init_args{'program'}=delete $args{'program'};
    $init_args{'timeout'}=delete $args{'timeout'};
    $init_args{'debug'}=delete $args{'debug'};
    $init_args{'database'}=delete $args{'database'};
    my $self       = $classname->SUPER::new(%args);
    $self->_init(%init_args);
    return $self;                   # And give it back
}

sub _init {
    my $self = shift;
    my %args=@_;
    my $database=delete $args{'database'};
    foreach (keys %args){
	$self->$_($args{$_});
    }
    my @SERVER_STARTUP = ("set height 0\n","set nostop\n");

    $self->debug($self->debug());
    $self->raw_pty(1);
    $self->exp_internal($self->debug() -1 >0 ? 1 : 0);
    $self->spawn($self->program,$self->params);

    $self->expect($self->timeout,
		  [ timeout  => sub {
		      croak "Timeout in spires startup\n";
		  }],
		  [$PROMPT => sub{
			my $self=shift;
			$self->clear_accum();
			$self->print(@SERVER_STARTUP);
		    }],
		  );
    $self->expect($self->timeout(),[$PROMPT]);
    $self->db($database) if $database;
    return( $self );

}



=pod



=item ask

 $spires->ask(@commands)

Takes 1 argument a list of commands to be sent on separate lines

This function returns an array of the results from each command.
$results[0] is the full output (with newlines, etc) from spires from the
first command, and so on for any further commands.  The command itself is
not returned (?), based ont he policy that you should know because you
    asked! Commands need not be terminated by a newline.

In scalar context returns the results of the *first* command

=cut


sub ask{
    my $self=shift;
    my $ERROR=qr/Continue XEQ\?/;
    my @results=();
    my $timeout=0;
    $self->TOflag(0);
    my @commands=@_;
    map {s/([^\n])$/$1\n/} @commands;
    $self->print(shift @commands);
    $self->expect($self->timeout,
		  [ timeout  => sub {
		      carp "Timeout in spires expect\n";
		      $self->TOflag(1);
		      return();
		  }],
		  [$PROMPT=> sub{
		      my $self=shift;
		      my $answer=$self->before();
		      $answer=~s/.*\n//;  #throw away first line-last comand
		      $answer=~s/\p{IsCntrl}/\n/g;
		      push @results, $answer;
		      $self->clear_accum();
		      return unless @commands;
		      $self->print(shift @commands);
		      exp_continue_timeout;
		  }],
		  #errors and unexpected (ha) prompts
		  [$ERROR=>sub{
		      $self->print("y");
		      exp_continue_timeout;
		  }],
		  );


    return wantarray ? @results : $results[0];

}

=pod

=item number

 $spires->number(@commands)

performs ask(@commands)
finds the first line in the output containing "result" and returns the
    number on that line. Returns 0 if "Zero result" is found.  Returns
    null if no matching line is found.  Also works with Stacking commands

Should accurately return the number of results found by the first search
    in @commands


=cut

sub number{
    $self=shift;
    @args=@_;
    if (! @args){push @args,'sho result';}
    @results=$self->ask(@args);
    foreach (@results){
		next unless ((m/result/i) || (m/stack/i));
		return(0) if m/-Zero/;
		if (m/-Result\:\s*(\d+)/) {return($1)};
		if (m/-Stack\:\s*(\d+)/) {return($1)};
    }
    return();
}



=pod

=item element

 $spires->element(@elementname)

performs  ask("typ elemname") and extracts the values from the resulting output

if called in array context returns array of arrays where the outer array
    is looping over the records, and the inner is looping over multiple
    occs  (tested)  both arrays start at 0.

if called in scalar context returns the first occ of the first record
(that has a non-null value for  element) (tested)

(currently can't do multiple elems, but should soon make a new method for that...)

Values returned are not terminated by semicolon, and are not preceded by elem names

Returns null if there is no element, or if there is no result

=cut
sub test{
return 1;
}
sub element{
	use Data::Dumper;
    $self=shift;
    $elem=shift;
    my @return=();
    return('') unless $self->number("sho result")|| $self->number("sho stack");
    my @results=split /\n *\n/, $self->ask("typ $elem");
    my $rescnt=-2;  #first 2 lines blank...
    foreach (@results){
    	 s/\n/ /g;
    	 while(1){last unless s/(= \".*[^\\]);(.*\"\;)/$1\\\;$2/g}
	    $rescnt++;
	    s/([^\\])\;/$1 \;/g;
	    my @occs= split / \;/, $_;
		foreach (@occs){
		#print "\nresult=$rescnt occ:$_ \n\n";
		my $val='';
		if ( m/^[^=]+ = (.*)/){
		  $val=$1;
		}
		elsif (m/^\S\;/){
		  $val='';
		  }
		  else{next;}

		$val=~s{\\\;}{\;}g;
		if (wantarray){
		#	print "$rescnt->$val\n";
	    	push @{$return[$rescnt]},$val;
		}
		else {
	    	return($val);
		}
    }
    }
    return(@return);
}

=pod

=item asHash

  $spires->asHash(key=><key>,db=>db)

outputs a single record as a hash of arrays of elements, structures are arrays of hashes of arrays
key and db are optional, otherwise outputs the first record of current result.
Ill clear any format set and not reset them!


=cut

sub asHash{
	my $self=shift;
	my %args=@_;
	if ($args{db}) { $self->ask('sel '.$args{db})}
	if ($args{key}) { $self->ask('sta '.$args{key},'gen res')}
	if (! $self->number) {carp('No result for asHash');return(0);}

	$record=($self->ask('clr for','for res','dis','endf'))[2];
	@lines=split /\;\n/, $record;
	#print Dumper @lines;
	%record=();
	$oldlevel=1;
	unshift @hashes, \%record;
	@names=();
	unshift @names, 'record';
	foreach (@lines){
		s/^\s*\n(\s+)/$1/;
		if (/(\s+)(\S+) = (.*)$/s){
			$indent=$1;$name=$2;$value=$3;$noval=0;
		}
		elsif (/(\s+)([^=]+)$/s){
			$indent=$1;$name=$2;$value='';$noval=1;
		}
		else{
			carp("asHash failed to parse record at line $_");
			return(0);
		}
		$level=length($indent);
		$curhash=$hashes[0];
		if ($level>$oldlevel){  #new structure
			pop @{$curhash->{$lastname}};  # we know we must have put one here for the first unindented line of the struct-so get rid of it
		    if ($lastnoval){   #the last thing we found had no value, don't add it here it is a str name
		    	unshift @hashes,{$name=>[$value]};
		    }
		    else{          #the last thing we found had a value, add it here it is a str key
		    	unshift @hashes,{$lastname=>[$lastval],$name=>[$value]};
		    }
			unshift @names, $lastname;
			$oldlevel=$level;
			#carp("down one level ($level) $name=$value");
		}
		elsif ($level<$oldlevel){ #structure end

			# take care to the str we just findished
			$strhash=shift @hashes;
			$strname=shift @names;
			$curhash=$hashes[0];  # move back up one level
			$curval=$curhash->{$strname};
			$i=0;
			foreach (@$curval){	# in case we had earlier keyed structures with no other elems
				if (ref($_) ne 'HASH'){
				$curhash->{$strname}->[$i]={$strname=>[$curhash->{$strname}->[$i]]};
			}
			$i++;
		}
			push @{$curhash->{$strname}}, $strhash;
			$oldlevel=$level;
			#carp("back up one level ($level) $name=$value");
			# start the new str or value
			if (exists($curhash->{$name})){
				push @{$curhash->{$name}}, $value;
			}
			else {
				$curhash->{$name}=[$value];
			}
		}
		else{

			if ( exists($curhash->{$name})){
				push @{$curhash->{$name}}, $value;
			}
			else {
				$curhash->{$name}=[$value];
			}

		}
		$lastname=$name;
		$lastval=$value;
		$lastnoval=$noval;

	}
	#print Dumper(%record);
	return(\%record) unless wantarray;
	return(%record);


}

=pod

=item list

 $spires->list(elementname)

performs  ask("typ elemname") and extracts the values from the resulting output

in array context returns array of all values of the element, 1 entry per element value _no_ separation for diff records

in scalar context returns first occuring element

Note that this method is well suited for singly occuring elements since there will be one entry per record

(currently can't do multiple elems, but should soon make a new method for that...)

Values returned are not terminated by semicolon, and are not preceded by elem names

Returns null if there is no element, or if there is no result

=cut

sub list{
	use Data::Dumper;
    $self=shift;
    $elem=shift;
    my @return=();
    return('') unless $self->number("sho result") || $self->number("sho stack");
    my @results=split /\n *\n/, $self->ask("typ $elem");
    my $rescnt=-2;  #first 2 lines blank...
    foreach (@results){
    	 s/\n/ /g;
    	 while(1){last unless s/(= \".*[^\\]);(.*\"\;)/$1\\\;$2/g}
	    $rescnt++;
	    s/([^\\])\;/$1 \;/g;
	    my @occs= split / \;/, $_;
		foreach (@occs){
		#print "\nresult=$rescnt occ:$_ \n\n";
		my $val='';
		if ( m/^[^=]+ = (.*)/){
		  $val=$1;
		}
		elsif (m/^\S\;/){
		  $val='';
		  }
		  else{next;}

		$val=~s{\\\;}{\;}g;
		if (wantarray){
	    	push @return,$val;
		}
		else {
	    	return($val);
		}
    }
    }
    return(@return);
}


=pod

=item merge

$spi->merge($string,<$key>)

Merges the given string into all records in the current result, unless $key is supplied
in which case it merges into only $key.  Returns 0 if key is not found, or if no current
result.

Uses a temporary text file, so no spires size limits apply.

Uses currently selsected db

Returns the number of successful merges.   It compares this with the requested merges and carps
if there is a difference, but still returns number of succ.

=cut

sub merge {
	my $self=shift;
	my $string=shift;
	my $key=shift;
	return(0) unless (($req=$self->number("sho result")) || $key);
	if ($key){
		$self->ask("clr sta");
		unless ($self->number("sta $key")==1) {carp "Couldn't find $key\n"; return(0);}
        @commands=("for sta", "merge all","endf");
        $req=1;
	}
	else{@commands=("for res", "mer all","endf")}
	my $tmpfile="/tmp/tmpspimerge.$$.tmp";
	if (open(TMP,">$tmpfile")){
		print TMP "$string\n";
		   close TMP;
		   $self->ask("use $tmpfile");
		$output=($self->ask(@commands))[1];
        unlink $tmpfile;
        if ($output=~m/MER\s+(\d+)\s+(\d+)/){
        	 my $spireq=$1;
        	 my $suc=$2;
        	 if ($spireq!=$req){carp "Requested $req merges, Spires saw $spireq\n";}
        	 if ($suc!=$req){carp "Requested $req merges, Spires did $suc\n-SPIRES said\n$output\n";}
        	 return($suc);
        }
    	else
    	{carp "Merges probably failed-SPIRES said\n$output\n";
        return(0);}
	}
	else {
		carp "Error opening $tmpfile:$!\n";
        return(0);
	}


}

=pod

=item db

 $spi->db("hep")

performd $spi->ask("sel hep")

=cut

sub db{
	my $self=shift;
	my $db=shift;
	return($self->ask("sel $db"));
}

=pod

=item batch

$spi->batch($string,<db>)

batches the given string after selecting db (otherwise uses current)

Uses a temporary text file, so no spires size limits apply.

Returns the number of successful merges+adds.   It compares this with the requested merges/adds and carps
if there is a difference, but still returns number of succ.

=cut

sub batch {
	my $self=shift;
	my $string=shift;
	my $db=shift||'';
	my $num=grep /^\s*merg?e? |^\s*add|^\s*addupda?t?e? |^\s*upda?t?e?|^\s*remo?v?e?/i, split /\n/, $string;
	my $tmpfile="/tmp/tmpspimerge.$$.tmp";
	if (open(TMP,">$tmpfile")){
		print TMP "$string\n";
		   close TMP;
		 if ($db){$self->ask("clr sel","sel $db");}
		   $self->ask("use $tmpfile");
		$output=($self->ask('inp bat'))[0];
		warn "Output from batch:\n".$output."\n" if $self->debug;
        unlink $tmpfile;
        my $tmp=$output;
        my $spireq=0;
        my $suc=0;
        while ($tmp=~s/(MER\s+|ADD\s+|UPD\s+|REM\s+)(\d+)\s+(\d+)//){
        	  $spireq+=$2;
        	  $suc+=$3;
		}

        if (($suc==$spireq)&&($suc==0))
    	{carp "Merges probably failed-SPIRES said\n$output\n";
        return(0);}
			if ($output=~m/Err/){carp "Probable errors:\n$output\n";}
        	 if ($spireq!=$num){carp "Requested $num merges/adds/upds, Spires saw $spireq\n";}
        	 if ($suc!=$num){carp "Requested $num merges/adds/upds, Spires did $suc\n";}
        	 return($suc);

}
	else {
		carp "Error opening $tmpfile:$!\n";
        return(0);
	}


}




=pod

=item close

 $spires->close()

attempts to exit and do an expect soft close;

=cut

sub close{
    $self=shift;
    $self->print("exit\n");
    $self->do_soft_close();
}



=pod

=back

=head1 AUTHOR

Travis C. Brooks  travis@SLAC.stanford.edu


=head1 BUGS

Plenty-most are unknown

The object echoes to stdout everything -annoying but not a big problem

Claims DESTROY gives a problem.

array of results is not what one would expect....includes lots of
    pieces. and the desired result is only one part.


serious problem-- string '->' within a title causes propt to fire!!  added
    "\r" to prompt should help but not totally prevent this...

=head1 COPYRIGHT

2006, Travis Brooks, Stanford Linear Accelerator Center

=cut




