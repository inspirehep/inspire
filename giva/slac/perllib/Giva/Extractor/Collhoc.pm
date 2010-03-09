package Giva::Extractor::Collhoc;

use vars qw(@ISA);
@ISA = qw(Giva::Extractor);

sub extract
{
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
  warn "Starting extraction\n";
  %affHash = "";
  $instFlag = 0;
  $foundauth = 0;
  $foundaff  = 0;
  my $clean = '';
  my $line  = '';
  warn "Extracting from tex file ". $self->file . "\n" if $self->verbose;
  if (!(open(TEX, $self->file)))
  {
    warn "Error opening ". $self->file . "\n";
    return(0);
  }
  while (<TEX>)
  {
    $clean .= &Brace($_);
  }
  close (TEX);
  foreach (split /\n/, $clean)
  {
    my $line = $_;
    $line = &LittleThings($line);
    $line = &NewCommand($line);
    $line = &Decode($line);
    $line = &AuthorForm($line);
    if ($line =~ /(\\author|\\affiliation)/)
    {
      $line2 .= $line;
    }
  }
  $line = &Cluster($line2);
  foreach (split /\n/, $line)
  {
    if ($_ =~ /AUTHOR \= (.*);/)
    {
      $auth      = $1;
      $foundauth = 1;
    }
    elsif ($_ =~ /AFFILIATION \= (.*);/)
    {
      $aff      = $1;
      $foundaff = 1;
    }
    else
    {
      $foundauth = 0;
      $foundaff  = 0;
    }
    if ($foundauth)
    {
      $self-> foundAuth($auth);
    }
    if ($foundaff)
    {
      $self-> foundAff($aff);
      $foundaff = 0;
    }
  }
  print "EXTRACTED = ".$self->extracted."\n" if $self->verbose;
  return ($self->extracted);
}



sub Cluster
{
  my $line = $_[0];
  $line =~ s/\$\^\{\l\,\}\$(\$\^\{\d+\,\d+\}\$)/$1/g;
  $line =~ s/\\author\{(.*)\$\^\{(\w+)\,(\w+)\}\$\}/\
ASTR\;
  AUTHOR = $1\;
  AFFILIATION = $affHash{$2}\;
  AFFILIATION = $affHash{$3}\;
/g;
  $line =~ s/\\author\{(.*)\$\^\{?(\w+)\}?\$\}/\
ASTR\;
  AUTHOR = $1\;
  AFFILIATION = $affHash{$2}\;
/g;
  #$line=~s/\s+/ /g;
  $line=~s/\\author\{([^\}]+)\}/  AUTHOR = $1;\n/g;
  $line=~s/\\affiliation\{([^\}]+)\}/  AFFILIATION = $1;\nASTR;\n/g;
  $line =~ s/^\s*//;
  return "$line";
}

