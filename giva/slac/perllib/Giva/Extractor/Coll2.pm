
package Giva::Extractor::Coll2;

use Giva::Extractor;
use vars qw(@ISA);
@ISA = qw(Giva::Extractor);






sub foundAuth
{
 my $self=shift;
 my $auth=shift;
 print "Coll2 found Auth $auth" if $self->verbose;
  $auth =~ s/\,\s*$//;
  $auth =~ s/\.(\S)/\. $1/g;
  $auth =~ s/^\s+//;
  $auth =~ s/\s+$//;
  my $q = "\\'";
  my $char = "A-z\\-";
  $char = $q.$char;
  my $chars = "A-z\\.\\-\\s";
  $chars = $q.$chars;
  $auth =~ s/\;//;
  $auth =~ s/\$[^\$]*\$//;
  $auth =~ s/([A-Z]) /$1\. /g;
  my @spanish = qw(Avila Castro Cuenca Delli Diaz Fonseca Grosse
                   Jesus Mortari Munoz Pereira Tico);
  #print "author1 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([zZ]ur [$chars]*)$/$2, $1/;
  #print "author1a = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([vV][ao]n der? [$chars]*)$/$2, $1/;
  #print "author8 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([vV][ao]n [$chars]*)$/$2, $1/;
  #print "author9 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([A-Z][a-z]+ y [$chars]*)$/$2, $1/;
  $auth =~ s/([A-Z][$chars]+) ([A-Z][a-z]+ [DdLl][aei][l]? [$chars]*)$/$2, $1/;
  #print "author2 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([Dd][ei] [Ll][a]* [$chars]*)$/$2, $1/;
  #print "author3 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([DdLl][aei][la]* [$chars]*)$/$2, $1/;
  #print "author4 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([Ll][eo] [$chars]*)$/$2, $1/;
  #print "author5 = $auth *\n";
  $auth =~ s/([A-Z][$chars]+) ([eE][l] [$chars]*)$/$2, $1/;
  #print "author6 = $auth *\n";
  foreach $spanish (@spanish)
  {
    $auth =~ s/([A-Z][$chars]+) ($spanish) ([A-Z][a-z][$chars]*)$/$2 $3, $1/;
    $auth =~ s/([A-Z][$chars]+) ([A-Z][a-z][$chars]*) ($spanish)$/$2 $3, $1/;
  }
  $auth =~ s/([A-Z][$chars]+) ([A-Z][a-z]+e[zs]) ([A-Z][$chars]*)$/$2 $3, $1/;
  $auth =~ s/([A-Z][$chars]+) ([A-Z]\w+) ([A-Z][a-z]+e[zs])$/$2 $3, $1/;
  #print "author7 = $auth *\n";
  if ($auth !~ /\,/)
  {
    $auth=~s/(.*) ([A-Zdv][$char]+)$/$2, $1/;
  }
  #print "author10 = $auth *\n";
  $auth =~ s/([A-Z])\. ([A-Z])\./$1\.$2./g;
  #print "author11 = $auth *\n";
  $auth =~ s/(.*) ([A-Z][a-z]+) ([JrIV\.]+)$/$2, $1, $3/;
  my $author = $auth;
  return ($self->SUPER::foundAuth($auth));
}




