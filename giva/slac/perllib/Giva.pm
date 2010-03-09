# Module that handles extracting authors or references from PS files.
# Contains:
#	Get_Authors
#	Get_Postscript
# 	Get_References


package Giva;


=pod

=head1 SYNOPSIS

Giva.pm - a wrapper for interacting with Giva routines that extract authors and references


=head1 Constructing


#  Create Giva object
#
my $giva = Giva->new(
	input=>$user,
	spi=>$spi,
	verbose=>$args{v},
	irn=>$irn,
	eprint=>$lanl,
	method=>$routine,
	ext=>'refs',
	flatfile=>$args{f},
	file=>'pdf'
	);


=over

=item input  (a user input object if running with a person watching)

=item spi ( a spiexpect object)

=item irn of record in question

=item eprint or do it by eprint nubmer

=item method  Name of a Giva::Extractor::<method> module that will actually do the extraction

=item ext "refs"" or "auths" or "authsbare"

=item flatfile name of flatfile to extract from, otherwise we will find it

=item string string to extract from (also need to set file to string)

=item file  type of file (pdf,tex,ps, String, paste)


=back

=head1 METHODS



=cut



use Giva::Extractor;

use Inputter::Authors;
use arxiv;

use Class::Struct;
use LWP::Simple;
use File::Temp qw();
use File::Copy;


struct Giva => {
		astrlist => 'Astrlist',
		spi      => 'Expect::Spires',
		input    => 'Inputter',
		tempfile  => '$',
		arxiv     => 'arxiv',
		irn      => '$',
		eprint   => '$',
		file     => '$',
		url      => '$',
		refs	 => '@',
		ext      => '$',
		success  => '$',
		method   => '$',
		extractor=> '$',
		verbose  => '$',
		flatfile => '$',
		string   => '$',
	};


my $PDFSCRIPT='/usr/local/bin/pdftotext';
my $PRESCRIPT = '/u/li/slaclib/prescript/prescript-2.1/prescript plain';
my $GIVADIR='/u3/spires/giva/';


=item download


Downloads the appropriate file acording to irn/eprint and file

=cut

sub download{
	my $self=shift;
	my $spi=$self->spi;


    my $tmpfile=$self->tempfile;
	warn "downloading to $tmpfile" if $self->verbose;

	if ($self->flatfile){
		copy($self->flatfile,$self->tempfile);
		return(1);
	}
	if ($self->string){
		return(1);
	}
    if ($self->irn && ! $self->eprint){

		$spi->ask('sel hep',"find irn ".$self->irn);
		my $eprint=$spi->list('lanl');

		my $url=$spi->list('url');
		if ($eprint){
			$self->eprint($eprint);
		}
		elsif ($url && ! $self->url){
			$self->url($url);
		}
	}
	if ($self->file eq 'paste'){
		warn "downloading via paste" if $self->verbose;
		$self->paste;
		return(1);
	}
	elsif ($self->eprint){
		my $fname='';

		if ($self->file eq 'tex'){
			warn "downloading ".$self->eprint." via eprint (tex)" if $self->verbose;
			$fname=$self->arxiv->getTeX(
				id=>$self->eprint,
				file=>$tmpfile,
				user=>$self->input
			);
		}
		else{
				warn "downloading ".$self->eprint." via eprint (pdf)" if $self->verbose;
		    $fname=$self->arxiv->getPDF($self->eprint,$tmpfile);
		}
		$self->tempfile($fname) || $self->input->error("Error Downloading File");

	}
	elsif ($self->url){
		$self->input->print("Warning trying to download ".$self->file." from:\n".$self->url) if $self->verbose;
		getstore($self->url,$tmpfile);
	}
	else { return(0);}
	my $download=$self->tempfile;
	if (-e $download){
	   return($download);
	}
	else{
		$self->input->error("Error Downloading File: $download does not exist");
		return(0);
	}
}

=item extractor_init

Creates and returns the extractor as specified by method

=cut

sub extractor_init{
	my $self=shift;
	my $class="Giva::Extractor::".$self->method;
	eval "require $class";
	my $obj=$class->new(
		file=>$self->tempfile,
		verbose=>$self->verbose,
		spi=>$self->spi,
		ext=>$self->ext,
	);
	return($self->extractor($obj));


}


=iten getText

