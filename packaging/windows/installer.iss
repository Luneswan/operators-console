; Inno Setup script for Operator's Console.
; Build with:  iscc /DAppVersion=1.0.0 packaging\windows\installer.iss
; Produces a per-user installer, so no administrator prompt is needed.

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#define AppName "Operator's Console"
#define AppId "operators-console"
#define AppExe "operators-console.exe"
#define SourceDir "..\..\dist\operators-console"

[Setup]
AppId={{7C4B1E52-3D7A-4C1F-9B36-2E5F0A9D41C8}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=no
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename={#AppId}-{#AppVersion}-windows-setup
SetupIconFile=..\icons\operators-console.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
MinVersion=10.0
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Always created, including on a silent install or an in-app update.
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "Start {#AppName}"; Flags: nowait postinstall skipifsilent

; Progress lives in %APPDATA%, so an uninstall never destroys the user's work.
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
