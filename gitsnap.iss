[Setup]
AppName=Gitsnap
AppVersion=1.0
DefaultDirName={autopf}\Gitsnap
DefaultGroupName=Gitsnap
OutputDir=Output
OutputBaseFilename=Gitsnap_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=compiler:SetupClassicIcon.ico

[Files]
Source: "dist\gitsnap.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Gitsnap"; Filename: "{app}\gitsnap.exe"
Name: "{autodesktop}\Gitsnap"; Filename: "{app}\gitsnap.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\gitsnap.exe"; Description: "Launch Gitsnap"; Flags: nowait postinstall skipifsilent
