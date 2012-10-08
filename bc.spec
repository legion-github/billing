%define python_sitearch %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib(1)')

%define bc_user  _bc
%define bc_group _bc

Summary:  CROC Cloud Platform - Billing controller
Name:     bc
Version:  0.0.0
Release:  CROC1%{?dist}
Epoch:    %(date +%s)
License:  GPLv3
Group:    Applications/System

BuildRequires:  python, python-setuptools

Requires: python
Requires: python-psycopg2
Requires: python-msgpack
Requires: bc-common

Vendor:     CROC
URL:        http://cloud.croc.ru
BuildRoot:  %_tmppath/%name-%version-root
BuildArch:  noarch

Source0: billing.tar.gz

%description
CROC Cloud Platform billing controller


%package admin
Summary:  CROC Cloud billing admin utilities
Group:    Applications/System

%description admin
CROC Cloud billing admin utilities


%package common
Summary:  CROC Cloud billing commons (billing side)
Group:    Applications/System

%description common
CROC Cloud billing common files, directories and libraries.
Billing private library.


%package jsonrpc
Summary:  JSONRPC implementation for python.
Group:    Applications/System

%description jsonrpc
JSONRPC implementation.


%package client-billing
Summary:  CROC Cloud billing client library.
Group:    Applications/System

Requires: common
Requires: bc-jsonrpc

%description client-billing
CROC Cloud billing client library.


%package wapi
Summary:  CROC Cloud Platform - API Controller
Group:    Applications/System

Requires:  python, httpd, mod_wsgi
Requires:  bc-common
Requires:  bc-jsonrpc

%description wapi
HTTP API interface for contoller.


%package -n gs-bc
Summary:  CROC Cloud Platform Garbage collection service (BC)
Group:    Applications/System

Requires: gs
Requires: bc-common

%description -n gs-bc
Garbage collection service (BC)


%prep
%setup

%install
[ %buildroot = "/" ] || rm -rf %buildroot

%__python setup.py install \
	--root="%buildroot" \
	--prefix="%_prefix" \
	--install-lib="%python_sitearch"

mkdir -p -- %buildroot/%_localstatedir/run/bc

find %buildroot/ -name '*.egg-info' -exec rm -rf -- '{}' '+'

%clean
[ %buildroot = "/" ] || rm -rf %buildroot

%pre
groupadd -r -f %bc_group
getent passwd %bc_user >/dev/null ||
	useradd  -r -M -g %bc_group -d /dev/null -s /dev/null -n %bc_user

%post
chkconfig --add %name

%preun
service %name stop ||:
[ "$1" != "0" ] || chkconfig --del %name ||:

%pre common
groupadd -r -f %bc_group

%post wapi
service httpd condrestart ||:

%postun wapi
[ "$1" != "0" ] || service httpd condrestart ||:

%post -n gs-bc
service crond reload

%preun -n gs-bc
[ "$1" != "0" ] || service crond reload ||:

%files
%_bindir/bc-*
%_sysconfdir/rc.d/init.d/*
%attr(770,root,%bc_group) %_localstatedir/run/bc

%files admin
%_bindir/billing-*

%files common
%attr(644,root,%bc_group) %config(noreplace) %_sysconfdir/billing.conf
%python_sitearch/bc

%files jsonrpc
%python_sitearch/bc_jsonrpc

%files client-billing
%python_sitearch/bc_client

%files wapi
%_libexecdir/bc
%python_sitearch/bc_wapi
%config(noreplace) %_sysconfdir/httpd/conf.d/*.conf

%files -n gs-bc
%_datadir/c2/gs
%config(noreplace) %_sysconfdir/cron.d/*

%changelog
