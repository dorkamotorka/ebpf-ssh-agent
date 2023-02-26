%define version_from_deb %(dpkg-parsechangelog --show-field version | sed -E 's/\.[0-9]+$//g')
%define patch_ver_from_deb %(dpkg-parsechangelog --show-field version | grep -Eo '\.[0-9]+$' | cut -c 2-)

Name: sshlog
Version: %{version_from_deb}
Release: %{patch_ver_from_deb}%{?dist}
Summary: SSH logging utility

License: AGPLv3
URL: https://github.com/sshlog/sshlog
Source0: %{name}-%{version}.tar.gz

%{?systemd_requires}
#Buildrequires: systemd-rpm-macros
#BuildRequires: cmake
#Requires: 

%description
sshlog is a tool that logs SSH activity.

# Ignore installed files that we don't use (e.g., symlink for libsshlog.so)
%define _unpackaged_files_terminate_build 0

%prep
%setup -q

%build
# If compiling for kernel version 5.8+, use -DUSE_RINGBUF=ON for more efficient data transfer
cmake \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_VERBOSE_MAKEFILE=OFF \
    -DCMAKE_COLOR_MAKEFILE=ON \
    -Bbuild_redhat/ -S.
cd build_redhat; make -j8;

%install
rm -rf %{buildroot}
cd build_redhat/
make install DESTDIR=%{buildroot}
cd ../

./daemon/build_binary.sh
mkdir -p %{buildroot}/usr/bin/
cp dist/* %{buildroot}/usr/bin/
mkdir -p %{buildroot}/var/log/sshlog && chmod 700 %{buildroot}/var/log/sshlog
mkdir -p %{buildroot}/etc/sshlog/conf.d
mkdir -p %{buildroot}/etc/sshlog/plugins
mkdir -p %{buildroot}/etc/sshlog/samples
mkdir -p %{buildroot}/usr/lib/systemd/system/
cp daemon/config_samples/* %{buildroot}/etc/sshlog/samples/
cp distros/redhat/sshlog.service %{buildroot}/usr/lib/systemd/system/ 

%clean
rm -rf %{buildroot}

# Add a group for sshlog
%pre
groupadd sshlog 2>/dev/null || true

# Install the systemd service
%post
%systemd_post sshlog.service

%postun
%systemd_postun sshlog.service

%files
%defattr(-,root,root,-)
/usr/bin/*
/usr/lib/libsshlog.so.1
/var/log/sshlog
/etc/sshlog/*
/usr/lib/systemd/system/sshlog.service