sub AuthorForm
{
  my $line = $_[0];
  $line=~s/\\thanks\{[^\}]+\}//g;
  $line=~s/\\author\{([^\}]+)\\inst\{([^\}]+)\}/\\author\{$1\$\^\{$2\}\$\}/;
  if ($line =~ /\\institute/ && $instFlag == 0)
  {
    $instFlag = 1;
    $line =~ s/\\institute\{(.*)/\\affiliation\{\$\^$instFlag\}\$$1\}/;
    $instFlag++;
  }
  if ($instFlag and $line =~ /\\and/)
  {
    $line =~ s/\\and (.*)/\n\\affiliation\{\$\^$instFlag\}\$$1\}/g;
    $instFlag++;
  }
  $line =~ s/(.*)\\a?l?t?affilma?rk\{([^\}]+)\}/\\author\{$1\$^\{$2\}\$\}/g;
  $line =~ s/\\altaffiltext\{(\d+)\}\{(.*)\}/\\affiliation\{\$^\{$1\}\$$2\}/g;
  $line =~ s/\\affilmk\{(\d+)\}\{(.*)\}/\\affiliation\{\$^\{$1\}\$$2\}/g;
  $line =~ s/\\and (.*)\s*\\inst\{([^\}]+)\}/\\author\{$1\$^\{$2\}\$\}/g;
  $line =~ s/\$\^\{?(\w+)\,[a-z\\]+\}?\$/\$\^\{$1\}\$/g;
  $line =~ s/^([A-Z][\w\. \-]+)(\$\^\{.*\}\$)\,?/\\author\{$1$2\}/g;
  $line =~ s/^(\$\^\{.*\}\$)\s*(.*)/\n\\affiliation\{$1$2\}/g;
  $line =~ s/\\it\s*(\$\^\{.*\}\$)\s*(.*)/\n\\affiliation\{$1$2\}/g;
  $line=~s/\\author\[([^\]]+)\]\{([^\}]+)\}/\\author\{$2\$^\{$1\}\$\}/g;
  $line=~s/\\altaffiliation/\\affiliation/g;
  $line =~ s/[aA]lso (at|with) / /g;
  $line=~s/^\\address\[([^\]]+)\]\{([^\}]+)\}/\\affiliation\{\$^\{$1\}\$$2\}/g;
  if  ($line =~ /\\affiliation\{\$\^\{?(\w+)\}?\$\W*(.*)\}/ )
  {
    my $aff = $2;
    my $affkey = $1;
    $aff =~ s/\\\\//;
    $aff =~ s/\$\^\{?[a-z]\}?\$//g;
    $affHash{$affkey} = $aff;
    $line = "";
  }
  return $line;
}

sub Brace
{
  my $line = $_[0];
  chomp($line);
  $line = &Decode($line);
  $line =~ s/\s+/ /;
  $line =~ s/\s$//;
  $line =~ s/^\%.*//;
  $line =~ s/([^\\])\%.*/$1/;
  if ($line =~ /^\\author\{[^\}]+$/)
  {
    $line = "BEGIN_AUTHORS";
  }
  elsif ($line =~ /^\\author\{([^\}]+\{[^\}]+\})$/ )
  {
    $line = "$1";
  }
  $line =~ s/(\\altaffilmark\{[^\}]+\})\}/$1/;
  if ($line =~ /\{/)
  {
    my $line1 = $line;
    $line1 =~ s/[^\{]//g;
    my $nlbrace1 = length($line1);
    $nlbrace = $nlbrace1 + $nlbrace;
  }
  if ($line =~ /\}/)
  {
    my $line1 = $line;
    $line1 =~ s/[^\}]//g;
    my $nrbrace1 = length($line1);
    $nrbrace =  $nrbrace1 + $nrbrace;
  }
  if ($nlbrace > $nrbrace)
  {
    #$line = "nlbrace=$nlbrace  nrbrace=$nrbrace: $line ";
    $line = "$line ";
    $nlbrace = $nlbrace - $nrbrace;
  }
  elsif ($nrbrace == $nlbrace)
  {
    #$line = "nlbrace=$nlbrace  nrbrace=$nrbrace: $line\n";
    $line = "$line\n";
    $nlbrace = 0;
  }
  $nrbrace = 0;
  $line =~ s/[ ]+/ /g;
  $line =~ s/^[ ]+//;
  $line =~ s/\\and [\n]?/\n \\and /g;
  if ($line =~ /\S/)
  {
    return "$line";
  }
}

