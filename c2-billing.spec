%define python_sitearch %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib(1)')

Summary:  CROC Cloud Platform - Billing controller
Name:     c2-bc
Version:  0.0.0
Release:  CROC1%{?dist}
Epoch:    %(date +%s)
License:  GPLv3
Group:    Applications/System

BuildRequires:  python, python-setuptools

Requires:       python
Requires:       c2-bc-common-cloud

Vendor:     CROC
URL:        http://cloud.croc.ru
BuildRoot:  %_tmppath/%name-%version-root
BuildArch:  noarch

Source0: c2-billing.tar.gz

%description
CROC Cloud Platform billing controller


%package common-billing
Summary:  CROC Cloud billing commons (billing side)
Group:    Applications/System

Requires: c2-common

%description common-billing
CROC Cloud billing common files, directories and libraries.
Billing private library.


%package common-cloud
Summary:  CROC Cloud billing commons (cloud side)
Group:    Applications/System

Requires: python-mongo
Requires: python-msgpack

%description common-cloud
CROC Cloud billing common files, directories and libraries.
Billing public interface.


%package -n c2-abc
Summary:  CROC Cloud Platform - API Controller
Group:    Applications/System

Requires:       python, httpd, mod_wsgi
Requires(pre):  c2-bc-common-cloud

%description -n c2-abc
CROC Cloud Platform API Controller


%package -n c2-gs-bc
Summary:  CROC Cloud Platform Garbage collection service (BC)
Group:    Applications/System

Requires: c2-gs
Requires: c2-bc-common-cloud

%description -n c2-gs-bc
Garbage collection service (BC)


%prep
%setup

%install
[ %buildroot = "/" ] || rm -rf %buildroot

%__python setup.py install \
	--root="%buildroot" \
	--prefix="%_prefix" \
	--install-lib="%python_sitearch"

find %buildroot/ -name '*.egg-info' -exec rm -rf -- '{}' '+'

%clean
[ %buildroot = "/" ] || rm -rf %buildroot

%post
chkconfig --add %name

%preun
service %name stop ||:
[ "$1" != "0" ] || chkconfig --del %name ||:

%post -n c2-abc
service httpd condrestart ||:

%postun -n c2-abc
[ "$1" != "0" ] || service httpd condrestart ||:

%post -n c2-gs-bc
service crond reload

%preun -n c2-gs-bc
[ "$1" != "0" ] || service crond reload ||:

%files
%_bindir/*
%_sysconfdir/rc.d/init.d/*

%files common-billing
%_sysconfdir/billing.conf
%python_sitearch/bc

%files common-cloud
%python_sitearch/billing

%files -n c2-abc
%_libexecdir/billing
%config(noreplace) %_sysconfdir/httpd/conf.d/*.conf

%files -n c2-gs-bc
%_datadir/c2/gs
%config(noreplace) %_sysconfdir/cron.d/*

%changelog
