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
ArchitecturesInstallIn64BitMode=x64os
DisableProgramGroupPage=yes
PrivilegesRequired=admin

[Files]
; EXE principal
Source: "..\dist\SistemaPagamentos.exe"; DestDir: "{app}"; Flags: ignoreversion

; .env de exemplo (cria apenas na primeira instalacao)
Source: ".env.example"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist


[Icons]
Name: "{group}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"
Name: "{autodesktop}\SistemaPagamentos"; Filename: "{app}\SistemaPagamentos.exe"

[Run]
Filename: "{app}\SistemaPagamentos.exe"; Description: "Abrir SistemaPagamentos"; Flags: nowait postinstall skipifsilent
