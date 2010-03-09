# /usr/local/bin/perl


use Test::Simple tests=>20;
use Data::Dumper;
use Expect::Spires;

my $spitest=Expect::Spires->new(debug=>1,database=>'RESTAURANT');


warn "Tests rely on the RESTAURANT db as installed with SPIRES\n";

ok(defined($spitest) && ref $spitest eq 'Expect::Spires', 'constructor works');
ok($spitest->test,'module is live');

#$spitest->ask('sel restaurant');
ok( $spitest->ask('sho sel')=~ /RESTAURANT/i , 'Restaurant selected, init via db is working');
ok($spitest->number('find name pot')==3 ,' Restaurant search finds 3 \'pots\' number is working (failure might be bad data in restaurant..)');
ok($spitest->number('and name foobarblarf')==0 ,' Restaurant search finds nothing');
ok(!($spitest->toflag), "to flag is not set");

$spishort=Expect::Spires->new(debug=>1,database=>'RESTAURANT',timeout=>'1');
print $spishort->ask('sleep 40');
ok($spishort->toflag,"toflag is set on timeout");



$spitest->number('find name pot');
my $comment=$spitest->element('comments');
ok($comment=~/^\s*\"Located .* garlic dressing/, '->element (scalar) returned correct value');


my @comments=$spitest->element('comments');
ok(@comments, '->element (array) returned value');

#print Dumper(@comments);
ok($comments[1][0]=~/food marvelous\.\s*$/, '->element (array) returned correct value');


my $name=$spitest->list('name');
ok($name=~/pot/i, '->list (scalar) returned correct value');

my @names=$spitest->list('name');
ok($names[0]=~/pot/i, '->list (array) returned correct value');


ok($spitest->number('or name suzette')==4,'search history preserved');
my @recs=$spitest->element('recommender');
ok($recs[1][1] eq 'V. Davis','->elem (array for mult occ. elems)');


#print Dumper(@recs);

#test merge
$num_res=$spitest->number("find name pot");
$merge_str="Recommender(100)= Travis Brooks;";
ok($spitest->merge($merge_str)==$num_res,'merge into result (Failure may mean no privs in restaurant file)');
ok($spitest->merge($merge_str,733)==1,'merge with key');

$spitest->ask("clr sta","sta 733","gen res");
@recs=($spitest->element('recommender'))[0];
$rec=pop @{$recs[0]};
ok($rec=~/Travis Brooks/, "Merge actually updates");

$num_res=$spitest->number("find name pot");
$batch_str="mer 733;\nRecommender(100)= M. Sullivan;\n;\n";
ok($spitest->batch($batch_str,'restaurant')==1,'batch into result (Failure may mean no privs in restaurant file)');
$spitest->number("find name pot");
@recs=$spitest->list("recommender");

ok(grep(/M\. Sullivan/,@recs), "batch actually updates");


#undo any damage...
$spitest->ask("find name pot","for res","deq all",'endf');

#$spitest->number("sel hep","find a brooks, t and a bjorken");
$spitest->number("find name pot");
%hash=$spitest->asHash();
ok($hash{NAME}->[0]=~/pot/i,'asHash returns correct hash');

