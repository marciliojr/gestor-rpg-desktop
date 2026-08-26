Name:           gestor-rpg
Version:        1.0.0
Release:        1%{?dist}
Summary:        Gestor desktop para mestrar RPG
License:        LicenseRef-NOASSERTION
URL:            https://github.com/marciliojr/gestor-rpg-desktop
BuildArch:      x86_64

%description
Aplicativo desktop para mestrar RPG com 3D&T Victory e D&D 5e: campanhas,
fichas, documentos, monstros, combate com grid e log de sessão.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/gestor-rpg
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps
cp -a %{_sourcedir}/dist/gestor-rpg/. %{buildroot}/opt/gestor-rpg/
ln -s /opt/gestor-rpg/gestor-rpg %{buildroot}/usr/bin/gestor-rpg
install -m 0644 %{_sourcedir}/packaging/gestor-rpg.desktop %{buildroot}/usr/share/applications/gestor-rpg.desktop
install -m 0644 %{_sourcedir}/src/gestor_rpg/resources/gestor-rpg.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/gestor-rpg.svg

%files
/opt/gestor-rpg
/usr/bin/gestor-rpg
/usr/share/applications/gestor-rpg.desktop
/usr/share/icons/hicolor/scalable/apps/gestor-rpg.svg

%changelog
* Wed Aug 26 2026 Gestor RPG <gestor-rpg@localhost> - 1.0.0-1
- Primeira versão estável (1.0): nav agrupada, ajuda, PDF da campanha.

* Tue Aug 25 2026 Gestor RPG <gestor-rpg@localhost> - 0.1.0-1
- Empacote inicial com binário congelado e atalho no menu.
