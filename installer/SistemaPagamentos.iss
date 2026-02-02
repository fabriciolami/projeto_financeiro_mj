#define MyAppName "SistemaPagamentos"
#define MyAppVersion "1.0.1"
#define MyAppExeName "SistemaPagamentos.exe"

[Setup]
AppId={{A9B9E2E4-1234-4F88-9C88-123456789ABC}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Marmoraria Jardim
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=setup_SistemaPagamentos
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
PrivilegesRequired=admin

[Files]
Source: "..\dist\SistemaPagamentos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SistemaPagamentos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: onlyifdoesntexist


[Icons]
Name: "{group}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"
Name: "{autodesktop}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"

[Run]
Filename: "{app}\SistemaPagamentos.exe"; Description: "Abrir SistemaPagamentos"; Flags: nowait postinstall skipifsilent
