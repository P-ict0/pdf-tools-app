; Define application constants
#define MyAppName "PDF Tools"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppPublisher "P-ict0"
#define MyAppURL "https://github.com/P-ict0/pdf-tools-app"

[Setup]
AppId={{98AAE78F-AF6E-44B1-99A1-3C5180C9867A}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
CreateAppDir=yes
DefaultDirName={commonpf}\{#MyAppName}
LicenseFile=..\LICENSE
PrivilegesRequired=admin
OutputBaseFilename=pdf_tools_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\pdf_tools_windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include the VERSION file
Source: "..\VERSION"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\pdf_tools_windows.exe"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\pdf_tools_windows.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