sub extract
{
  my $self=shift;

  return (0) unless $self->ext eq 'auths';
	$self->Astrlist(
		Astrlist::Input->new(
			spi     => $self->spi,
			astrIdx => -1,
			verbose => $self->verbose
		)
	);

  my $bibKey = 0;
  my $affKey = 0;
  my $titleFlag = 0;
  my $titlefootFlag = 0;
  my $titlefootAff = "";
  my $namechars= "A-z\-";
  my $extracted=0;
  my $instituteStyle = 0;
  my %hash = ();
  my %hashInst = ();
  my $authorCluster = 0;
  my $authorStart = 0;
  my %hashSuper = ();
  my $instBrace = 0;
  my $altaffilFlag = 0;


  #
  # This first part seeks to replace any aliases and redefinitions
  #

  warn "extracting from tex file " . $self->file . "\n" if $self->verbose;
	if ( !( open( TEX, $self->file ) ) ) {
		warn "Error opening" . $self->file;
		return (0);
	}

	my $flat='';
  while ( defined ($info=<TEX>) )
  {
    chomp($info);

    if ($info =~ /\\optbar/)
    {
      next;
    }
    $info =~ s/[ ]+$//;
    $info =~ s/([^\%])\%.*/$1\n/;
    $info =~ s/\s*\\\\\s*/\n/g;
    if ($info =~ /\\affiliation\s*\{\s*\{[\{\s]*/)
    {
      $instBrace = 1;
      $info =~ s/\\affiliation\s*\{\s*\{[\{\s]*/\\affiliation\{/g;
    }
    elsif ($instBrace)
    {
      $info =~ s/\{\$\^/\$\^/g;
    }
    $info =~ s/\\linebreak / /;
    $info =~ s/\\centerline/\\mbox/g;
    $info =~ s/\\altaffilmark\{(\w+)\,\}/\\altaffilmark\{$1\}\,/g;
    $info =~ s/[alt\,]*address\=\{/\\address\{/g;
    $info =~ s/\$\\\,/\$/g;
    $info =~ s/\\\,\$/\$/g;
    $info =~ s/\,\s?\,/\,/g;
    if (!($info =~ /newcommand/))
    {
      $info =~ s/\\mbox[ ]+/\\mbox/g;
      #if ($info =~ /\\mbox\{(.*)\}$/){print "MBOX1 $1 *\n";}
      #if ($info =~ /\\mbox\{(.*)\}/){print "MBOX2 $info *\n";}
      $info =~ s/\\mbox\s*\{(.*)\}$/\n$1\n/g;
      $info =~ s/\\mbox\s*\{(.*)$/\n$1\n/g;
    }

    if ($info =~ /\\altaffiltext\{\w+\}\{[^\}]*$/)
    { print "Got the altaffilFlag\n";
      $altaffilFlag = 1;
    }
    if ($altaffilFlag && $info =~ /\}\s*$/)
    { print "Closed the altaffilFlag\n";
      $altaffilFlag = 0;
    }

    $info =~ s/\\institute\{[ ]*\$/\\institute\{\n\$/;
    $info =~ s/^[ ]+//;
    $info =~ s/^\$[ ]+(\S)/\$$1/;
    $info =~ s/\{[ ]+(\S)/\{$1/;
    if ($info =~ /\\\\\s*$/)
    { print "YYYYYYY $info **\n" if $self->verbose;
      $flat.= "$info\n";
    }
    elsif ($info =~ /\{[^\}]+$/ || $info =~ /\\newcommand\*?\{\\[^\}]+\}\s*$/
           || $altaffilFlag)
    {
      $info =~ s/\}\s+$/\}/;
       $flat.="$info ";
    }
    else
    {
      $flat.= "$info\n";
    }
  }

  close (TEX);

#
# Second pass
#

my $flat2='';

  foreach $info ( split /\n/, $flat)
  {

    chomp($info);
      print "infor:$info\n" if $self->verbose;
    $info =~ s/\}[ ]+\{/\}\{/g;
    #A.A.~Shishkin\Iref{dubna}
    $info =~ s/(.*)\\Iref\{(.*)\}/\\author\{$1\}\\affiliation\{$2\}/g;
#
    if ($info =~ /\\newcommand\*?\{\\(.*)\}\{(.*)\}/ ||
        $info =~ /\\def\\(.*)\{(\\.*)\}/  ||
        $info =~ /\\def\\(.*)\{(.*)\}/ )
    {
      $hash{$1} = $2;
      print "newcommand hash($1) = $hash{$1}\n" if $self->verbose;
    }
    elsif ($info =~ /\\newcommand\*?\\(.*)\{(.*)\}/ )
    {
      $hash{$1} = $2;
      print "newcommand hash($1) = $hash{$1}\n" if $self->verbose;
    }
    elsif ($info =~ /^\$\^\{?(\d+)\}?\$[\W]*(.*)/ ||
           $info =~ /\\altaffiltext\{(\w+)}\s*\{(.*)\}/ ||
            $info =~ /\\address\{\$\^\{?(\d+)\}?\$[\W]*(.*)/ )
    {
      my $aff5 = $2;
      my $aff5key = $1;
      print "AFF5 = $aff5\n" if $self->verbose;
      $aff5 =~ s/\\\\//;
      $aff5 =~ s/\$\^\{?[a-z]\}?\$//g;
      print "AFF5 = $aff5\n" if $self->verbose;
      $aff5 = $self->Decode($aff5);
      $hashSuper{$aff5key} = $aff5;
      $instituteStyle = 5;
      print "hashSuper($aff5key) = $hashSuper{$aff5key}\n" if $self->verbose;
    }
    else
    {
      for my $key (keys %hash)
      {
        $info =~  s/\\$key/$hash{$key}/g;
      }
    }
#
    $info =~ s/DpTitle/title/;
    if ($info =~ /\\title\{/)
    {
      $titleFlag = 1;
    }
    if ($titleFlag)
    {
      if ($info =~ /\}\s*$/)
      {
        $titleFlag = 0;
        $info = "$info\n"
      }
      if ($info =~ /\S/)
      {
        $flat2.= "$info";
      }
    }
    $info = $self->Decode($info);
    $info =~ s/\\thanksref\{[^\}]+\}//g;
    $info =~ s/\\corauthref\{\w+\}//g;
    $info =~ s/^\\address\{/\\affiliation\{/;
    #$info =~ s/^\\institute\{/\\affiliation\{/;
    $info =~ s/^\\inst\{/\\affiliation\{/;
    $info =~ s/\\author\s+\{/\\author\{/g;
    $info =~ s/\\affiliation[ ]+\{/\\affiliation\{/g;
#    $info =~ s/\\affiliation[\{]+/\\affiliation\{/g;
#    $info =~ s/^\{\$\^/\$\^/;
    $info =~ s/\\DpName\{(.+)\}\{(.+)\}/\\author\[$2\]\{$1\}/g;
    $info =~ s/\\DpNameTwo\{(.+)\}\{(.+)\}}\{(.+)\}/\\author\[$2,$3\]\{$1\}/g;
    $info =~ s/\\DpNameThree\{(.+)\}\{(.+)\}}\{(.+)\}\{(.+)\}/\\author\[$2,$3,$4\]\{$1\}/g;
    $info =~ s/affiliation(.*)\$[^\$]+\$/affiliation$1/g;
    $info =~ s/[ ]+/ /g;
    $info =~ s/[ ]+$//g;
    $info =~ s/^\s+//g;
    if ($info =~ /\\inst\{/)
    {
      $instituteStyle = 1;
    }
    if ($info =~ /\\author\{[^\}]*$/)
    {
      $authorStart  = 1;
    }
    if ($info =~ /\\author\{.*\$\,.*\$\,/)
    {
      $authorCluster = 1;
      $info =~ s/\$\,/\$\,\n/g;
    }
    if ($authorCluster || $authorStart)
    {
      $info =~ s/\,(\$[^\$]+\$)/$1\,/g;
      $info =~ s/\$\s*\,\s*/\$\,\n/g;
      if ($info =~ /\\affiliation/)
      {
        $authorCluster = 0;
        $authorStart  = 0;
      }
    }
    if ($instituteStyle)
    {
      if ($info =~ /\\institute\{/)
      {
        $instituteStyle = 2;
      }
      if ($instituteStyle == 2)
      {
        if ($info =~ /\}/)
        {
          $instituteStyle = 0;
        }
        $info =~ s/ \\and\s?/\}\n\\institute\{/g;
      }
    }
    if ($info =~ /\\institute\{/ && $instituteStyle == 0)
    {
      $instituteStyle = 4;
       print " = 4!!\n" if $self->verbose;
    }
    if ($instituteStyle == 4)
    {
      if ($info =~ /^\}/)
      {
        $instituteStyle = 0;
      }
      #print "1 $info\n" if $self->verbose;
      $info =~ s/\$(.*)\$(.*)/\\affiliation\{$2\}/;
      #print "2 $info\n" if $self->verbose;
    }
    if ($titleFlag == 0)
    {
      if ($info =~ /\\author\{.*\}\s*\\affiliation\{(.*)\}/)
      {
        $info =~ s/\\author\{([^\}]+)\}/\\author\{$1\}\n/;
      #  $flat2.= "$info\n";
      }
      if (($info =~ /\{[^\}]+$/ || $instituteStyle == 2))
      {
        $flat2.= "$info";
      }
      elsif ($info =~ /\w/)
      {
        $flat2.= "$info\n";
      }
      if ($info =~ /\\author\[.*\]\{.*\}/)
      {
        $instituteStyle = 3;
      }
      if ($instituteStyle == 3 && $info =~ /\\address\[(.*)\]\{(.*)/)
      {
        $hashInst{$1} = $2;
        print "$instituteStyle hashInst($1) = $hashInst{$1}\n" if $self->verbose;
      }
      if ($instituteStyle == 3 && $info =~ /\\titlefoot\{(.*)$/)
      {
        $titlefootAff = $1;
        $titlefootFlag = 1;
        #print "titlefootAff = $titlefootAff\n" if $self->verbose;
      }
      if ($titlefootFlag == 1 && $info =~ /\\label{(.*)\}\}/)
      {
        $hashInst{$1} = $titlefootAff;
        print "$instituteStyle hashInst($1) = $hashInst{$1}\n" if $self->verbose;
        $titlefootFlag = 0;
      }
    }
  }  # while split $flat


#
# End of second pass
#





my $final='';
  if ($instituteStyle == 3 || $instituteStyle == 5)
  {
    my $line;
    foreach (split /\n/, $flat2)
    {
      my $a = "\\author";
      my $b = "\n\\affiliation";
      if (/\\author\[.*\]\{.*\}/)
      {
        s/\\author\[(.*)\]\{([^\,]+)\,?\}/$a\{$2\}$b\{$hashInst{$1}\}/;
        $_ = $self->Decode($_);
        print "THIS $_\n" if $self->verbose;
      }
     if ($instituteStyle == 5 &&
         /^([A-Z].*)\$\^\{?(\w+)\,?\}\$\$\^\{?(\d+)/)
     {
       s/\$\^\{?(\w+)\,?\}\$//;
     }
#    if ($instituteStyle == 5 && /^([A-Z].*)\$\^\{?(\d+)\,(\d+)\}?\$[\s\,]*$/)
      if ($instituteStyle == 5 && /^([A-Z].*)\$\^\{?(\d+)\,\d[\d\,]*\}\$[\s\,]*$/
          ||  /^(.*)\\altaffilmark\{\w+\}\,\\altaffilmark.*altaffil/
          ||  /^(.*)\\altaffilmark\{\w+\}\,\\altaffilmark/)
      {
        my $manyAff  = "$a\{$1\}";
        #$b\{$hashSuper{$2}\}$b\{$hashSuper{$3}\}\n";
        while (/(\d+)/gc)
        {
          $manyAff  = "$manyAff"."$b\{$hashSuper{$1}\}";
        }
        while (/\{(\w+)\}/gc)
        {
          $manyAff  = "$manyAff"."$b\{$hashSuper{$1}\}";
        }
        $_ = "$manyAff\n";
        $_ = $self->Decode($_);
        print "THIS.SUP X $_\n"if $self->verbose;
      }
      if ($instituteStyle == 5 && /^([A-Z].*)\$\^\{?(\d+)\}?\$[\s\,]*$/ ||
           /^(.*)\\altaffilmark\{(\w+)\}[\,\s]*$/  )
      {
        $_  = "$a\{$1\}$b\{$hashSuper{$2}\}\n";
        $_ = $self->Decode($_);
        print "THIS.SUP 1 $_\n" if $self->verbose;
      }
      if ($instituteStyle == 5)
      {
        s/\\author\{\s*$//;
      }
      if (/\S/)
      {
        $final.= "$_";
      }
      if (/\\begin\{abstract\}/)
      {
        #return;
      }
    }
  }


  $foundauth=0;
  $foundaff=0;
  my $affFlag = 0;
  my $authorStyle=0;

  while (<FLAT>)
  {
    $foundauth=0;
    if (/^\\author\{s*$/)
    {
      $authorStyle = 3;
      print "authorStyle = $authorStyle\n";
    }
    if ($authorStyle == 3 && /^\}\s*$/)
    {
      $authorStyle = 0;
    }
    if (/\\title\{(.*)\}/)
    {
    	## FIX me -no method for this yet!

      #my $tt = $1;
      #$tt =~ s/([\$\s\,])\\(\w+)([\$\s\,])/$1$hash{$2}$3/g;
     # print EXTRACT "TT = $1\;\nASTR;\n";
    }
    #s/\\altaffiliation\{[^\}]+\}//g;
    if (/\\author\{([^\}]+)\}/)
    {
      $authorStyle = 1;
    }
    if (($authorStyle == 1 && /\\author\{([^\}]+)\}/) ||
        ($authorStyle == 3 && /(.*)\$.*\,/))
    {


      $self->foundAuth($1);
      $affFlag = 0;

    }
    while ($authorStyle == 1 && /\\affiliation\{([^\}]+)\}/gc)
    {
      $affFlag = 1;
      $self->foundAff($1);
    }
    if (/([A-Z][^\,]+)\\inst\{(\d+)\}/)
    {
      $authorStyle = 2;
    $self->foundAuth($1);
    }
    if ($authorStyle == 2 && /\\institute\{(.*)\}/)
    {
      $self->foundAff($1);
    }
    if ($authorStyle > 0)
    {
      $bibKey = 0;
    }
    if (/\\author/ && !/affiliation/)
    {
      $bibKey=1; #simple \author commands
      #print "bibKey = $bibkey\n";
    }
    if (/\\begin\{Authlist\}/i)
    {
      $bibKey=1;
      $needEnd="titlepage";
    }
    elsif (/^[A-Z\.\s\-]+ [A-Z][a-z]+[\$\{\}\^\w\s]+\,$/ && $authorStyle == 0)
    { #print "FOUND ONE $_\n";
      $bibKey=1;
    }
    if (($needEnd)&& (m/\\end\{$needEnd\}/))
    { print "end1 $_\n";
      $bibKey=0;
    }
    #if ((m/\\begin\{abstract/i || m/\\abstract\{/i) && !($instituteStyle==5))
    #{ print "end2 $_\n";
    #  $bibKey=0;   # almost certainly done
    #  print EXTRACT "hn(99) $extracted authors from coll_auth.pl\;\n";
    #  return $extracted;
    #}
    if (/\\end\{titlepage/i && !($instituteStyle==5))
    { print "end3 $_\n";
      $bibKey=0;   # almost certainly done
    }
    if (/\\section\{/i)
    { print "end4 $_\n";
      $bibKey=0;   # almost certainly done
    }
    if (/\\maketitle/i)
    { print "end4 $_\n";
      $bibKey=0;   # almost certainly done
    }
    if ($bibKey==1)
    {
      s/\\author[^\{]+\{/\\author\{/g;
      s/\\address[^\{]+\{/\\address\{/g;
      s/\\Instfoot\{[^\}]+\}\{/affiliation\{/;
      if( ! (m/author|affiliation|address/)  && m/\\Iref/)
      {
        s/^([^\\]*)\\Iref.*\,/author\{$1\}/;
      }
      s/\~/ /g;
      s/\\\"//g;
      s/\\\'\\i /i/g;
      s/\\\`//g;
      s/\\L\\\'od\\\'z/Lodz/g;
      s/\{\\l\}/l/g;
      s/\s+/ /g;
      s/\\thanksref\{.*\}//g;
      s/\\[^\w]\{([^\}]+)\}/$1/g;
      s/\\{\[^\w]([^\}]+)\}/$1/g;
      s/\\[^\w]//g;
      s/\\([A-z])/$1/g;
      s/\mbox\{([^\}]+)\}/$1/g;
      s/\;//g;
      s/\s+$//;
      #print "Let's check ***$_ ***\n";
      if (/author\{(.*)\}affiliation\{(.*)\}/)
      {
        $self->foundAuth($1);
        $self->foundAff($2);
      }
      elsif (/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/)
      {
        $auth="$5, $1 $2 $3 $4";
        $foundauth=1;
        #print "A1 = _$\n";
      }
      elsif (/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/)
      {
        $auth="$4, $1 $2 $3";
        $foundauth=1;
        #print "A2 = _$\n";
      }
      elsif (/author\{([$namechars]+\.)\s*([$namechars]+\.)\s*([^\}]+)\}/)
      {
        $auth="$3, $1 $2";
        $foundauth=1;
        #print "A3 = $_\n";
      }
      elsif (/author\{([$namechars]+\.)\s*([^\}]+)\}/)
      {
        $auth="$2, $1";
        $foundauth=1;
        #print "A4 = $_\n";
      }
      elsif (/([A-Za-z-\.]+\.) ([A-Z][a-z]+)([\s\-])([A-Z][a-z]+)\,?\$\^\{(\d+)/)
      {
        $auth="$2$3$4, $1";
        $foundauth=1;
        #print "A5 = $_\n";
      }
      elsif (/([A-Za-z\.\-]+\.) ([A-Z][a-z]+)\,\?$\^\{(\d+)/)
      {
        $auth="$2, $1";
        $foundauth=1;
        #print "A6 = $_\n";
      }
      elsif (/([A-Za-z\.\-]+\.) ([A-Z][a-z]+)altaffilmark\{\w\}/)
      {
        $auth="$2, $1";
        $foundauth=1;
        #print "A8 = $_\n";
      }
      elsif (/([A-Za-z\.\-]+\.) ([A-Za-z\.\-]+\.) ([A-Z][a-zA-Z\-]+)\,?\$\^\{(\d+)/)
      {
        $auth="$3, $1$2";
        $foundauth=1;
        #print "A9 = $_\n";
      }
      elsif (/^([A-Z\.\s\-]+) (Ma?c\s?[A-Z][a-z]+)[^\,]*\,?$/ ||
             /^([A-Z\.\s\-]+) ([A-Z][a-z]+[\- ][A-Z][a-z]+)[^\,]*\,?$/ ||
             /^([A-Z\.\s\-]+) ([A-Z][a-z]+)[\$\{\}\^\w\s]*\,?$/ )
      {
        $auth="$2, $1";
        $foundauth=1;
        #print "A10 = $_\n";
      }
      elsif (/^([A-Z\.\s\-]+) ([A-Z][a-z]+)[\$\{\}\^\w\s]*\,?/ &&
             $authorStyle==0)
      {
        #while (/([A-Z\.\s\-]+) ([A-Z][a-z]+)[\$\{\}\^\w\s]*\,?/gc)
        while (/([^\,]+)/gc)
        {
          $self->foundAuth($1);
        }
        #$foundauth=1;
        #print "A11 = $_\n";
      }
      if ($foundauth)
      {
        #print "A = $auth\n";
      }
      elsif (/affiliation\{([^\}]+)\}/)
      {
        $aff="$1";
        $foundaff=1;
      }
      elsif (/address\{([^\}]+)\}/)
      {
        $aff="$1";
        $foundaff=1;
      }
      elsif (/centerline\{\$\^\{(\d+)\}\$([^\}]+)\}?/)
      {
        $aff="$2";
        $foundaff=1;
      }
      elsif (/altaffiltext\{(\w)\} \{(.*)\}/)
      {
        $aff="$2";
        $foundaff=1;
      }
      elsif (/\{it ([^\}]+)\}/)
      {
        $aff="$1";
        $foundaff=1;
      }
      if ($foundauth && $authorStyle == 0)
      {
        if (($foundaff==1 || $affKey == 1) && $authorStyle == 0)
        {
          $foundaff=0;
        }

    $self->foundAuth($auth);
      }
      if ($foundaff)
      {
        $foundaff=0;
        chomp($aff);
        $aff=~s/\s+$//g;
        $self->foundAff($aff);
      }
      if (/^affiliation$/)
      {
        $affKey = 1;
      }
      if ($affKey && /\w/ && !/affiliation/)
      {
        s/\;/ /g;
        if (/[\$\^\d\{\}]+(.*)/)
        {
          $aff = $1;
          if ($foundaff == 0)
          {
          	$self->foundAff($aff);
          }
        }
        if (/^\}/)
        {
          $affKey = 0;
        }
      }
    }
  }
  print $self->extracted." extracted via Coll2\n" if $self_>verbose;
  return($self->extracted);
}


sub Decode
{
  my $line = $_[0];
  $line =~ s/\%.*$//g;  #LaTeX comments
  if ($line =~ /\\\\[ ]*$/)
  {
#    print "AAAA $line *\n";
    $line =~ s/\\\\/ /g;
#    print "BBBB $line *\n";
  }
#  $line =~ s/[ ]*\\\\[ ]*/\n/g;
#  $line =~ s/\\\\/ /g;
  $line =~ s/\\&/ and /g;
  $line =~ s/--/-/g;
#  $line =~ s/\$,[ ]+/\$,\n/g;
  $line =~ s/\\ss/ss/g;
  $line =~ s/\\\,/ /;
  $line =~ s/^[ ]+//;
  $line =~ s/\{\\l\}\\\-/l/g;
  $line =~ s/\\\'\{\\i\}/i/g;
  $line =~ s/\\[cuv]\{([A-Za-z])\}/$1/g;
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
  $line =~ s/\\L /L/g;
  $line =~ s/\\Lodz/Lodz/g;
  $line =~ s/\~/ /g;
  $line =~ s/\\v //g;
  $line =~ s/\\c c/c/g;
  if ($line =~ /Kra/)
  {
    print "$line\n";
  }
  return "$line";
}


1;
