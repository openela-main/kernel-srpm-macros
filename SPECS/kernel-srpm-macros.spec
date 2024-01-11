Name:           kernel-srpm-macros
Version:        1.0
Release:        13%{?dist}
Summary:        RPM macros that list arches the full kernel is built on
# This package only exist in Fedora repositories
# The license is the standard (MIT) specified in
# Fedora Project Contribution Agreement
# and as URL we provide dist-git URL
License:        MIT
URL:            https://src.fedoraproject.org/rpms/kernel-srpm-macros
BuildArch:      noarch
# We are now the ones shipping kmod.attr
Conflicts:      redhat-rpm-config <= 184
# macros.kmp, kmodtool and rpmsort were moved from kernel-rpm-macros
# to kernel-srpm-macros in 1.0-9/185-9
Conflicts:      kernel-rpm-macros < 185-9

# Macros
Source0:        macros.kernel-srpm
Source1:        macros.kmp

# Dependency generator scripts
Source100:      find-provides.ksyms
Source101:      find-requires.ksyms
Source102:      firmware.prov
Source103:      modalias.prov
Source104:      provided_ksyms.attr
Source105:      required_ksyms.attr
Source106:      modalias.attr

# Dependency generators & their rules
Source200:      kmod.attr

# Misc helper scripts
Source300:      kmodtool
Source301:      rpmsort
Source302:      symset-table

# kabi provides generator
Source400: kabi.attr
Source401: kabi.sh

# BRPs
Source500: brp-kmod-set-exec-bit
Source501: brp-kmod-restore-perms

%global rrcdir /usr/lib/rpm/redhat


%description
This packages contains the rpm macro that list what arches
the full kernel is built on.
The variable to use is kernel_arches.

%package -n kernel-rpm-macros
Version: 185
Release: %{release}
Summary: Macros and scripts for building kernel module packages
Requires: redhat-rpm-config >= 13

# for brp-kmod-compress
Requires: %{_bindir}/xz
# for brp-kmod-compress, brp-kmod-set-exec-bit
Requires: %{_bindir}/find
# for find-provides.ksyms, find-requires.ksyms, kmodtool
Requires: %{_bindir}/sed
# for find-provides.ksyms, find-requires.ksyms
Requires: %{_bindir}/awk
Requires: %{_bindir}/grep
Requires: %{_bindir}/nm
Requires: %{_bindir}/objdump
Requires: %{_bindir}/readelf
# for find-requires.ksyms
Requires: %{_sbindir}/modinfo
Requires: %{_sbindir}/modprobe

%description -n kernel-rpm-macros
Macros and scripts for building kernel module packages.

%prep
# Not strictly necessary but allows working on file names instead
# of source numbers in install section
%setup -c -T
cp -p %{sources} .


%build
# nothing to do


%install
mkdir -p %{buildroot}/%{_rpmconfigdir}/macros.d
install -p -m 0644 -t %{buildroot}/%{_rpmconfigdir}/macros.d macros.kernel-srpm
%if 0%{?rhel} >= 8
  sed -i 's/^%%kernel_arches.*/%%kernel_arches x86_64 s390x ppc64le aarch64/' \
    %{buildroot}/%{_rpmconfigdir}/macros.d/macros.kernel-srpm
%endif

mkdir -p %{buildroot}%{rrcdir}/find-provides.d
mkdir -p %{buildroot}%{_fileattrsdir}
install -p -m 755 -t %{buildroot}%{rrcdir} kmodtool rpmsort symset-table
install -p -m 755 -t %{buildroot}%{rrcdir} find-provides.ksyms find-requires.ksyms
install -p -m 755 -t %{buildroot}%{rrcdir}/find-provides.d firmware.prov modalias.prov
install -p -m 755 -t %{buildroot}%{rrcdir} brp-kmod-restore-perms brp-kmod-set-exec-bit
install -p -m 644 -t %{buildroot}%{_rpmconfigdir}/macros.d macros.kmp
install -p -m 644 -t %{buildroot}%{_fileattrsdir} kmod.attr

