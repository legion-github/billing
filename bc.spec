%define python_sitearch %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib(1)')

%define bc_user  _bc
%define bc_group _bc

Summary:  BC Platform package
Name:     bc
Version:  2.0.0
Release:  1%{?dist}
Epoch:    %(date +%s)
License:  GPLv3
Group:    Applications/System

BuildRequires: python
BuildRequires: python-setuptools

Requires: python
Requires: python-psycopg2
Requires: python-msgpack
Requires: bc-common

BuildRoot:  %_tmppath/%name-%version-root
BuildArch:  noarch

Source0: bc.tar.gz

%description
BC Platform package.


%package calc-server
Summary:  BC Platform - Calc server
Group:    Applications/System

Requires: python
Requires: bc-common

%description calc-server
Billing calculator.


%package data-server
Summary:  BC Platform - Data manage server
Group:    Applications/System

Requires: python
Requires: bc-common
Requires: bc-client

%description data-server
Storage data contoller.


%package wapi
Summary:  BC Platform - API Controller
Group:    Applications/System

Requires: python
Requires: httpd
Requires: mod_wsgi
Requires: bc-common
Requires: bc-jsonrpc

%description wapi
HTTP API interface for contoller.


%package admin
Summary:  BC admin utilities
Group:    Applications/System

Requires: bc-common
Requires: bc-client

%description admin
BC admin utilities.


%package jsonrpc
Summary:  JSONRPC implementation for python
Group:    Applications/System

Requires: python

%description jsonrpc
JSONRPC implementation.


%package common
Summary:  BC server library
Group:    Applications/System

Requires: python
Requires: python-psycopg2
Requires: python-msgpack

%description common
BC common files, directories and libraries.


%package client
Summary:  BC client library
Group:    Applications/System

Requires: python
Requires: bc-jsonrpc
Requires: python-connectionpool

# TODO: Remove
Requires: bc-common

%description client
BC client library.


%prep
%setup -q


%install
[ %buildroot = "/" ] || rm -rf %buildroot

%__python setup.py install \
	--root="%buildroot" \
	--prefix="%_prefix" \
	--install-lib="%python_sitearch"

mkdir -p -- %buildroot/%_localstatedir/run/bc

find %buildroot/ -name '*.egg-info' -exec rm -rf -- '{}' '+'

# Remove for now
rm -rfv -- %buildroot/etc/cron.d %buildroot/usr/share/c2

%clean
[ %buildroot = "/" ] || rm -rf %buildroot


%pre calc-server
groupadd -r -f %bc_group
getent passwd %bc_user >/dev/null ||
	useradd  -r -M -g %bc_group -d /dev/null -s /dev/null -n %bc_user

%post calc-server
if [ "$1" = "0" ]; then
	chkconfig --add bc-calc
else
	service bc-calc condrestart
fi

%preun calc-server
if [ "$1" = "0" ]; then
	service bc-calc stop ||:
	chkconfig --del bc-calc ||:
fi

%pre data-server
groupadd -r -f %bc_group
getent passwd %bc_user >/dev/null ||
	useradd  -r -M -g %bc_group -d /dev/null -s /dev/null -n %bc_user

%post data-server
if [ "$1" = "0" ]; then
	chkconfig --add bc-data
else
	service bc-data condrestart
fi

%preun data-server
if [ "$1" = "0" ]; then
	service bc-data stop ||:
	chkconfig --del bc-data ||:
fi

%post wapi
service httpd condrestart ||:

%postun wapi
[ "$1" != "0" ] || service httpd condrestart ||:


%pre common
groupadd -r -f %bc_group


%files calc-server
%_bindir/bc-calc-*
%_sysconfdir/rc.d/init.d/bc-calc
%attr(770,root,%bc_group) %_localstatedir/run/bc

%files data-server
%_sysconfdir/rc.d/init.d/bc-data
%_bindir/bc-data-*
%attr(770,root,%bc_group) %_localstatedir/run/bc

%files admin
%_bindir/billing-*
%_bindir/task_creator
%attr(600,root,root) %config(noreplace) %_sysconfdir/wapi-acl.conf

%files common
%attr(644,root,%bc_group) %config(noreplace) %_sysconfdir/billing.conf
%python_sitearch/bc

%files jsonrpc
%python_sitearch/bc_jsonrpc

%files client
%python_sitearch/bc_client

%files wapi
%_libexecdir/bc
%python_sitearch/bc_wapi
%config(noreplace) %_sysconfdir/httpd/conf.d/*.conf


%changelog
* Wed Oct 10 2012 Alexey Gladkov <alexey.gladkov@gmail.com> 1349878993:2.0.0-1.el6
- First standalone build.
