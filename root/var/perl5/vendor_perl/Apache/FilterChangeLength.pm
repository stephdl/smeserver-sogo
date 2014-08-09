package Apache::FilterChangeLength;

use strict;
use warnings FATAL => 'all';

use Apache2::RequestRec ();

use APR::Table ();
use APR::Bucket ();
use APR::Brigade ();

use base qw(Apache2::Filter);

use Apache2::Const -compile => qw(OK);
use APR::Const     -compile => ':common';

sub handler {
    my ($filter, $bb) = @_;
    my $ctx = $filter->ctx;
    my $data = exists $ctx->{data} ? $ctx->{data} : '';
    $ctx->{invoked}++;
    my ($bdata, $seen_eos) = flatten_bb($bb);
    $data .= $bdata if $bdata;

    if ($seen_eos) {
        my $len = length $data;
        $filter->r->headers_out->set('Content-Length', $len);
        $filter->print($data) if $data;
    }
    else {
        # store context for all but the last invocation
        $ctx->{data} = $data;
        $filter->ctx($ctx);
    }

    return Apache2::Const::OK;
}

sub flatten_bb {
    my ($bb) = shift;
    my $seen_eos = 0;

    my @data;
    for (my $b = $bb->first; $b; $b = $bb->next($b)) {
        $seen_eos++, last if $b->is_eos;
        $b->read(my $bdata);
        push @data, $bdata;
    }
    return (join('', @data), $seen_eos);
}

1;
