#!/usr/bin/perl -w 

#----------------------------------------------------------------------
# copyright (C) 2011 Firewall-Services
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#----------------------------------------------------------------------
package    esmith::FormMagick::Panel::sogo;

use strict;

use esmith::FormMagick;
use esmith::AccountsDB;
use esmith::ConfigDB;
use esmith::cgi;
use esmith::util;
use Exporter;
use Carp qw(verbose);

our @ISA = qw(esmith::FormMagick Exporter);

our @EXPORT = qw(
    get_prop
    apply
);


our $accountdb = esmith::AccountsDB->open();
our $configdb = esmith::ConfigDB->open();

sub new {
    shift;
    my $self = esmith::FormMagick->new();
    $self->{calling_package} = (caller)[0];
    bless $self;
    return $self;
}

sub get_prop{
    my ($fm, $prop, $default) = @_;
    return $configdb->get_prop("sogod", $prop) || $default;
}

sub apply {
    my ($self) = @_;
    my $q = $self->{cgi};

    $configdb->set_prop('sogod', 'status', $q->param("status"));
    $configdb->set_prop('sogod', 'ACLsSendEMailNotifications', $q->param("aclSendMail"));
    $configdb->set_prop('sogod', 'MailAuxiliaryUserAccountsEnabled', $q->param("auxAccounts"));
    $configdb->set_prop('sogod', 'PublicAccess', $q->param("publicAccess"));
    $configdb->set_prop('sogod', 'ActiveSync', $q->param("activeSync"));
    $configdb->set_prop('sogod', 'EnableEMailAlarms', $q->param("enableEMailAlarms"));
    
    unless ( system ("/sbin/e-smith/signal-event", "sogo-modify") == 0 ){
        return $self->error('ERROR_OCCURED', 'FIRST');;
    }

    return $self->success('SUCCESS','FIRST');
}

1;