install -p -m 644 -t "%{buildroot}%{_fileattrsdir}" kabi.attr
install -p -m 755 -t "%{buildroot}%{_rpmconfigdir}" kabi.sh

install -p -m 644 -t "%{buildroot}%{_fileattrsdir}" provided_ksyms.attr required_ksyms.attr
install -p -m 644 -t "%{buildroot}%{_fileattrsdir}" modalias.attr

%files
%{_rpmconfigdir}/macros.d/macros.kernel-srpm
%{_rpmconfigdir}/macros.d/macros.kmp
%{_fileattrsdir}/kmod.attr
%{rrcdir}/kmodtool
%{rrcdir}/rpmsort

%files -n kernel-rpm-macros
%{_rpmconfigdir}/kabi.sh
%{_fileattrsdir}/kabi.attr
%{_fileattrsdir}/modalias.attr
%{_fileattrsdir}/provided_ksyms.attr
%{_fileattrsdir}/required_ksyms.attr
%dir %{rrcdir}/find-provides.d
%{rrcdir}/brp-kmod-restore-perms
%{rrcdir}/brp-kmod-set-exec-bit
%{rrcdir}/symset-table
%{rrcdir}/find-provides.ksyms
%{rrcdir}/find-requires.ksyms
%{rrcdir}/find-provides.d/firmware.prov
%{rrcdir}/find-provides.d/modalias.prov

%changelog
* Mon Jun 12 2023 Eugene Syromiatnikov <esyr@redhat.com> - 1.0-13
- Handle symvers.xz in kabi.attr (#2209253).
- Fix indirect __crc_* sumbols parsing in find-provides.ksyms
  and find-requires.ksyms to avoid matching multiple sections
  producing bogus duplicate provides for kmods that have both __kcrctab
  and __kcrctab_gpl sections (#2115811, #2178935).
- Call "readelf -R" on a correct section in find-requires.ksyms.
- Rewrite section data extraction in find-provides.ksyms and find-requires.ksyms
  to avoid garbage at the end of extracted sections, causing unnecessary awk
  complaints (#2115811).
- Perform section parsing inside the awk script in find-provides.ksyms
  and find-requires.ksyms to avoid hitting command line argument limit
  when handling large .rodata sections (#2178935).

* Tue Jan 31 2023 Eugene Syromiatnikov <esyr@redhat.com> - 1.0-12
- Support storing of __crc_* symbols in sections other than .rodata.
- Resolves: #2135047

* Thu Feb 17 2022 Eugene Syromiatnikov <esyr@redhat.com> - 1.0-11
- Work around a change in type of __crc_* symbols for some kmods printed by nm
  on ppc64le and s390x
- Resolves: #2055464

* Thu Nov 18 2021 Eugene Syromiatnikov <esyr@redhat.com> - 1.0-10
- Add conflicts of kernel-srpm-macros with kernel-rpm-macros < 185-9
  as macros.kmp, kmodtool, and rpmsort were moved from the latter
  to the former.

* Mon Sep 20 2021 Eugene Syromiatnikov <esyr@redhat.com> - 1.0-9
- Update scripts with RHEL-specific changes.

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.0-8
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue May 25 2021 Michal Domonkos <mdomonko@redhat.com> - 1.0-7
- Bump release for a rebuild in a sidetag

* Wed May 12 2021 Michal Domonkos <mdomonko@redhat.com> - 1.0-6
- Adopt kernel-rpm-macros subpackage & kmod.attr from redhat-rpm-config
- Resolves: #1959914

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.0-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Aug 04 2020 Merlin Mathesius <mmathesi@redhat.com> - 1.0-3
- Escape percent for %%kernel_arches macro

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 21 2020 Troy Dawson <tdawson@redhat.com> - 1.0-1
- Initial build

