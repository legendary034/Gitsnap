[Setup]
AppName=Gitsnap
AppVersion=1.1
DefaultDirName={autopf}\Gitsnap
DefaultGroupName=Gitsnap
OutputDir=installer
OutputBaseFilename=Gitsnap_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=gitsnap_icon.ico
UninstallDisplayIcon={app}\gitsnap.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Start Gitsnap automatically when Windows starts"; GroupDescription: "Startup Options:"

[Files]
Source: "dist\gitsnap.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Gitsnap"; Filename: "{app}\gitsnap.exe"
Name: "{autodesktop}\Gitsnap"; Filename: "{app}\gitsnap.exe"; Tasks: desktopicon
Name: "{userstartup}\Gitsnap"; Filename: "{app}\gitsnap.exe"; Tasks: startupicon

[Run]
Filename: "{app}\gitsnap.exe"; Description: "{cm:LaunchProgram,Gitsnap}"; Flags: nowait postinstall skipifsilent
