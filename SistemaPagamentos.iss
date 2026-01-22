#define MyAppName "Projeto Financeiro MJ"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Marmoraria Jardim"
#define MyAppURL "https://github.com/fabriciolami/projeto_financeiro_mj"
#define MyAppExeName "SistemaPagamentos.exe"

[Setup]
AppId={{362111E4-8497-4B73-8534-931ADE4611DC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\ProjetoFinanceiroMJ
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
SolidCompression=yes
WizardStyle=modern
OutputDir=Output
OutputBaseFilename=ProjetoFinanceiroMJ_Setup_{#MyAppVersion}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
