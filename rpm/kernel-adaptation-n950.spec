Name:       kernel-adaptation-n950
Summary:    Kernel Adaptation for n950
Version:    2.6.32.20130129.1
Release:    1
Group:      Kernel/Linux Kernel
License:    GPLv2
URL:        https://github.com/nemomobile/kernel-adaptation-n950-n9
Source0:    %{name}-%{version}.tar.bz2
Source1:    kernel-adaptation-n950.config
Source2:    kernel-adaptation-n950.cmdline
Source3:  kernel-adaptation-n950.spec.tpl
Source4:  generate-spec.sh
Source5:  kernel-adaptation-n950-debug.config
Source6:  README

BuildRequires:  pkgconfig(ncurses)
BuildRequires: module-init-tools
BuildRequires:  mer-kernel-checks
BuildRequires:  perl
BuildRequires:  kmod >= 9
BuildRequires:  fdupes
Provides:   kernel = %{version}
Conflicts: kernel-adaptation-n950-debug
%description
Kernel for n950.

%define kernel_version_build %{version}-n950
%define kernel_devel_dir %{_prefix}/src/linux-%{kernel_version_build}

%define package_dir %{name}-%{version}
%define modules_dir %{buildroot}/lib/modules/%{kernel_version_build}
%define builds_uImage 0
%define builds_vmlinuz 1
%define kernel_arch %{_arch}


%package devel
Summary:    Devel files for n950 kernel
Group:      Development/System
Requires:   %{name} = %{version}-%{release}
Provides:   kernel-devel = %{version}

%description devel
Devel for n950 kernel

%prep
%setup -q -n %{package_dir}


#cp %{SOURCE1} ./.config
cp arch/arm/configs/n9_mer_defconfig .config
# make sure EXTRAVERSION says what we want it to say
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = .20130129.1-n950/" Makefile

# Verify this spec is using the latest template version
/usr/bin/mer_verify_kernel_spec 1 --fatal-if-old

# Verify the config meets the current Mer requirements
/usr/bin/mer_verify_kernel_config .config

echo The target hw is n950
echo The desc is %{summary}

# << setup

%build
# >> build pre

# arm/mips: uImage
# others  : bzImage
%if 0%{?builds_uImage}
make %{?jobs:-j%jobs} uImage
%endif

%if 0%{?builds_vmlinuz}
make %{?jobs:-j%jobs} bzImage
%endif

make %{?jobs:-j%jobs} modules

# << build pre



# >> build post
# << build post

%install
rm -rf %{buildroot}
# >> install pre

# Modules
# Consider : INSTALL_MOD_STRIP
mkdir -p %{modules_dir}/
make INSTALL_MOD_STRIP=1 INSTALL_MOD_PATH=%{buildroot} modules_install
touch %{modules_dir}/modules.dep

# /boot
mkdir -p %{buildroot}/boot/
make INSTALL_PATH=%{buildroot}/boot/ install

%if 0%{?builds_uImage}
install -m 755 arch/%{kernel_arch}/boot/uImage %{buildroot}/boot/
%endif

%if 0%{?builds_vmlinuz}
install -m 755 arch/%{kernel_arch}/boot/zImage %{buildroot}/boot/vmlinuz-%{kernel_version_build}
%endif

install -m 644 .config %{buildroot}/boot/config-%{kernel_version_build}
install -m 600 System.map %{buildroot}/boot/System.map-%{kernel_version_build}

# And save the headers/makefiles etc for building modules against
#
# This all looks scary, but the end result is supposed to be:
# * all arch relevant include/ files
# * all Makefile/Kconfig files
# * all script/ files

mkdir -p %{buildroot}/%{kernel_devel_dir}

# dirs for additional modules per module-init-tools, kbuild/modules.txt
# first copy everything
cp --parents $(find  -type f -name "Makefile*" -o -name "Kconfig*") %{buildroot}/%{kernel_devel_dir}
cp Module.symvers %{buildroot}/%{kernel_devel_dir}
cp System.map %{buildroot}/%{kernel_devel_dir}
if [ -s Module.markers ]; then
cp Module.markers %{buildroot}/%{kernel_devel_dir}
fi
# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}/%{kernel_devel_dir}/Documentation
rm -rf %{buildroot}/%{kernel_devel_dir}/scripts
rm -rf %{buildroot}/%{kernel_devel_dir}/include

