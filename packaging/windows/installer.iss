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
; An in-app update runs this installer from inside the app it replaces.
; Builds before 1.1.0 run it while their own updater still holds
; operators-console.exe open, and that updater has no window, so the default
; graceful close cannot reach it. "force" lets the Restart Manager end
; whatever holds these files; the app is reopened below, not by Windows.
CloseApplications=force
CloseApplicationsFilter=*.exe,*.dll,*.pyd
RestartApplications=no
; Every install leaves a log in %TEMP%, so an update that fails in the field
; can be diagnosed from something other than a guess.
SetupLogging=yes

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
; A silent run is an in-app update. The updater that ran it may have been
; closed above, so the installer opens the new version itself - unless the
; updater says it will (/NORELAUNCH, which builds from 1.1.0 pass).
Filename: "{app}\{#AppExe}"; Flags: nowait; Check: RelaunchAfterUpdate

; Progress lives in %APPDATA%, so an uninstall never destroys the user's work.
[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function CmdLineHas(const Name: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), Name) = 0 then
    begin
      Result := True;
      Exit;
    end;
end;

function RelaunchAfterUpdate: Boolean;
begin
  Result := WizardSilent and not CmdLineHas('/NORELAUNCH');
end;
