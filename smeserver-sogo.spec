# $Id$
%define name smeserver-sogo
%define version 1.3
%define release 16

Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Summary:	SME Server SOGo Groupware
Group:		Networking/Daemons
License:	GPLv3+
URL:		http://www.smeserver.org
Source0:	%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Epoch: 9
BuildRequires:	e-smith-devtools
Requires:	smeserver-release >= 9
Requires:	e-smith-ldap
Requires:	sogo >= 2.3.0
Requires:	sogo-tool
Requires:	memcached
Requires:	sogo-activesync
Requires: 	sope49-gdl1-mysql
Requires: 	sogo-ealarms-notify
Requires: 	python-memcached
Requires:       smeserver-dovecot-extras
%description
SME Server module for SOGo groupware.

%prep
##my bad to remove a bad folder if exists [1.3-6.sme]
/bin/rm -rf /var/service/tinydns/root/data/ &> /dev/null

%setup -q

%build
[ -x createlinks ] && ./createlinks

%install
rm -rf $RPM_BUILD_ROOT
rm -f %{name}-%{version}-filelist

(cd root   ; /usr/bin/find . -depth -print | /bin/cpio -dump $RPM_BUILD_ROOT)

/sbin/e-smith/genfilelist \
    --dir /var/lib/sogo/GNUstep 'attr(0755,sogo,sogo)' \
    --dir /var/lib/sogo/GNUstep/Defaults 'attr(0755,sogo,sogo)' \
    $RPM_BUILD_ROOT > %{name}-%{version}-%{release}-filelist

%clean
rm -rf $RPM_BUILD_ROOT


%post

if [ $1 == 1 ]; then #first install
    /etc/e-smith/events/actions/initialize-default-databases &> /dev/null
    /sbin/e-smith/expand-template \
        /etc/e-smith/sql/init/30sogo_mysql_create_database
    /sbin/e-smith/expand-template \
        /etc/e-smith/sql/init/31sogo_mysql_update_privileges
    /sbin/e-smith/expand-template \
        /var/lib/sogo/smeserver/sogo_mysql_update_privileges.sql
    /sbin/e-smith/expand-template \
        /etc/e-smith/sql/init/31sogo_upgrade
    /sbin/e-smith/expand-template \
       /etc/e-smith/sql/init/32sogo_upgrade_2.3
    /sbin/service mysql.init start
    /sbin/e-smith/signal-event sogo-modify
elif [ $1 -gt 1 ]; then #update
    /sbin/e-smith/expand-template \
        /etc/e-smith/sql/init/31sogo_upgrade
    /sbin/e-smith/expand-template \
       /etc/e-smith/sql/init/32sogo_upgrade_2.3
    /sbin/service mysql.init start
    /etc/e-smith/events/actions/initialize-default-databases &> /dev/null || :
    /sbin/e-smith/signal-event sogo-modify || :
fi

# set sogo password
/bin/cat /etc/openldap/ldap.pw | /usr/bin/passwd sogo --stdin &> /dev/null || :


%postun
if [ $1 = 1 ]; then
    /etc/e-smith/events/actions/initialize-default-databases &> /dev/null || :
    /sbin/e-smith/signal-event sogo-modify || :
fi



%files -f %{name}-%{version}-%{release}-filelist


%changelog
* Wed Oct 7 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-16.sme
- /etc/e-smith/sql/init/32sogo_upgrade_2.3 is now executable

* Sat Aug 22 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-15.sme
- Added sogo-modify to mysql.init

* Wed Jul 8 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-14.sme
- Upgrade to sogo 2.3.0, alteration table needed
- thank to ian case <ianc@caseinfo.net>

* Sat Feb 21 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-12.sme
- Remove a sogo user when a SME Server user is removed

* Sat Feb 21 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-11.sme
- Fix the qpsmtpd fix_headers_case plugin

* Tue Jan 6 2015 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-10.sme
- Added bindFields parameters to SOGoUserSources based on suggestion of Nicola Tiana in [SME: 7578]
- According to SOGo installation guide, the value of bindFields has to be in an array for recent version
- Thanks to  Mats Schuh <m.schuh@neckargeo.net>

* Tue Dec 30 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-9.sme
- stop cron email confirmation to the sogo user account [SME: 8756]
- code done by Mats Schuh <m.schuh@neckargeo.net>

* Mon Dec 29 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-8.sme
- Sogo must be an admin of dovecot for expire-autoreply [SME: 8753]
- Thanks to  Mats Schuh <m.schuh@neckargeo.net>

* Sat Nov 01 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-7.sme
- removed a bad file 80srvSOGo in the template path of /var/service/tinydns/root/data
- added restart and event-template to tinydns with sogo-modify