# Copy all scripts
cp .config %{buildroot}/%{kernel_devel_dir}
cp -a scripts %{buildroot}/%{kernel_devel_dir}
if [ -d arch/%{kernel_arch}/scripts ]; then
cp -a arch/%{kernel_arch}/scripts %{buildroot}/%{kernel_devel_dir}/arch/%{kernel_arch}
fi
# FIXME - what's this trying to do ... if *lds expands to multiple files the -f test will fail.
if [ -f arch/%{kernel_arch}/*lds ]; then
cp -a arch/%{kernel_arch}/*lds %{buildroot}/%{kernel_devel_dir}/arch/%{kernel_arch}/
fi
# Clean any .o files from the 'scripts'
find %{buildroot}/%{kernel_devel_dir}/scripts/ -name \*.o -print0 | xargs -0 rm -f

# arch-specific include files
cp -a --parents arch/%{kernel_arch}/include %{buildroot}/%{kernel_devel_dir}

# arm has include files under plat- and mach- areas (x86/mips don't)
%if "%{?kernel_arch}" == "arm"
cp -a --parents arch/%{kernel_arch}/mach-*/include %{buildroot}/%{kernel_devel_dir}
cp -a --parents arch/%{kernel_arch}/plat-*/include %{buildroot}/%{kernel_devel_dir}
%endif

# normal include files
mkdir -p %{buildroot}/%{kernel_devel_dir}/include

# copy only include/* directories
cp -a $(find include -mindepth 1 -maxdepth 1 -type d) %{buildroot}/%{kernel_devel_dir}/include

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built. Also .conf
touch -r %{buildroot}/%{kernel_devel_dir}/Makefile %{buildroot}/%{kernel_devel_dir}/include/linux/version.h
touch -r %{buildroot}/%{kernel_devel_dir}/.config %{buildroot}/%{kernel_devel_dir}/include/linux/autoconf.h

# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
cp %{buildroot}/%{kernel_devel_dir}/.config %{buildroot}/%{kernel_devel_dir}/include/config/auto.conf

# We don't want this to be in the image.
rm -f %{buildroot}/boot/vmlinux-*

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version_build} -name "*.ko" -type f -exec chmod u+x {} \;
# << install pre

# >> install post
# HACKS
chmod 644 %{buildroot}%{kernel_devel_dir}/arch/arm/plat-omap/include/plat/dma.h
find %{buildroot}%{kernel_devel_dir}/ -name '.gitignore' -delete
find %{buildroot}%{kernel_devel_dir}/ -name '.*.cmd' -delete

cp %{SOURCE2} %{buildroot}/boot/cmdline-%{kernel_version_build}
ln -s cmdline-%{kernel_version_build} %{buildroot}/boot/cmdline
ln -s vmlinuz-%{kernel_version_build} %{buildroot}/boot/bzImage
ln -s System.map-%{kernel_version_build} %{buildroot}/boot/System.map

# << install post

%fdupes  %{buildroot}%{kernel_devel_dir}/

%files
%defattr(-,root,root,-)
/lib/modules/%{kernel_version_build}/*
/boot/System.map-%{kernel_version_build}
/boot/config-%{kernel_version_build}
# >> files

# do we need this? should it be versioned only for x86
/boot/System.map

%if 0%{?builds_vmlinuz}
/boot/vmlinuz-%{kernel_version_build}
/boot/bzImage
/boot/cmdline-%{kernel_version_build}
/boot/cmdline
%endif

%if 0%{?builds_uImage}
/boot/uImage
%endif

%if 0%{?builds_firmware}
/lib/firmware/*
%endif
# << files

%files devel
%defattr(-,root,root,-)
%{kernel_devel_dir}/*
%{kernel_devel_dir}/.config
# >> files devel
# << files devel
