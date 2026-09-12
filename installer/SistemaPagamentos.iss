#define MyAppName "SistemaPagamentos"
#define MyAppVersion "1.0.7"
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
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
DisableProgramGroupPage=yes
PrivilegesRequired=admin

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "..\dist\SistemaPagamentos.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"
Name: "{autodesktop}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"

[Run]
Filename: "{app}\SistemaPagamentos.exe"; Description: "Abrir SistemaPagamentos"; Flags: nowait postinstall skipifsilent