* Sun Sep 21 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-5.sme
- SOGoMailMessageCheck has been replaced by SOGoRefreshViewCheck

* Sun Aug 31 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-4.sme
- Added  . separator for imap, instead of / by default

* Sun Aug 17 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.3-3.sme
- a bit of clean and new  code inspired from ipasserelle-groupware. Thanks to daniel berteaud <daniel@firewall-services.com>
- added sieve and acl support (come with smeserver-dovecot-extras)
- added a panel in the server-manager with options
- added active-sync support
- added sogo notifications


* Thu May 08 2014 stephane de Labrusse <stephdl@de-labrusse.fr> - 1.1-2
- First release For SME Server 9 Thanks for all previous valorous developers
- removed expand-template for bootstrap-console-save in createlink
- added an architecture detection for template the file 
- /etc/e-smith/templates/etc/httpd/conf/httpd.conf/85SOGoAccess

* Wed Dec 11 2013 Davide Principi <davide.principi@nethesis.it> - 1.0.1-1
- Fixed sogo.conf syntax. Refs #2339

* Mon Dec  9 2013 Davide Principi <davide.principi@nethesis.it> - 1.0.0-1
- Release 1.0.0. Refs #2339
- Require sogo >= 2.1.1b-1  

* Mon Dec  9 2013 Davide Principi <davide.principi@nethesis.it> - 0.9.1-1
- Release 0.9.1
- Fixes bug #2372

* Mon Dec  2 2013 Davide Principi <davide.principi@nethesis.it> - 0.9-1
- sogo home directory moved to /var/lib/sogo to fix #2369

* Fri Apr 26 2013 Davide Principi <davide.principi@nethesis.it> - 0.8-2
- Create symlink to new SOGo 2.0.x homedir, to support fresh installations

* Thu Oct 18 2012 Giacomo Sanchiettti <giacomo.sanchietti@nethesis.it> - 0.8-1
- Add support for vacation auto-disable feature
- Add memcached requires (previously on sogo package)

* Fri Sep 14 2012 Alessio Fattorini <alessio.fattorini@nethesis.it> - 0.7-1
- Enable notification for calendar modifications (refs #1398)
- Customize From header (refs #1339)
- Support SharedFolder (refs #1432)

* Fri Mar 9 2012 Alessio Fattorini <alessio.fattorini@nethesis.it> - 0.6.1
- Removed bindFields (bug #845)
- Fixed backup by sogo-tool (bug #839)
- Upgrade SOGo db to 1.3.12

* Wed Nov 30 2011 Alessio Fattorini <alessio.fattorini@nethesis.it> - 0.6
- change GNUstep path

* Wed Sep 7 2011 Alessio Fattorini <alessio.fattorini@nethesis.it> - 0.5.9-2
- Add CardDAV external access (bug #423) 

* Wed Jul 20 2011 Alessio Fattorini <alessio.fattorini@nethesis.it> - 0.5.9-1
- Disable sieve support for NethService 8.0
- Correct postun

* Mon May 16 2011 Giacomo Sanchietti <giacomo@nethesis.it> - 0.5.8-1
- Add sieve support
- Add configurable prefork option
- Enable session folders
- Update to SOGo 1.3.4

* Thu Aug  5 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.6-1
- add configurable option for ACLsSendEMailNotifications
- add EnablePublicAccess
- change MailingMechanism to SMTP
- redirect http requests for sogo to SOGo

* Mon Aug  2 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.5-1
- upgrade to sogo 1.3.0

* Tue Mar 30 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.4-1
- escape curly brackets in sogo logrotate template

* Fri Mar 19 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.3-1
- add logrotate for sogo log files
- nethesis smesetup (post/postun) scripts

* Tue Mar 16 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.2-2
- rej files cleanup

* Tue Mar 16 2010 Daniel Berteaud <daniel@firewall-services.com> - 0.5.2-1
- enable groups for ACL
- configure admin users from the db
- disable bogus notifications (acl and folders)
- configure sent and draft imap folders from DB
- redirect webmail when imp is disabled (Stephen Noble)
- proxypass port from the db (Federico Simoncelli)

* Fri Mar 12 2010 Daniel Berteaud <daniel@firewall-services.com> - 0.5.1-1
- anonymous bind is sufficient to authenticate users
- limit sogo daemon bind to the loopback interface
- SOGo protected with SSL
- memcached bind to loopback, port from TCPPort
- templates expansion from post-upgrade to bootstrap-console-save
- read the ldap port from db
- split the local ldap directory in two parts: users and groups
- notifications sent by email will have the correct URL

* Thu Feb 18 2010 Federico Simoncelli <federico@nethesis.it> - 0.5.0-1
- first release