extracts text from the file downloaded by download, usues extractor based on file type specified

puts resulting text in tempfile

=cut

sub getText{
	my $self=shift;
	if ($self->file eq 'paste'){
		return(1);
	}
	elsif ($self->file eq 'tex'){
		return(1);
	}
	elsif ($self->file eq 'pdf'){
		(my $txtname=$self->tempfile).='.txt';
		system "$PDFSCRIPT ".$self->tempfile." $txtname";
		rename $txtname, $self->tempfile;
	}
	elsif ($self->file eq 'ps'){
		(my $txtname=$self->tempfile).='.txt';
		system "$PRESCRIPT ".$self->tempfile." $txtname";
		rename $txtname, $self->tempfile;
	}
	elsif ($self->file eq 'string' || $self->string){
		my $txtname=$self->tempfile;
		open(TXT, ">$txtname");
		print TXT $self->string;
		close(TXT);
	}
}


sub arxiv{
	my $self=shift;
	if ($self->{arxiv}) {return($self->{arxiv})}
	return($self->{arxiv} = arxiv->new());
}


=item tempfile_init

simply creates tempfile using the File::Temp module to ensure uniqeness

=cut

sub tempfile_init{

my $self=shift;
my $tmp=new File::Temp(UNLINK=>0,DIR=>$GIVADIR);
my $tmpname=$tmp->filename;
$tmp->close;
$self->tempfile($tmpname);
return($tmpname);
}


=item  extract

Performs the actual extraction by download, getText, extractor_init, then rnning the extractor

returns an array of refs if that was desired, or an astrlist object or bare spires authlist as specified in ext

=cut

sub extract{
	my $self=shift;
	chdir($GIVADIR);
	$self->tempfile_init;

	$self->download;

	$self->getText;

	print "Obtained ".$self->tempfile." :\n"  if $self->verbose;
	$self->extractor_init;
	return(0) unless $self->extractor->extract(@_);
	if ($self->ext eq 'refs'){
		return($self->extractor->refs);
	}
	elsif ($self->ext eq 'auths'){
		return($self->extractor->Astrlist);
	}
	elsif ($self->ext eq 'authsbare'){
		return($self->extractor->Astrlist->toSPIRES);
	}

	return(0);
}


=item paste

Handles the creation of a file by pasting from a pdf or other sourece

=cut

sub paste{
	my $self=shift;
	my $eprint=$self->eprint;
	my $url=$self->url;

	my $txtfile=$self->tempfile;
	open(TXT,">$txtfile")|| carp("Paste cannot open $txtfile:$!")&&return(0);

	my $arx='http://arXiv.org/pdf/'.$eprint;

	if (!$eprint){
		$self->input->print("The paper is not an eprint, but it may be at:\n\n  $url\n\n");
	}
	else {
		$self->input->print(" This eprint is available at:\n\n  $arx\n\n");
	}

my $msg= "\n\nUse the browser's Text select tool to cut and paste authors or
    references into this screen\nSee Denise for tutorial\n\nPaste the refs/auths below.
      After refs or auths type ***END\n";
$self->input->print($msg);

alarm 600; # IF we get in trouble, we can leave after 10 mins
{  # scope for the paste
    local $SIG{ALRM}= sub { die "The Paste took too long\n"};
    local $SIG{INT}='IGNORE';
    local $SIG{QUIT}='IGNORE';
    local $SIG{HUP}='IGNORE';
    local $SIG{TERM}='IGNORE';
    $/="\n***END\n";
    $paste=<STDIN>;
    $/="\n";
    #Trick for getting rid of ctrl chars without getting rid of \n
    $paste=~s/\n/\*\*\*NEWLINE\*\*\*/g;
 #   $paste=~s/\p{IsC}/\?/g;   #use utf8
 #   $paste=~s/\x{00B8}/\n Iwas a circumflex \n/g;

    $paste=~s/[[:cntrl:]]/\?/g;  #if use POSIX
    $paste=~s/\*\*\*NEWLINE\*\*\*/\n/g;

}  #end of scope for the paste, hopefully we made it out alive!

alarm(0);

$self->input->print("\n\nYou entered\n\n$paste\n\n");

print TXT $paste;

close(TXT);
return(1);

}



sub DESTROY{
      my $self = shift;
      unlink $self->tempfile unless $self->verbose;
}

		1;