sub NewCommand
{
  my $info = $_[0];
  if ($info =~ /\\newcommand\*?\{\\(.*)\}\{(.*)\}/ ||
      $info =~ /\\def\\(.*)\{(\\.*)\}/  ||
      $info =~ /\\def\\(.*)\{(.*)\}/ ||
      $info =~ /\\address\[(\w+)\]\{(.*)\}/)
  {
    $hash{$1} = $2;
  }
  if ($info =~ /(.*\w+)\\address\[(\w+)\]\{(.*)\}/)
  {
    $info = "\\author\{$1\}\n\\affiliation\{$3\}\n";
  }
  elsif ($info =~ /(.*)\\addressmark\[(\w+)\](.*)\n/)
  {
    $info = "\\author\{$1\}\n\\affiliation\{$hash{$2}\}$3";
  }
  elsif ($info =~ /\\newcommand{\\(.*)}\[1\]\{(.*)\#1(.*)\}/)
  {
    #$hash{$1} = $2;
    $command1 = $1;
    $command1First = $2;
    $command1Second = $3;
  }
  elsif ($info =~ /\\newcommand{\\(.*)}\[2\]\{(.*)\#1(.*)\#2(.*)\}/)
  {#print "2 : $info\n";
    #$hash{$1} = $2;
    $command2 = $1;
    $command2First = $2;
    $command2Second = $3;
    $command2Third = $4;
  }
  elsif ($info =~ /\\newcommand\*?\\(.*)\{(.*)\}/ )
  {
    $hash{$1} = $2;
  }
  elsif ($info =~ /(.*)\\$command2\{([^\}]+)\}\{([^\}]+)\}(.*)/)
  {
$info="$1"."$command2First"."$2"."$command2Second"."$3"."$command2Third"."$4";
  }
  elsif ($info =~ /(.*)\\$command1\{([^\}]+)\}(.*)/)
  {
    $info = "$1"."$command1First"."$2"."$command1Second"."$3";
  }
  else
  {
    for my $key (keys %hash)
    {
      $info =~  s/\\$key(\W)/$hash{$key}$1/g;
    }
  }
  return "$info";
}

sub LittleThings
{
  my $line = $_[0];
  $line =~ s/\^(\d)/\^\{$1\}/g;
  $line =~ s/^\$[ ]+/\$/;
  $line =~ s/ \$[ ]+\^/ \$\^/g;
  $line =~ s/\{[ ]+/\{/g;
  $line =~ s/[ ]+\}/\}/g;
#  $line =~ s/^\%.*//;
#  $line =~ s/([^\\])\%.*/$1/;
  $line =~ s/\\affiliation\{/\n\\affiliation\{/g;
  $line =~ s/\\thanks\{[dD]eceased\}//g;
#  $line =~ s/\\address\[/\n\\address\[/g;
  return $line;
}

sub Decode
{
  my $line = $_[0];
  if ($line =~ /\\\\[ ]*$/)
  {
    $line =~ s/\\\\/ /g;
  }
  $line =~ s/\\&/ and /g;
  $line =~ s/--/-/g;
  $line =~ s/\{\\ss\}/ss/g;
  $line =~ s/\\ss/ss/g;
  $line =~ s/\\\,/ /;
  $line =~ s/^[ ]+//;
  $line =~ s/\{\\l\}\\\-/l/g;
  $line =~ s/\{?\\\'\{?\\i\}/i/g;
  $line =~ s/\\\~\{n\}/n/g;
  $line =~ s/\\[cuv]\{([A-z])\}/$1/g;
  $line =~ s/\$\\acute\{(\w)\}\$/$1/g;
  $line =~ s/\{\\[\'\"]([A-z])\}/$1/g;
  $line =~ s/\\\.(\w)/$1/g;
  $line =~ s/\\H{([a-z])}/$1/g;
  $line =~ s/\{\\AA}/A/g;
  $line =~ s/\\[\"\'\`\^\.]\{([A-z])\}/$1/g;
  $line =~ s/\\[\"\'\`\^]([A-z])/$1/g;
  $line =~ s/\\~([A-z])/$1/g;
  $line =~ s/\{[ ]+/\{/g;
  $line =~ s/\{\\l\}/l/g;
  $line =~ s/\\i /i/g;
  $line =~ s/\\l /l/g;
  $line =~ s/\{\\L\}/L/g;
  $line =~ s/\\L /L/g;
  $line =~ s/\\Lodz/Lodz/g;
  $line =~ s/\s*\~/ /g;
  $line =~ s/\\v //g;
  $line =~ s/o\\v/ov/g;
  $line =~ s/\\c c/c/g;
  $line =~ s/\\textsc\{([^\}]+)\}/$1/g;
  return "$line";
}



1;

