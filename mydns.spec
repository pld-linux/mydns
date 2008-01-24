# TODO:
# - fix configure patch to change source file instead of generated configure
#
# Conditional build:
%bcond_with	mysql		# enable MySQL support
%bcond_with	pgsql		# enable PostgreSQL support
%bcond_with	ssl		# enable TLS/SSL support
#
Summary:	MyDNS - a free Database Driven Nameserver
Summary(pl.UTF-8):	MyDNS - darmowy serwer nazw wykorzystujący relacyjne bazy danych
Name:		mydns
Version:	1.1.0
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://mydns.bboy.net/download/%{name}-%{version}.tar.gz
Source1:	%{name}.conf
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Patch0:		%{name}-configure.patch
URL:		http://mydns.bboy.net/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake >= 1:1.9.6
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ssl:BuildRequires:	openssl-devel >= 0.9.7i}
%{?with_pgsql:BuildRequires:	postgresql-devel}
BuildRequires:	rpmbuild(macros) >= 1.310
BuildRequires:	texinfo
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Provides:	nameserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MyDNS is a free DNS server implemented from scratch and is designed to
serve records directly from an SQL database, either MySQL or
PostgreSQL.

%description -l pl.UTF-8
MyDNS to darmowy serwer nazw zaimplementowany od podstaw i
zaprojektowany aby udostępniać rekordy bezpośrednio z bazy SQL -
obecnie MySQL lub PostgreSQL.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	--disable-nls \
	--with-confdir=%{_sysconfdir}/%{name} \
	--with%{?with_mysql:out}-pgsql \
	--with%{?with_pgsql:out}-mysql \
	--with%{!?with_ssl:out}-openssl

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/%{name},/etc/sysconfig}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/mydns

rm -f $RPM_BUILD_ROOT%{_infodir}/dir*

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun	-p	/sbin/postshell
-/usr/sbin/fix-info-dir -c %{_infodir}

%files
%defattr(644,root,root,755)
%doc ChangeLog AUTHORS BUGS README README.mysql INSTALL NEWS TODO QUICKSTART.*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mydns
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%{_infodir}/*.info*
%{_mandir}/man*/*
