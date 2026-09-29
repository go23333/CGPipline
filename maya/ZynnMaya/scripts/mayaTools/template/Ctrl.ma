//Maya ASCII 2023 scene
//Name: Ctrl.ma
//Last modified: Tue, Feb 03, 2026 05:03:37 PM
//Codeset: 936
requires maya "2023";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2023";
fileInfo "version" "2023";
fileInfo "cutIdentifier" "202211021031-847a9f9623";
fileInfo "osv" "Windows 10 Pro v2009 (Build: 19045)";
fileInfo "UUID" "63A6ECB3-44A5-646E-11B3-F4A590781CA5";
createNode transform -s -n "persp";
	rename -uid "FA8A4080-41F7-1969-C0FC-1990FC447A70";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -0.60097612178457582 5.1375959897755896 34.235140797029779 ;
	setAttr ".r" -type "double3" -11.138352729605309 -3.8000000000002343 4.9805666234319189e-17 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "60D3AD08-4D06-051B-85CB-3FA9BEFB23C1";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 35.637487954470046;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" -1.1950168609619141 -4.7800674438476562 0 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "A0DB9E08-44CA-77F8-BCC6-4788FFB462E5";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "8C089014-4133-D243-DC74-5C920DC835F0";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "E8DEC8CC-49EF-5B54-11C3-BA92FEA67634";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 45.069077088830511 174.50432070109861 1016.2544877585466 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "C551AB12-427F-440C-9BDB-A9B4E280801F";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1013.4628722724016;
	setAttr ".ow" 37.245993286117745;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".tp" -type "double3" 45.069077088830511 174.50432070109861 2.7916154861450195 ;
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "1147ABB1-47C2-1313-7C16-C091CDA58235";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "A85B739E-477A-9B47-C5D9-1888D87A3A9B";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "ctrlBox";
	rename -uid "E2494B20-4698-D18E-58CE-0EB4A7745539";
	addAttr -ci true -sn "limits" -ln "limits" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "ACtrlVis" -ln "ACtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "BCtrlVis" -ln "BCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "CCtrlVis" -ln "CCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "EyeCtrlVis" -ln "EyeCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "AimCtrlVis" -ln "AimCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "TeethCtrlVis" -ln "TeethCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "TongueCtrlVis" -ln "TongueCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "RegionsCtrlVis" -ln "RegionsCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "UpMidLoCtrlVis" -ln "UpMidLoCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "SquashCtrlVis" -ln "SquashCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "CustomCtrlVis" -ln "CustomCtrlVis" -dv 1 -min 0 -max 1 -at "bool";
	setAttr -k off -cb on ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr -k off -cb on ".tx";
	setAttr -k off -cb on ".ty";
	setAttr -k off -cb on ".tz";
	setAttr -k off -cb on ".rx";
	setAttr -k off -cb on ".ry";
	setAttr -k off -cb on ".rz";
	setAttr -k off -cb on ".sx";
	setAttr -k off -cb on ".sy";
	setAttr -k off -cb on ".sz";
	setAttr -cb on ".limits";
	setAttr -cb on ".ACtrlVis";
	setAttr -cb on ".BCtrlVis";
	setAttr -cb on ".CCtrlVis";
	setAttr -cb on ".EyeCtrlVis" no;
	setAttr -cb on ".AimCtrlVis";
	setAttr -cb on ".TeethCtrlVis";
	setAttr -cb on ".TongueCtrlVis";
	setAttr -cb on ".RegionsCtrlVis" no;
	setAttr -cb on ".UpMidLoCtrlVis";
	setAttr -cb on ".SquashCtrlVis";
	setAttr -cb on ".CustomCtrlVis";
createNode nurbsCurve -n "ctrlBoxShape" -p "ctrlBox";
	rename -uid "1FC1427B-46DB-9D8F-5997-C4B26FE4445A";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-2.3900337219238281 4.7800674438476562 0
		2.3900337219238281 4.7800674438476562 0
		2.3900337219238281 -6.6920944213867184 0
		-2.3900337219238281 -6.6920944213867184 0
		-2.3900337219238281 4.7800674438476562 0
		;
createNode transform -n "ctrlBoxBrow_R" -p "ctrlBox";
	rename -uid "54CD08D9-4618-3ABB-018D-A3A94B8E6793";
	setAttr ".t" -type "double3" -1.1950168609619141 3.5850505828857422 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxBrow_RShape" -p "ctrlBoxBrow_R";
	rename -uid "6904A574-4AC2-F988-EEEA-7F9235167DFF";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlBrow_R" -p "ctrlBoxBrow_R";
	rename -uid "E8D176F5-4B5C-E07E-F4B1-5AA464CC5326";
	addAttr -ci true -k true -sn "squeeze" -ln "squeeze" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "outerUpDown" -ln "outerUpDown" -smn 0 -smx 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlBrow_RShape" -p "ctrlBrow_R";
	rename -uid "A62A71E8-450C-FAB5-83DB-7897230A9E27";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxBrow_L" -p "ctrlBox";
	rename -uid "F6214FF1-4B89-3159-A7EE-5FBEC84CEAF1";
	setAttr ".t" -type "double3" 1.1950168609619141 3.5850505828857422 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxBrow_LShape" -p "ctrlBoxBrow_L";
	rename -uid "1E417CB7-406F-57B7-458A-218487CF4632";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlBrow_L" -p "ctrlBoxBrow_L";
	rename -uid "1CCEB119-4A4B-6FA2-5C8A-DC9A046A8CDA";
	addAttr -ci true -k true -sn "squeeze" -ln "squeeze" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "outerUpDown" -ln "outerUpDown" -smn 0 -smx 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlBrow_LShape" -p "ctrlBrow_L";
	rename -uid "32C99CA5-4DD6-53FF-4EBA-EDA6CC9ECF6F";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxEye_R" -p "ctrlBox";
	rename -uid "A07945E7-44A5-E103-4F12-EE9974EC2550";
	setAttr ".t" -type "double3" -1.1950168609619141 1.8164256811141968 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxEye_RShape" -p "ctrlBoxEye_R";
	rename -uid "A67FF036-4854-2D59-BE46-DE804760048F";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlEye_R" -p "ctrlBoxEye_R";
	rename -uid "40D46D4E-4DB9-0DEA-E8C9-7890E56AE761";
	addAttr -ci true -k true -sn "iris" -ln "iris" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "pupil" -ln "pupil" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "wide" -ln "wide" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "blink" -ln "blink" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "squint" -ln "squint" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "upperLid" -ln "upperLid" -nn "Upper Lid" -min -10 -max 10 
		-at "double";
	addAttr -ci true -sn "S_S" -ln "S_S" -nn "上闭眼上幅度调整" -dv -0.02 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "S_X" -ln "S_X" -nn "上闭眼下幅度调整" -dv -0.065 -min -10 
		-max 10 -at "double";
	addAttr -ci true -sn "X_S" -ln "X_S" -nn "下闭眼上幅度调整" -dv 0.07 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "X_X" -ln "X_X" -nn "下闭眼下幅度调整" -dv 0.03 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "lowerLid" -ln "lowerLid" -nn "Lower Lid" -min -10 -max 10 
		-at "double";
	addAttr -ci true -sn "blinkCenter" -ln "blinkCenter" -nn "Blink Center" -min 0 -max 
		10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
	setAttr -k on ".upperLid";
	setAttr -l on ".S_S";
	setAttr -l on ".S_X" -0.086;
	setAttr -l on ".X_S" 0.084;
	setAttr -l on ".X_X";
	setAttr -k on ".lowerLid";
	setAttr -k on ".blinkCenter";
createNode nurbsCurve -n "ctrlEye_RShape" -p "ctrlEye_R";
	rename -uid "9266B3EF-4A2B-C2F2-76E2-92845F4185EF";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxEye_L" -p "ctrlBox";
	rename -uid "78FC8CF1-47AE-116D-2D30-648B9A3FDD85";
	setAttr ".t" -type "double3" 1.1950168609619141 1.8164256811141968 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxEye_LShape" -p "ctrlBoxEye_L";
	rename -uid "3918C831-4B96-0798-2095-3FAA17522465";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlEye_L" -p "ctrlBoxEye_L";
	rename -uid "7306F7EC-4A30-6058-8DA3-E89610DBAC5D";
	addAttr -ci true -k true -sn "iris" -ln "iris" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "pupil" -ln "pupil" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "wide" -ln "wide" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "blink" -ln "blink" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "squint" -ln "squint" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "upperLid" -ln "upperLid" -nn "Upper Lid" -min -10 -max 10 
		-at "double";
	addAttr -ci true -sn "S_S" -ln "S_S" -nn "上闭眼上幅度调整" -dv -0.02 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "S_X" -ln "S_X" -nn "上闭眼下幅度调整" -dv -0.065 -min -10 
		-max 10 -at "double";
	addAttr -ci true -sn "X_S" -ln "X_S" -nn "下闭眼上幅度调整" -dv 0.07 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "X_X" -ln "X_X" -nn "下闭眼下幅度调整" -dv 0.03 -min -10 -max 
		10 -at "double";
	addAttr -ci true -sn "lowerLid" -ln "lowerLid" -nn "Lower Lid" -min -10 -max 10 
		-at "double";
	addAttr -ci true -sn "blinkCenter" -ln "blinkCenter" -nn "Blink Center" -min 0 -max 
		10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
	setAttr -k on ".upperLid";
	setAttr -l on ".S_S";
	setAttr -l on ".S_X" -0.086;
	setAttr -l on ".X_S" 0.084;
	setAttr -l on ".X_X";
	setAttr -k on ".lowerLid";
	setAttr -k on ".blinkCenter";
createNode nurbsCurve -n "ctrlEye_LShape" -p "ctrlEye_L";
	rename -uid "8D9EFDA7-4739-18ED-C597-9D930502D1D4";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxCheek_R" -p "ctrlBox";
	rename -uid "2E8A5CAA-4231-54C6-E0F0-66AEEAF6DAE7";
	setAttr ".t" -type "double3" -1.1950168609619141 0 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxCheek_RShape" -p "ctrlBoxCheek_R";
	rename -uid "B6DD4202-47B5-720D-36B9-489E560B14FC";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 0 0
		-1 0 0
		-1 1 0
		;
createNode transform -n "ctrlCheek_R" -p "ctrlBoxCheek_R";
	rename -uid "09540C4C-435A-0C66-8ACB-22BB5DAA848C";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 0 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlCheek_RShape" -p "ctrlCheek_R";
	rename -uid "16F0D836-44C8-D75A-1556-AC903BB6A432";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxCheek_L" -p "ctrlBox";
	rename -uid "EA8A7E53-4B8C-60EB-4CBD-8AA0CEC111C4";
	setAttr ".t" -type "double3" 1.1950168609619141 0 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxCheek_LShape" -p "ctrlBoxCheek_L";
	rename -uid "601A6DE6-474B-CE5D-2F62-3BBA4C1E253B";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 0 0
		-1 0 0
		-1 1 0
		;
createNode transform -n "ctrlCheek_L" -p "ctrlBoxCheek_L";
	rename -uid "A14B63BD-4EE2-AC24-10EF-A5AA8AEEDC23";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 0 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlCheek_LShape" -p "ctrlCheek_L";
	rename -uid "1A14CF09-4B4D-DB76-E2EB-FC9310474A66";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxNose_R" -p "ctrlBox";
	rename -uid "AF7AADAF-4DC8-DE4C-091B-14B59EEC0902";
	setAttr ".t" -type "double3" -1.1950168609619141 -1.0516148805618286 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxNose_RShape" -p "ctrlBoxNose_R";
	rename -uid "4474CFE1-411C-5DDD-0803-B6AFC3F4980A";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 0 0
		-1 0 0
		-1 1 0
		;
createNode transform -n "ctrlNose_R" -p "ctrlBoxNose_R";
	rename -uid "F898B272-4B4C-53D8-46B0-AC99892FC741";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 0 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlNose_RShape" -p "ctrlNose_R";
	rename -uid "AB07E994-4EA6-4EA2-99BC-798D61FF82AB";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxNose_L" -p "ctrlBox";
	rename -uid "F425935F-4B76-0B20-1BD0-179BE392D174";
	setAttr ".t" -type "double3" 1.1950168609619141 -1.0516148805618286 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxNose_LShape" -p "ctrlBoxNose_L";
	rename -uid "7FCF1E18-48AD-A678-BBEA-189E0612ED88";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 0 0
		-1 0 0
		-1 1 0
		;
createNode transform -n "ctrlNose_L" -p "ctrlBoxNose_L";
	rename -uid "5BB01410-47F3-1913-1CD8-CEA7B22AFCAC";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 0 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlNose_LShape" -p "ctrlNose_L";
	rename -uid "F3C49694-4671-59FA-446D-0DBAA3CFC412";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxLips_M" -p "ctrlBox";
	rename -uid "95DCDD7F-499B-FE65-6758-3581B2400EEB";
	setAttr ".t" -type "double3" 0 -2.0076284408569336 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxLips_MShape" -p "ctrlBoxLips_M";
	rename -uid "DAB93031-430E-2D33-C19A-879BFC9C921D";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlLips_M" -p "ctrlBoxLips_M";
	rename -uid "BF05982F-45CB-630E-6E36-03B15B5152F4";
	addAttr -ci true -k true -sn "upperPress" -ln "upperPress" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "lowerPress" -ln "lowerPress" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "upperSqueeze" -ln "upperSqueeze" -smn -10 -smx 10 
		-at "double";
	addAttr -ci true -k true -sn "lowerSqueeze" -ln "lowerSqueeze" -smn -10 -smx 10 
		-at "double";
	addAttr -ci true -k true -sn "upperRoll" -ln "upperRoll" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "lowerRoll" -ln "lowerRoll" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "upperPucker" -ln "upperPucker" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "lowerPucker" -ln "lowerPucker" -smn -10 -smx 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlLips_MShape" -p "ctrlLips_M";
	rename -uid "A26374F3-45C9-5D4E-A465-A78A2BADD147";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxMouth_M" -p "ctrlBox";
	rename -uid "D3864028-4CBC-92A0-8975-E9B6A3E85967";
	setAttr ".t" -type "double3" 0 -3.0592432022094727 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxMouth_MShape" -p "ctrlBoxMouth_M";
	rename -uid "5E77EC53-4816-538F-E57D-048577059BC0";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.99999999999999822 0 0
		1.0000000000000018 0 0
		1 -1 0
		-1 -1 0
		-0.99999999999999822 0 0
		;
createNode transform -n "ctrlMouth_M" -p "ctrlBoxMouth_M";
	rename -uid "282ADEA0-4466-9246-9E34-8AA3DA9A8F8A";
	addAttr -ci true -k true -sn "jawForward" -ln "jawForward" -smn -10 -smx 10 -at "double";
	addAttr -ci true -k true -sn "jawSide" -ln "jawSide" -smn -10 -smx 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 0 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
createNode nurbsCurve -n "ctrlMouth_MShape" -p "ctrlMouth_M";
	rename -uid "1E7DBA4F-439F-F70C-9A5E-D680C0F6B8BE";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxMouthCorner_R" -p "ctrlBox";
	rename -uid "09A8DF10-46B7-0CA8-A777-1DBE1950124B";
	setAttr ".t" -type "double3" -1.1950168609619141 -4.7800674438476562 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxMouthCorner_RShape" -p "ctrlBoxMouthCorner_R";
	rename -uid "31A36F6D-4762-01CF-0DA0-C2849444B2BA";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlMouthCorner_R" -p "ctrlBoxMouthCorner_R";
	rename -uid "637C9FF4-4457-E8E8-3A5D-739D5AEEEC54";
	addAttr -ci true -sn "smile" -ln "smile" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "smileMaxValue" -ln "smileMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "frown" -ln "frown" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "frownMaxValue" -ln "frownMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "narrowSmile" -ln "narrowSmile" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "narrowSmileMaxValue" -ln "narrowSmileMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "narrowFrown" -ln "narrowFrown" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "narrowFrownMaxValue" -ln "narrowFrownMaxValue" -dv 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
	setAttr -cb on ".smile" 10;
	setAttr -cb on ".frown";
	setAttr -cb on ".narrowSmile" 1.4747525453567505;
	setAttr -cb on ".narrowFrown";
createNode nurbsCurve -n "ctrlMouthCorner_RShape" -p "ctrlMouthCorner_R";
	rename -uid "6F9DCC60-4C42-0D2F-4FF0-0C831AA62F7F";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxMouthCorner_L" -p "ctrlBox";
	rename -uid "27320F30-4DF8-6971-E0B7-DDB1A0EEC06F";
	setAttr ".t" -type "double3" 1.1950168609619141 -4.7800674438476562 0 ;
	setAttr ".s" -type "double3" 0.79667790730794275 0.79667790730794275 0.79667790730794275 ;
createNode nurbsCurve -n "ctrlBoxMouthCorner_LShape" -p "ctrlBoxMouthCorner_L";
	rename -uid "C9DA68AB-43EE-D35E-B330-F0B3A76C7A53";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlMouthCorner_L" -p "ctrlBoxMouthCorner_L";
	rename -uid "D437169E-4524-D26D-AC8A-6AA21704D4FE";
	addAttr -ci true -sn "smile" -ln "smile" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "smileMaxValue" -ln "smileMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "frown" -ln "frown" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "frownMaxValue" -ln "frownMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "narrowSmile" -ln "narrowSmile" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "narrowSmileMaxValue" -ln "narrowSmileMaxValue" -dv 10 -at "double";
	addAttr -ci true -sn "narrowFrown" -ln "narrowFrown" -smn 0 -smx 1 -at "double";
	addAttr -ci true -sn "narrowFrownMaxValue" -ln "narrowFrownMaxValue" -dv 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".mntl" -type "double3" -1 -1 0 ;
	setAttr ".mxtl" -type "double3" 1 1 0 ;
	setAttr ".mtze" yes;
	setAttr ".xtze" yes;
	setAttr -cb on ".smile" 10;
	setAttr -cb on ".frown";
	setAttr -cb on ".narrowSmile" 1.4747525453567505;
	setAttr -cb on ".narrowFrown";
createNode nurbsCurve -n "ctrlMouthCorner_LShape" -p "ctrlMouthCorner_L";
	rename -uid "9A357520-49DB-71A9-D479-6DA8160A1F41";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-0.28284271247461901 -2.7755575615628914e-17 0
		-2.7755575615628914e-17 0.28284271247461901 0
		0.28284271247461901 2.7755575615628914e-17 0
		2.7755575615628914e-17 -0.28284271247461901 0
		-0.28284271247461901 -2.7755575615628914e-17 0
		;
createNode transform -n "ctrlBoxPhonemes_M" -p "ctrlBox";
	rename -uid "2CC6524B-4E42-59D0-BB29-2C9BDE3603FF";
	setAttr ".t" -type "double3" -0.76481079101562499 -6.2140876770019533 0 ;
	setAttr ".s" -type "double3" 0.28970105720288825 0.28970105720288825 0.28970105720288825 ;
createNode nurbsCurve -n "ctrlBoxPhonemes_MShape" -p "ctrlBoxPhonemes_M";
	rename -uid "892C17CE-4FA7-E6FF-8A86-8E8E2971E642";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlPhonemes_M" -p "ctrlBoxPhonemes_M";
	rename -uid "2C306D76-4401-86AC-A96D-9E90FC799045";
	addAttr -ci true -k true -sn "aaa" -ln "aaa" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "eh" -ln "eh" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "ahh" -ln "ahh" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "ohh" -ln "ohh" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "uuu" -ln "uuu" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "iee" -ln "iee" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "rrr" -ln "rrr" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "www" -ln "www" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "sss" -ln "sss" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "fff" -ln "fff" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "tth" -ln "tth" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "mbp" -ln "mbp" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "ssh" -ln "ssh" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "schwa" -ln "schwa" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "gk" -ln "gk" -smn 0 -smx 10 -at "double";
	addAttr -ci true -sn "lntd" -ln "lntd" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "multipliers" -ln "multipliers" -at "double";
	addAttr -ci true -k true -sn "jaw" -ln "jaw" -dv 1 -smn 0 -smx 2 -at "double";
	addAttr -ci true -k true -sn "lip" -ln "lip" -dv 1 -smn 0 -smx 2 -at "double";
	addAttr -ci true -sn "Szz" -ln "Szz" -min 0 -max 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".ahh";
	setAttr -l on ".rrr";
	setAttr -l on ".www";
	setAttr -l on ".sss";
	setAttr -l on ".tth";
	setAttr -l on ".ssh";
	setAttr -l on ".schwa";
	setAttr -l on ".gk";
	setAttr -l on ".lntd";
	setAttr -l on -k on ".multipliers";
	setAttr -k on ".Szz";
createNode nurbsCurve -n "ctrlPhonemes_MShape" -p "ctrlPhonemes_M";
	rename -uid "7439232C-4CE0-A3BE-7204-80868B70C79E";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 8 0 no 3
		9 0 1 2 3 4 5 6 7 8
		9
		-0.55320539999999996 -0.59999999999999998 1.3322676295501878e-16
		-0.10619099999999999 0.59370420000000002 -1.3182881453133178e-16
		0.1169004 0.59370420000000002 -1.3182881453133178e-16
		0.5605853999999999 -0.59999999999999998 1.3322676295501878e-16
		0.34332119999999999 -0.59999999999999998 1.3322676295501878e-16
		0.23593800000000001 -0.29616300000000001 6.5761396328412049e-17
		-0.23355239999999999 -0.29616300000000001 6.5761396328412049e-17
		-0.33677399999999996 -0.59999999999999998 1.3322676295501878e-16
		-0.55320539999999996 -0.59999999999999998 1.3322676295501878e-16
		;
createNode nurbsCurve -n "ctrlPhonemes_MShape1" -p "ctrlPhonemes_M";
	rename -uid "ADDCBAC3-48C2-08DE-D076-4685CEC52E58";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 3 0 no 3
		4 0 1 2 3
		4
		-0.18194160000000001 -0.13467180000000001 2.9903146625542833e-17
		-0.0013045859999999999 0.41639700000000002 -9.2458707356968265e-17
		0.18349499999999999 -0.13467180000000001 2.9903146625542833e-17
		-0.18194160000000001 -0.13467180000000001 2.9903146625542833e-17
		;
createNode transform -n "ctrlBoxEmotions_M" -p "ctrlBox";
	rename -uid "5C276B64-4D51-8A20-6DA7-DF90B788D3C5";
	setAttr ".t" -type "double3" 0 -6.2140876770019533 0 ;
	setAttr ".s" -type "double3" 0.28970105720288825 0.28970105720288825 0.28970105720288825 ;
createNode nurbsCurve -n "ctrlBoxEmotions_MShape" -p "ctrlBoxEmotions_M";
	rename -uid "AB75FECC-46A7-8A5D-3890-6DAE7664CB33";
	setAttr -k off ".v";
	setAttr ".ovdt" 2;
	setAttr ".ove" yes;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		-1 1 0
		1 1 0
		1 -1 0
		-1 -1 0
		-1 1 0
		;
createNode transform -n "ctrlEmotions_M" -p "ctrlBoxEmotions_M";
	rename -uid "6FE15C5A-402C-A75A-7827-9DB604CB9DC2";
	addAttr -ci true -k true -sn "happy" -ln "happy" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "angry" -ln "angry" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "sad" -ln "sad" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "surprise" -ln "surprise" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "fear" -ln "fear" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "disgust" -ln "disgust" -smn 0 -smx 10 -at "double";
	addAttr -ci true -k true -sn "contempt" -ln "contempt" -smn 0 -smx 10 -at "double";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "ctrlEmotions_MShape" -p "ctrlEmotions_M";
	rename -uid "FFC29A06-4E0C-742F-99FB-529AE32B90CF";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 4 2 no 3
		9 -2 -1 0 1 2 3 4 5 6
		7
		-0.024999999999999953 0.44999999999999979 0
		-0.40000000000000002 0.625 0
		-0.77500000000000013 0.45000000000000001 0
		-0.40000000000000008 0.27499999999999997 0
		-0.024999999999999953 0.44999999999999979 0
		-0.40000000000000002 0.625 0
		-0.77500000000000013 0.45000000000000001 0
		;
createNode nurbsCurve -n "ctrlEmotions_MShape1" -p "ctrlEmotions_M";
	rename -uid "6E838A28-4E2A-94A4-49CB-F4BAA6CA4841";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 4 2 no 3
		9 -2 -1 0 1 2 3 4 5 6
		7
		0.77500000000000013 0.44999999999999979 0
		0.40000000000000002 0.625 0
		0.024999999999999953 0.45000000000000001 0
		0.39999999999999991 0.27499999999999997 0
		0.77500000000000013 0.44999999999999979 0
		0.40000000000000002 0.625 0
		0.024999999999999953 0.45000000000000001 0
		;
createNode nurbsCurve -n "ctrlEmotions_MShape2" -p "ctrlEmotions_M";
	rename -uid "295F59B4-468A-FA15-221E-95AE10EAE3B6";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.5485281374238572 -0.051471862576142752 0
		4.7500126261776384e-17 -0.32426406871192853 0
		-0.5485281374238572 -0.051471862576142946 0
		-0.77573593128807183 0.10000000000000009 0
		-0.5485281374238572 -0.44852813742385722 0
		-7.7705998787222589e-17 -0.67573593128807197 0
		0.5485281374238572 -0.44852813742385705 0
		0.77573593128807183 0.099999999999999867 0
		0.5485281374238572 -0.051471862576142752 0
		4.7500126261776384e-17 -0.32426406871192853 0
		-0.5485281374238572 -0.051471862576142946 0
		;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "152761E9-4B15-FFBF-97C8-80B800DB79FE";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "12F015BE-40CF-EAC1-7BCF-888942F40C4A";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "955AAE92-4BD5-9827-2A35-249C1DB5D6A2";
createNode displayLayerManager -n "layerManager";
	rename -uid "05C75FA4-4294-136C-0350-58951BD39FEA";
createNode displayLayer -n "defaultLayer";
	rename -uid "29750C7B-414F-F4C5-3D0A-B9AF1B88559F";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "3D806861-45F3-634C-22DF-84BA2D35F06E";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "42F071B7-455B-E748-8F03-AFA4D5C503C4";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "F732AE4F-4564-3D2E-A3AD-47A28E84FE6E";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1217\n            -height 732\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n"
		+ "            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n"
		+ "            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -shadows 0\n            -captureSequenceNumber -1\n"
		+ "            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n"
		+ "            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n"
		+ "            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n"
		+ "            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n"
		+ "            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n"
		+ "            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n"
		+ "            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1119\n            -height 732\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n"
		+ "            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -showUfeItems 1\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -selectCommand \"{}\" \n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n"
		+ "            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n"
		+ "            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -showUfeItems 1\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n"
		+ "            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n"
		+ "                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n"
		+ "                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -showUfeItems 1\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n"
		+ "                -snapValue \"none\" \n                -showPlayRangeShades \"on\" \n                -lockPlayRangeShades \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -keyMinScale 1\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -valueLinesToggle 1\n                -highlightAffectedCurves 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n"
		+ "                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n"
		+ "                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -showUfeItems 1\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n"
		+ "                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n"
		+ "                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -connectionMinSegment 0.03\n"
		+ "                -connectionOffset 0.03\n                -connectionRoundness 0.8\n                -connectionTension -100\n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -connectedGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -showUnitConversions 0\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -connectionMinSegment 0.03\n                -connectionOffset 0.03\n                -connectionRoundness 0.8\n                -connectionTension -100\n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -connectedGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n"
		+ "                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -showUnitConversions 0\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n{ string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"|persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n"
		+ "                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n"
		+ "                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n"
		+ "                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -bluePencil 1\n                -greasePencils 0\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n"
		+ "                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName; };\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1119\\n    -height 732\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1119\\n    -height 732\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "968971DE-4249-429D-CF4B-CDB75C1B3E10";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "100DB62E-406C-67C9-B4D1-F7AE342FF679";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -580.31133225185488 10155.951977391109 ;
	setAttr ".tgi[0].vh" -type "double2" 3006.5017120341872 11127.380510218578 ;
	setAttr -s 33 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 980;
	setAttr ".tgi[0].ni[0].y" 10411.4287109375;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" 980;
	setAttr ".tgi[0].ni[1].y" 9948.5712890625;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 980;
	setAttr ".tgi[0].ni[2].y" 9558.5712890625;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" 980;
	setAttr ".tgi[0].ni[3].y" 7998.5712890625;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 980;
	setAttr ".tgi[0].ni[4].y" 9038.5712890625;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" 980;
	setAttr ".tgi[0].ni[5].y" 11020;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 980;
	setAttr ".tgi[0].ni[6].y" 8518.5712890625;
	setAttr ".tgi[0].ni[6].nvs" 18304;
	setAttr ".tgi[0].ni[7].x" 980;
	setAttr ".tgi[0].ni[7].y" 7608.5712890625;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 980;
	setAttr ".tgi[0].ni[8].y" 9298.5712890625;
	setAttr ".tgi[0].ni[8].nvs" 18304;
	setAttr ".tgi[0].ni[9].x" 980;
	setAttr ".tgi[0].ni[9].y" 7738.5712890625;
	setAttr ".tgi[0].ni[9].nvs" 18304;
	setAttr ".tgi[0].ni[10].x" 980;
	setAttr ".tgi[0].ni[10].y" 9818.5712890625;
	setAttr ".tgi[0].ni[10].nvs" 18304;
	setAttr ".tgi[0].ni[11].x" 980;
	setAttr ".tgi[0].ni[11].y" 10310;
	setAttr ".tgi[0].ni[11].nvs" 18304;
	setAttr ".tgi[0].ni[12].x" 980;
	setAttr ".tgi[0].ni[12].y" 8778.5712890625;
	setAttr ".tgi[0].ni[12].nvs" 18304;
	setAttr ".tgi[0].ni[13].x" 980;
	setAttr ".tgi[0].ni[13].y" 10715.7138671875;
	setAttr ".tgi[0].ni[13].nvs" 18304;
	setAttr ".tgi[0].ni[14].x" 980;
	setAttr ".tgi[0].ni[14].y" 8908.5712890625;
	setAttr ".tgi[0].ni[14].nvs" 18304;
	setAttr ".tgi[0].ni[15].x" 980;
	setAttr ".tgi[0].ni[15].y" 7868.5712890625;
	setAttr ".tgi[0].ni[15].nvs" 18304;
	setAttr ".tgi[0].ni[16].x" 980;
	setAttr ".tgi[0].ni[16].y" 8258.5712890625;
	setAttr ".tgi[0].ni[16].nvs" 18304;
	setAttr ".tgi[0].ni[17].x" 980;
	setAttr ".tgi[0].ni[17].y" 8128.5712890625;
	setAttr ".tgi[0].ni[17].nvs" 18304;
	setAttr ".tgi[0].ni[18].x" 980;
	setAttr ".tgi[0].ni[18].y" 11222.857421875;
	setAttr ".tgi[0].ni[18].nvs" 18304;
	setAttr ".tgi[0].ni[19].x" 980;
	setAttr ".tgi[0].ni[19].y" 9428.5712890625;
	setAttr ".tgi[0].ni[19].nvs" 18304;
	setAttr ".tgi[0].ni[20].x" 980;
	setAttr ".tgi[0].ni[20].y" 9168.5712890625;
	setAttr ".tgi[0].ni[20].nvs" 18304;
	setAttr ".tgi[0].ni[21].x" 980;
	setAttr ".tgi[0].ni[21].y" 10208.5712890625;
	setAttr ".tgi[0].ni[21].nvs" 18304;
	setAttr ".tgi[0].ni[22].x" 980;
	setAttr ".tgi[0].ni[22].y" 8388.5712890625;
	setAttr ".tgi[0].ni[22].nvs" 18304;
	setAttr ".tgi[0].ni[23].x" 672.85711669921875;
	setAttr ".tgi[0].ni[23].y" 10767.142578125;
	setAttr ".tgi[0].ni[23].nvs" 18304;
	setAttr ".tgi[0].ni[24].x" 980;
	setAttr ".tgi[0].ni[24].y" 10614.2861328125;
	setAttr ".tgi[0].ni[24].nvs" 18304;
	setAttr ".tgi[0].ni[25].x" 980;
	setAttr ".tgi[0].ni[25].y" 11324.2861328125;
	setAttr ".tgi[0].ni[25].nvs" 18304;
	setAttr ".tgi[0].ni[26].x" 980;
	setAttr ".tgi[0].ni[26].y" 8648.5712890625;
	setAttr ".tgi[0].ni[26].nvs" 18304;
	setAttr ".tgi[0].ni[27].x" 980;
	setAttr ".tgi[0].ni[27].y" 10512.857421875;
	setAttr ".tgi[0].ni[27].nvs" 18304;
	setAttr ".tgi[0].ni[28].x" 980;
	setAttr ".tgi[0].ni[28].y" 10817.142578125;
	setAttr ".tgi[0].ni[28].nvs" 18304;
	setAttr ".tgi[0].ni[29].x" 980;
	setAttr ".tgi[0].ni[29].y" 9688.5712890625;
	setAttr ".tgi[0].ni[29].nvs" 18304;
	setAttr ".tgi[0].ni[30].x" 980;
	setAttr ".tgi[0].ni[30].y" 10918.5712890625;
	setAttr ".tgi[0].ni[30].nvs" 18304;
	setAttr ".tgi[0].ni[31].x" 980;
	setAttr ".tgi[0].ni[31].y" 10078.5712890625;
	setAttr ".tgi[0].ni[31].nvs" 18304;
	setAttr ".tgi[0].ni[32].x" 980;
	setAttr ".tgi[0].ni[32].y" 11121.4287109375;
	setAttr ".tgi[0].ni[32].nvs" 18304;
select -ne :time1;
	setAttr ".o" 30;
	setAttr ".unw" 30;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :initialMaterialInfo;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".dss" -type "string" "standardSurface1";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "ctrlBox.limits" "ctrlBrow_R.mtxe";
connectAttr "ctrlBox.limits" "ctrlBrow_R.mtye";
connectAttr "ctrlBox.limits" "ctrlBrow_R.xtxe";
connectAttr "ctrlBox.limits" "ctrlBrow_R.xtye";
connectAttr "ctrlBox.limits" "ctrlBrow_L.mtxe";
connectAttr "ctrlBox.limits" "ctrlBrow_L.mtye";
connectAttr "ctrlBox.limits" "ctrlBrow_L.xtxe";
connectAttr "ctrlBox.limits" "ctrlBrow_L.xtye";
connectAttr "ctrlBox.limits" "ctrlEye_R.mtxe";
connectAttr "ctrlBox.limits" "ctrlEye_R.mtye";
connectAttr "ctrlBox.limits" "ctrlEye_R.xtxe";
connectAttr "ctrlBox.limits" "ctrlEye_R.xtye";
connectAttr "ctrlBox.limits" "ctrlEye_L.mtxe";
connectAttr "ctrlBox.limits" "ctrlEye_L.mtye";
connectAttr "ctrlBox.limits" "ctrlEye_L.xtxe";
connectAttr "ctrlBox.limits" "ctrlEye_L.xtye";
connectAttr "ctrlBox.limits" "ctrlCheek_R.mtxe";
connectAttr "ctrlBox.limits" "ctrlCheek_R.mtye";
connectAttr "ctrlBox.limits" "ctrlCheek_R.xtxe";
connectAttr "ctrlBox.limits" "ctrlCheek_R.xtye";
connectAttr "ctrlBox.limits" "ctrlCheek_L.mtxe";
connectAttr "ctrlBox.limits" "ctrlCheek_L.mtye";
connectAttr "ctrlBox.limits" "ctrlCheek_L.xtxe";
connectAttr "ctrlBox.limits" "ctrlCheek_L.xtye";
connectAttr "ctrlBox.limits" "ctrlNose_R.mtxe";
connectAttr "ctrlBox.limits" "ctrlNose_R.mtye";
connectAttr "ctrlBox.limits" "ctrlNose_R.xtxe";
connectAttr "ctrlBox.limits" "ctrlNose_R.xtye";
connectAttr "ctrlBox.limits" "ctrlNose_L.mtxe";
connectAttr "ctrlBox.limits" "ctrlNose_L.mtye";
connectAttr "ctrlBox.limits" "ctrlNose_L.xtxe";
connectAttr "ctrlBox.limits" "ctrlNose_L.xtye";
connectAttr "ctrlBox.limits" "ctrlLips_M.mtxe";
connectAttr "ctrlBox.limits" "ctrlLips_M.mtye";
connectAttr "ctrlBox.limits" "ctrlLips_M.xtxe";
connectAttr "ctrlBox.limits" "ctrlLips_M.xtye";
connectAttr "ctrlBox.limits" "ctrlMouth_M.mtxe";
connectAttr "ctrlBox.limits" "ctrlMouth_M.mtye";
connectAttr "ctrlBox.limits" "ctrlMouth_M.xtxe";
connectAttr "ctrlBox.limits" "ctrlMouth_M.xtye";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_R.mtxe";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_R.mtye";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_R.xtxe";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_R.xtye";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_L.mtxe";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_L.mtye";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_L.xtxe";
connectAttr "ctrlBox.limits" "ctrlMouthCorner_L.xtye";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "ctrlEye_L.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn";
connectAttr "ctrlPhonemes_M.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "ctrlBoxShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn";
connectAttr "ctrlPhonemes_MShape1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn"
		;
connectAttr "ctrlLips_MShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn";
connectAttr "ctrlCheek_L.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn";
connectAttr "ctrlEmotions_MShape1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn"
		;
connectAttr "ctrlBrow_LShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn";
connectAttr "ctrlEye_LShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn";
connectAttr "ctrlEye_RShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[9].dn";
connectAttr "ctrlCheek_LShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[10].dn"
		;
connectAttr "ctrlBrow_R.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[11].dn";
connectAttr "ctrlCheek_RShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[12].dn"
		;
connectAttr "ctrlBrow_L.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[13].dn";
connectAttr "ctrlEmotions_M.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[14].dn";
connectAttr "ctrlMouthCorner_LShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[15].dn"
		;
connectAttr "ctrlPhonemes_MShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[16].dn"
		;
connectAttr "ctrlNose_RShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[17].dn"
		;
connectAttr "ctrlMouth_M.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[18].dn";
connectAttr "ctrlMouthCorner_RShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[19].dn"
		;
connectAttr "ctrlMouth_MShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[20].dn"
		;
connectAttr "ctrlNose_R.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[21].dn";
connectAttr "ctrlBrow_RShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[22].dn"
		;
connectAttr "ctrlBox.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[23].dn";
connectAttr "ctrlMouthCorner_R.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[24].dn"
		;
connectAttr "ctrlEye_R.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[25].dn";
connectAttr "ctrlEmotions_MShape2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[26].dn"
		;
connectAttr "ctrlCheek_R.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[27].dn";
connectAttr "ctrlNose_L.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[28].dn";
connectAttr "ctrlNose_LShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[29].dn"
		;
connectAttr "ctrlLips_M.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[30].dn";
connectAttr "ctrlEmotions_MShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[31].dn"
		;
connectAttr "ctrlMouthCorner_L.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[32].dn"
		;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
dataStructure -fmt "raw" -as "name=mapManager_slopes:string=value";
dataStructure -fmt "raw" -as "name=notes_frogLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_polySurface56:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane6:string=value";
dataStructure -fmt "raw" -as "name=notes_squareRocks_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass:string=value";
dataStructure -fmt "raw" -as "name=notes_riverSide:string=value";
dataStructure -fmt "raw" -as "name=notes_fountainHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floor_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_groundPlane_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayArea_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayFlowerBeds_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_groundB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloC:string=value";
dataStructure -fmt "raw" -as "name=mapManager_drawBridge_physPivot:string=value";
dataStructure -fmt "raw" -as "name=notes_juneBackYard:string=value";
dataStructure -fmt "raw" -as "name=notes_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_arbustosScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_left_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_trees:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSB:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_throwbotLeft_scatt:string=value";
dataStructure -fmt "raw" -as "name=DiffEdge:float=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiary:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloB:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayRocket_flowers:string=value";
dataStructure -fmt "raw" -as "name=faceConnectMarkerStructure:bool=faceConnectMarker:string[200]=faceConnectOutputGroups";
dataStructure -fmt "raw" -as "name=notes_vgtCampfire_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesSuelo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_tilesFloorDet:string=value";
dataStructure -fmt "raw" -as "name=faceConnectOutputStructure:bool=faceConnectOutput:string[200]=faceConnectOutputAttributes:string[200]=faceConnectOutputGroups";
dataStructure -fmt "raw" -as "name=notes_floor_flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_level1A:string=value";
dataStructure -fmt "raw" -as "name=notes_groundWoods_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane3:string=value";
dataStructure -fmt "raw" -as "name=notes_grasses:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloC:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersMain_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayMain_Flowers:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksCurbsGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_curbsGardenGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grass:string=value";
dataStructure -fmt "raw" -as "name=mapManager_concretePath_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_base_right:string=value";
dataStructure -fmt "raw" -as "name=notes_fountainRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_tunnel:string=value";
dataStructure -fmt "raw" -as "name=notes_det:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassA_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_chocolateFountain_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sidewalkGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_rightExterior_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_small_grass:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground03_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_CombinedGrass:string=value";
dataStructure -fmt "raw" -as "name=notes_terraces_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane4:string=value";
dataStructure -fmt "raw" -as "name=notes_treesRocksHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiary_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsCSA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floorScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesCDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSA:string=value";
dataStructure -fmt "raw" -as "name=notes_leaves:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiaryGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassesCenter_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_railes:string=value";
dataStructure -fmt "raw" -as "name=notes_grassADecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=externalContentTablZ:string=nodZ:string=key:string=upath:uint32=upathcrc:string=rpath:string=roles";
dataStructure -fmt "raw" -as "name=mapManager_pPlane4:string=value";
dataStructure -fmt "raw" -as "name=keyValueStructure:string=value";
dataStructure -fmt "raw" -as "name=notes_floorFlower:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksGround:string=value";
dataStructure -fmt "raw" -as "name=notes_treesA_parShape:string=value";
dataStructure -fmt "raw" -as "name=wingnut_ar:string=metadata";
dataStructure -fmt "raw" -as "name=notes_grass_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassD_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloP2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTielMainStreet_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_riverSideground:string=value";
dataStructure -fmt "raw" -as "name=notes_midground_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_Scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_Scatt:string=value";
dataStructure -fmt "raw" -as "name=notes_background_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_new_sand:string=value";
dataStructure -fmt "raw" -as "name=notes_railes:string=value";
dataStructure -fmt "raw" -as "name=mapManager_Suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassLeftMountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseScatter:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyFlowersBedA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseForest:string=value";
dataStructure -fmt "raw" -as "name=notes_square_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_bushes_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_ground03_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_throwbotLeftScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_vgTFicus39:string=value";
dataStructure -fmt "raw" -as "name=notes_floorOrangeConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_leftSpecific_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floorSquare:string=value";
dataStructure -fmt "raw" -as "name=Blur3dMetaData:string=Blur3dValue";
dataStructure -fmt "raw" -as "name=mapManager_stoneFloor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesGrasStairs_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_scatt:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloor:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeaves_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeRightScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassD_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_stairs_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1B_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_left:string=value";
dataStructure -fmt "raw" -as "name=notes_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_original:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloP1:string=value";
dataStructure -fmt "raw" -as "name=notes_midgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_base:string=value";
dataStructure -fmt "raw" -as "name=notes_juneNbhHouseE_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchG_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA8:string=value";
dataStructure -fmt "raw" -as "name=mapManager_degraded:string=value";
dataStructure -fmt "raw" -as "name=notes_vegetation_parShape:string=value";
dataStructure -fmt "raw" -as "name=OffStruct:float=Offset";
dataStructure -fmt "raw" -as "name=mapManager_floorFlower:string=value";
dataStructure -fmt "raw" -as "name=notes_floorOrangeGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_leaves:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsCSC_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_backWall_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_left1:string=value";
dataStructure -fmt "raw" -as "name=notes_mountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_rockTerraces_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTopiary_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_square_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassB_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_big_back:string=value";
dataStructure -fmt "raw" -as "name=notes_original:string=value";
dataStructure -fmt "raw" -as "name=notes_sand_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_restaurantBack:string=value";
dataStructure -fmt "raw" -as "name=mapManager_arbustosScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_curbsGarden_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_floorConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_left:string=value";
dataStructure -fmt "raw" -as "name=notes_concretesGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSB:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA:string=value";
dataStructure -fmt "raw" -as "name=notes_road_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_frogL_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_degraded:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantFront:string=value";
dataStructure -fmt "raw" -as "name=notes_bushesA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_holeRock_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_new_sand:string=value";
dataStructure -fmt "raw" -as "name=notes_terraceGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_juneBackYard:string=value";
dataStructure -fmt "raw" -as "name=notes_groundC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBase:string=value";
dataStructure -fmt "raw" -as "name=notes_groundA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rockSignRollo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_road_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundWoods_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=notes_bridge_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_strap_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_groundRocks:string=value";
dataStructure -fmt "raw" -as "name=mapManager_restaurantFront:string=value";
dataStructure -fmt "raw" -as "name=notes_testMode_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksGround:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_hojas:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassC_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_center_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_barbacueHouseFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_level1B_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassCenter_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terraceBush_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees_left:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainTrail_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesTrees_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_wasteLand_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_treesRocksAnimalHome_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sidewalkGrassB_parShape:string=value";
dataStructure -fmt "raw" -as "name=Curvature:float=mean:float=gaussian:float=ABS:float=RMS";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_small_grass:string=value";
dataStructure -fmt "raw" -as "name=OrgStruct:float[3]=Origin Point";
dataStructure -fmt "raw" -as "name=notes_grassD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassGround_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantBack:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_c_geo:string=value";
dataStructure -fmt "raw" -as "name=TifLocation:string=Path";
dataStructure -fmt "raw" -as "name=notes_rocskLeftPLA:string=value";
dataStructure -fmt "raw" -as "name=notes_grassJuneBackYard_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane5:string=value";
dataStructure -fmt "raw" -as "name=notes_rockSignRollo:string=value";
dataStructure -fmt "raw" -as "name=IdStruct:int32=ID";
dataStructure -fmt "raw" -as "name=notes_walkwaySquareFlowers_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksGrounds:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassB_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksGrounds:string=value";
dataStructure -fmt "raw" -as "name=notes_path:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloP2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseLeaves:string=value";
dataStructure -fmt "raw" -as "name=mapManager_circular:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeavesCarousel_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rocskLeftPLA:string=value";
dataStructure -fmt "raw" -as "name=notes_backgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_mainStreetMainstreetTrees04:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees_left1:string=value";
dataStructure -fmt "raw" -as "name=notes_entrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_widlPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaCorner_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_square_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_small:string=value";
dataStructure -fmt "raw" -as "name=mapManager_flowersSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_floorGrassA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_cheat_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_amp_lyref_cmp0010_layGround:string=value";
dataStructure -fmt "raw" -as "name=mapManager_backgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersRightLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopes_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_tunnelParkEntrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_scatterGround:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane5:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA8:string=value";
dataStructure -fmt "raw" -as "name=notes_scatterGround:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassRightMountains:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_drawBridge_physPivot:string=value";
dataStructure -fmt "raw" -as "name=RenderSettings:string=preset";
dataStructure -fmt "raw" -as "name=mapManager_square_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTopiary:string=value";
dataStructure -fmt "raw" -as "name=notes_geos:string=value";
dataStructure -fmt "raw" -as "name=mapManager_road_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_vgGroundB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassRightMountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSC:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksFence_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayCircular_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_rocks:string=value";
dataStructure -fmt "raw" -as "name=mapManager_terracesSuelo:string=value";
dataStructure -fmt "raw" -as "name=notes_Suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassCampfire_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloB:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket_flowers:string=value";
dataStructure -fmt "raw" -as "name=mapManager_throwbotLeft_scatt:string=value";
dataStructure -fmt "raw" -as "name=notes_floor1:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSA:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantNextHouse_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassD_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainsRight:string=value";
dataStructure -fmt "raw" -as "name=notes_levelC:string=value";
dataStructure -fmt "raw" -as "name=mapManager_strap_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_baseLeaves:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_rockCheated_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_riverSide:string=value";
dataStructure -fmt "raw" -as "name=DiffArea:float=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchH_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayRocket:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_circular:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloProvi3:string=value";
dataStructure -fmt "raw" -as "name=notes_base_hojas:string=value";
dataStructure -fmt "raw" -as "name=mapManager_geos:string=value";
dataStructure -fmt "raw" -as "name=notes_suelofuente:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBeauty_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane1:string=value";
dataStructure -fmt "raw" -as "name=FBXFastExportSetting_MB:string=19424";
dataStructure -fmt "raw" -as "name=mapManager_floorOrangeConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=Offset:float[3]=value";
dataStructure -fmt "raw" -as "name=FBXFastExportSetting_FBX:string=54";
dataStructure -fmt "raw" -as "name=notes_leaves_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesMountainsGrass_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_slabsAndStairsGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_path:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor_flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_vgFCarouselBed_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundRocks:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassBase:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassRightMountains:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTielMainStreet_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_baseForest:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_CombinedGrass:string=value";
dataStructure -fmt "raw" -as "name=mapManager_levelC:string=value";
dataStructure -fmt "raw" -as "name=mapManager_midgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloor_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_leavesDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayMain_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_det:string=value";
dataStructure -fmt "raw" -as "name=mapManager_stairs_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grasses:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwaySquare_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_tilesFloorDet:string=value";
dataStructure -fmt "raw" -as "name=notes_amp_lyref_cmp0010_layGround:string=value";
dataStructure -fmt "raw" -as "name=notes_right_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassGround_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sand_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_rockSignRollo_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_tunnel:string=value";
dataStructure -fmt "raw" -as "name=notes_base_left:string=value";
dataStructure -fmt "raw" -as "name=mapManager_riverSideground:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA9:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassD_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_railwayGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwaySpaceland_Main_Leaves:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassC_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA9:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantBack_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_throwbotLeftScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1A_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSC:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeavesFlowerBed_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchF_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane6:string=value";
dataStructure -fmt "raw" -as "name=notes_floorA:string=value";
dataStructure -fmt "raw" -as "name=notes_suelo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundPlane_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloP1:string=value";
dataStructure -fmt "raw" -as "name=notes_frogEntrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_ferns_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorCampfire:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane3:string=value";
dataStructure -fmt "raw" -as "name=notes_grassScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsRight:string=value";
dataStructure -fmt "raw" -as "name=notes_ground_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slideSundaeRightScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_curbsGarden_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesFlowers_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_carouselStairs_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayMain_Flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket:string=value";
dataStructure -fmt "raw" -as "name=notes_groundD_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rocks:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane1:string=value";
dataStructure -fmt "raw" -as "name=notes_polySurface56:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane2:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_ridePiggy_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksFence_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_level1A_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_small:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_floorCampfire:string=value";
dataStructure -fmt "raw" -as "name=notes_slopes:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsCSB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorA:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesGrassDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloorGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwaySpaceland_Main_Leaves:string=value";
dataStructure -fmt "raw" -as "name=notes_hotelBack_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_suelofuente:string=value";
dataStructure -fmt "raw" -as "name=idStructure:int32=ID";
dataStructure -fmt "raw" -as "name=notes_grassCDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_centerStreetGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_backWall_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesMountainsGrass_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchE_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_riverside_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_right:string=value";
dataStructure -fmt "raw" -as "name=notes_base_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_big_back:string=value";
dataStructure -fmt "raw" -as "name=notes_baseScatter:string=value";
dataStructure -fmt "raw" -as "name=notes_treesB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1A:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassA_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchDegraded_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_concretePath_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_heroesChoice_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_square_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_baseScatt:string=value";
applyMetadata -fmt "raw" -v "channel\nname default\nstream\nname wingnut_ar_stream\nindexType string\nstructure wingnut_ar\ncontext\n\"S'MKT-Master-1.0.1'\\np0\\n.\"\ncontext_resolve\n\"(lp0\\nS'maya_common_fishbowl-0.1.0'\\np1\\naS'platform-windows'\\np2\\naS'arch-AMD64'\\np3\\naS'autodesk_license-1.0.0'\\np4\\naS'maya-2019.2.0'\\np5\\naS'maya_live_link-2.0'\\np6\\naS'mgear-3.1.1'\\np7\\naS'mtoa-2019.2.0'\\np8\\naS'chaosgroup_license-1.0.0'\\np9\\naS'vray_for_maya-4.12.1.1'\\np10\\naS'six-1.10.0'\\np11\\naS'anytree-2.2.2'\\np12\\naS'python-2.7.14'\\np13\\naS'p4python-2017.2.1615960'\\np14\\naS'functools32-3.2.3.post2'\\np15\\naS'jsonschema-2.6.0'\\np16\\naS'rez_api-2.47.2'\\np17\\naS'qt_py-1.2.2'\\np18\\naS'war_qt-1.4.0'\\np19\\naS'shotgun_api3-3.0.40'\\np20\\naS'war-1.0.0'\\np21\\naS'ffmpeg-4.0.2'\\np22\\naS'enum34-1.1.6'\\np23\\naS'future-0.16.0'\\np24\\naS'ffmpeg_python-0.2.0'\\np25\\naS'requests-2.14.2'\\np26\\naS'war_foundations-2.36.1'\\np27\\naS'war_menu-1.4.1'\\np28\\naS'war_assets-2.4.0'\\np29\\naS'war_unreal-1.3.3'\\np30\\naS'war_scene-4.4.0'\\np31\\naS'war_machine-1.0.5'\\np32\\naS'war_anim-1.0.6'\\np33\\naS'war_compass-0.3.0'\\np34\\naS'war_maya_blendshapeRecv-2.1.1'\\np35\\naS'war_maya-1.0.0'\\np36\\naS'war_maya_common-1.7.1'\\np37\\naS'docutils-0.14'\\np38\\naS'wmPolyGoodies-4.04.1'\\np39\\naS'war_maya_validation-4.6.1'\\np40\\naS'war_ocio-2.5.1'\\np41\\naS'rv-7.3.1'\\np42\\naS'war_scene_maya-4.2.0'\\np43\\naS'wmModels-1.8.1'\\np44\\naS'wmMisc-6.17.1'\\np45\\naS'wmVertCopy-2.6.1'\\np46\\naS'AsfAmc-0.33.11'\\np47\\naS'wmAnim-1.51.2'\\np48\\naS'weta_cre-1.2.1'\\np49\\naS'weta_maya_models-0.2.0'\\np50\\na.\"\ncontext_rxt\n\"(dp0\\nVrez_version\\np1\\nV2.47.2\\np2\\nsVresolved_packages\\np3\\n(lp4\\n(dp5\\nVvariables\\np6\\n(dp7\\nVindex\\np8\\nNsVversion\\np9\\nV0.1.0\\np10\\nsVrepository_type\\np11\\nVfilesystem\\np12\\nsVlocation\\np13\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np14\\nsVname\\np15\\nVmaya_common_fishbowl\\np16\\nssVkey\\np17\\nVfilesystem.variant\\np18\\nsa(dp19\\nVvariables\\np20\\n(dp21\\nVindex\\np22\\nNsVversion\\np23\\nVwindows\\np24\\nsVrepository_type\\np25\\nVfilesystem\\np26\\nsVlocation\\np27\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np28\\nsVname\\np29\\nVplatform\\np30\\nssVkey\\np31\\nVfilesystem.variant\\np32\\nsa(dp33\\nVvariables\\np34\\n(dp35\\nVindex\\np36\\nNsVversion\\np37\\nVAMD64\\np38\\nsVrepository_type\\np39\\nVfilesystem\\np40\\nsVlocation\\np41\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np42\\nsVname\\np43\\nVarch\\np44\\nssVkey\\np45\\nVfilesystem.variant\\np46\\nsa(dp47\\nVvariables\\np48\\n(dp49\\nVindex\\np50\\nNsVversion\\np51\\nV1.0.0\\np52\\nsVrepository_type\\np53\\nVfilesystem\\np54\\nsVlocation\\np55\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np56\\nsVname\\np57\\nVautodesk_license\\np58\\nssVkey\\np59\\nVfilesystem.variant\\np60\\nsa(dp61\\nVvariables\\np62\\n(dp63\\nVindex\\np64\\nI0\\nsVversion\\np65\\nV2019.2.0\\np66\\nsVrepository_type\\np67\\nVfilesystem\\np68\\nsVlocation\\np69\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np70\\nsVname\\np71\\nVmaya\\np72\\nssVkey\\np73\\nVfilesystem.variant\\np74\\nsa(dp75\\nVvariables\\np76\\n(dp77\\nVindex\\np78\\nI3\\nsVversion\\np79\\nV2.0\\np80\\nsVrepository_type\\np81\\nVfilesystem\\np82\\nsVlocation\\np83\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np84\\nsVname\\np85\\nVmaya_live_link\\np86\\nssVkey\\np87\\nVfilesystem.variant\\np88\\nsa(dp89\\nVvariables\\np90\\n(dp91\\nVindex\\np92\\nI0\\nsVversion\\np93\\nV3.1.1\\np94\\nsVrepository_type\\np95\\nVfilesystem\\np96\\nsVlocation\\np97\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np98\\nsVname\\np99\\nVmgear\\np100\\nssVkey\\np101\\nVfilesystem.variant\\np102\\nsa(dp103\\nVvariables\\np104\\n(dp105\\nVindex\\np106\\nI0\\nsVversion\\np107\\nV2019.2.0\\np108\\nsVrepository_type\\np109\\nVfilesystem\\np110\\nsVlocation\\np111\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np112\\nsVname\\np113\\nVmtoa\\np114\\nssVkey\\np115\\nVfilesystem.variant\\np116\\nsa(dp117\\nVvariables\\np118\\n(dp119\\nVindex\\np120\\nNsVversion\\np121\\nV1.0.0\\np122\\nsVrepository_type\\np123\\nVfilesystem\\np124\\nsVlocation\\np125\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np126\\nsVname\\np127\\nVchaosgroup_license\\np128\\nssVkey\\np129\\nVfilesystem.variant\\np130\\nsa(dp131\\nVvariables\\np132\\n(dp133\\nVindex\\np134\\nI0\\nsVversion\\np135\\nV4.12.1.1\\np136\\nsVrepository_type\\np137\\nVfilesystem\\np138\\nsVlocation\\np139\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np140\\nsVname\\np141\\nVvray_for_maya\\np142\\nssVkey\\np143\\nVfilesystem.variant\\np144\\nsa(dp145\\nVvariables\\np146\\n(dp147\\nVindex\\np148\\nNsVversion\\np149\\nV1.10.0\\np150\\nsVrepository_type\\np151\\nVfilesystem\\np152\\nsVlocation\\np153\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np154\\nsVname\\np155\\nVsix\\np156\\nssVkey\\np157\\nVfilesystem.variant\\np158\\nsa(dp159\\nVvariables\\np160\\n(dp161\\nVindex\\np162\\nNsVversion\\np163\\nV2.2.2\\np164\\nsVrepository_type\\np165\\nVfilesystem\\np166\\nsVlocation\\np167\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np168\\nsVname\\np169\\nVanytree\\np170\\nssVkey\\np171\\nVfilesystem.variant\\np172\\nsa(dp173\\nVvariables\\np174\\n(dp175\\nVindex\\np176\\nNsVversion\\np177\\nV2.7.14\\np178\\nsVrepository_type\\np179\\nVfilesystem\\np180\\nsVlocation\\np181\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np182\\nsVname\\np183\\nVpython\\np184\\nssVkey\\np185\\nVfilesystem.variant\\np186\\nsa(dp187\\nVvariables\\np188\\n(dp189\\nVindex\\np190\\nI0\\nsVversion\\np191\\nV2017.2.1615960\\np192\\nsVrepository_type\\np193\\nVfilesystem\\np194\\nsVlocation\\np195\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np196\\nsVname\\np197\\nVp4python\\np198\\nssVkey\\np199\\nVfilesystem.variant\\np200\\nsa(dp201\\nVvariables\\np202\\n(dp203\\nVindex\\np204\\nNsVversion\\np205\\nV3.2.3.post2\\np206\\nsVrepository_type\\np207\\nVfilesystem\\np208\\nsVlocation\\np209\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np210\\nsVname\\np211\\nVfunctools32\\np212\\nssVkey\\np213\\nVfilesystem.variant\\np214\\nsa(dp215\\nVvariables\\np216\\n(dp217\\nVindex\\np218\\nI0\\nsVversion\\np219\\nV2.6.0\\np220\\nsVrepository_type\\np221\\nVfilesystem\\np222\\nsVlocation\\np223\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np224\\nsVname\\np225\\nVjsonschema\\np226\\nssVkey\\np227\\nVfilesystem.variant\\np228\\nsa(dp229\\nVvariables\\np230\\n(dp231\\nVindex\\np232\\nI0\\nsVversion\\np233\\nV2.47.2\\np234\\nsVrepository_type\\np235\\nVfilesystem\\np236\\nsVlocation\\np237\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np238\\nsVname\\np239\\nVrez_api\\np240\\nssVkey\\np241\\nVfilesystem.variant\\np242\\nsa(dp243\\nVvariables\\np244\\n(dp245\\nVindex\\np246\\nNsVversion\\np247\\nV1.2.2\\np248\\nsVrepository_type\\np249\\nVfilesystem\\np250\\nsVlocation\\np251\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np252\\nsVname\\np253\\nVqt_py\\np254\\nssVkey\\np255\\nVfilesystem.variant\\np256\\nsa(dp257\\nVvariables\\np258\\n(dp259\\nVindex\\np260\\nNsVversion\\np261\\nV1.4.0\\np262\\nsVrepository_type\\np263\\nVfilesystem\\np264\\nsVlocation\\np265\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np266\\nsVname\\np267\\nVwar_qt\\np268\\nssVkey\\np269\\nVfilesystem.variant\\np270\\nsa(dp271\\nVvariables\\np272\\n(dp273\\nVindex\\np274\\nNsVversion\\np275\\nV3.0.40\\np276\\nsVrepository_type\\np277\\nVfilesystem\\np278\\nsVlocation\\np279\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np280\\nsVname\\np281\\nVshotgun_api3\\np282\\nssVkey\\np283\\nVfilesystem.variant\\np284\\nsa(dp285\\nVvariables\\np286\\n(dp287\\nVindex\\np288\\nNsVversion\\np289\\nV1.0.0\\np290\\nsVrepository_type\\np291\\nVfilesystem\\np292\\nsVlocation\\np293\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np294\\nsVname\\np295\\nVwar\\np296\\nssVkey\\np297\\nVfilesystem.variant\\np298\\nsa(dp299\\nVvariables\\np300\\n(dp301\\nVindex\\np302\\nI0\\nsVversion\\np303\\nV4.0.2\\np304\\nsVrepository_type\\np305\\nVfilesystem\\np306\\nsVlocation\\np307\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np308\\nsVname\\np309\\nVffmpeg\\np310\\nssVkey\\np311\\nVfilesystem.variant\\np312\\nsa(dp313\\nVvariables\\np314\\n(dp315\\nVindex\\np316\\nNsVversion\\np317\\nV1.1.6\\np318\\nsVrepository_type\\np319\\nVfilesystem\\np320\\nsVlocation\\np321\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np322\\nsVname\\np323\\nVenum34\\np324\\nssVkey\\np325\\nVfilesystem.variant\\np326\\nsa(dp327\\nVvariables\\np328\\n(dp329\\nVindex\\np330\\nI0\\nsVversion\\np331\\nV0.16.0\\np332\\nsVrepository_type\\np333\\nVfilesystem\\np334\\nsVlocation\\np335\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np336\\nsVname\\np337\\nVfuture\\np338\\nssVkey\\np339\\nVfilesystem.variant\\np340\\nsa(dp341\\nVvariables\\np342\\n(dp343\\nVindex\\np344\\nNsVversion\\np345\\nV0.2.0\\np346\\nsVrepository_type\\np347\\nVfilesystem\\np348\\nsVlocation\\np349\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np350\\nsVname\\np351\\nVffmpeg_python\\np352\\nssVkey\\np353\\nVfilesystem.variant\\np354\\nsa(dp355\\nVvariables\\np356\\n(dp357\\nVindex\\np358\\nNsVversion\\np359\\nV2.14.2\\np360\\nsVrepository_type\\np361\\nVfilesystem\\np362\\nsVlocation\\np363\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np364\\nsVname\\np365\\nVrequests\\np366\\nssVkey\\np367\\nVfilesystem.variant\\np368\\nsa(dp369\\nVvariables\\np370\\n(dp371\\nVindex\\np372\\nNsVversion\\np373\\nV2.36.1\\np374\\nsVrepository_type\\np375\\nVfilesystem\\np376\\nsVlocation\\np377\\nVs:\\\\u005cpackages\\\\u005cfishbowl\\np378\\nsVname\\np379\\nVwar_foundations\\np380\\nssVkey\\np381\\nVfilesystem.variant\\np382\\nsa(dp383\\nVvariables\\np384\\n(dp385\\nVindex\\np386\\nNsVversion\\np387\\nV1.4.1\\np388\\nsVrepository_type\\np389\\nVfilesystem\\np390\\nsVlocation\\np391\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np392\\nsVname\\np393\\nVwar_menu\\np394\\nssVkey\\np395\\nVfilesystem.variant\\np396\\nsa(dp397\\nVvariables\\np398\\n(dp399\\nVindex\\np400\\nNsVversion\\np401\\nV2.4.0\\np402\\nsVrepository_type\\np403\\nVfilesystem\\np404\\nsVlocation\\np405\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np406\\nsVname\\np407\\nVwar_assets\\np408\\nssVkey\\np409\\nVfilesystem.variant\\np410\\nsa(dp411\\nVvariables\\np412\\n(dp413\\nVindex\\np414\\nNsVversion\\np415\\nV1.3.3\\np416\\nsVrepository_type\\np417\\nVfilesystem\\np418\\nsVlocation\\np419\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np420\\nsVname\\np421\\nVwar_unreal\\np422\\nssVkey\\np423\\nVfilesystem.variant\\np424\\nsa(dp425\\nVvariables\\np426\\n(dp427\\nVindex\\np428\\nNsVversion\\np429\\nV4.4.0\\np430\\nsVrepository_type\\np431\\nVfilesystem\\np432\\nsVlocation\\np433\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np434\\nsVname\\np435\\nVwar_scene\\np436\\nssVkey\\np437\\nVfilesystem.variant\\np438\\nsa(dp439\\nVvariables\\np440\\n(dp441\\nVindex\\np442\\nNsVversion\\np443\\nV1.0.5\\np444\\nsVrepository_type\\np445\\nVfilesystem\\np446\\nsVlocation\\np447\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np448\\nsVname\\np449\\nVwar_machine\\np450\\nssVkey\\np451\\nVfilesystem.variant\\np452\\nsa(dp453\\nVvariables\\np454\\n(dp455\\nVindex\\np456\\nNsVversion\\np457\\nV1.0.6\\np458\\nsVrepository_type\\np459\\nVfilesystem\\np460\\nsVlocation\\np461\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np462\\nsVname\\np463\\nVwar_anim\\np464\\nssVkey\\np465\\nVfilesystem.variant\\np466\\nsa(dp467\\nVvariables\\np468\\n(dp469\\nVindex\\np470\\nNsVversion\\np471\\nV0.3.0\\np472\\nsVrepository_type\\np473\\nVfilesystem\\np474\\nsVlocation\\np475\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np476\\nsVname\\np477\\nVwar_compass\\np478\\nssVkey\\np479\\nVfilesystem.variant\\np480\\nsa(dp481\\nVvariables\\np482\\n(dp483\\nVindex\\np484\\nI1\\nsVversion\\np485\\nV2.1.1\\np486\\nsVrepository_type\\np487\\nVfilesystem\\np488\\nsVlocation\\np489\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np490\\nsVname\\np491\\nVwar_maya_blendshapeRecv\\np492\\nssVkey\\np493\\nVfilesystem.variant\\np494\\nsa(dp495\\nVvariables\\np496\\n(dp497\\nVindex\\np498\\nNsVversion\\np499\\nV1.0.0\\np500\\nsVrepository_type\\np501\\nVfilesystem\\np502\\nsVlocation\\np503\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np504\\nsVname\\np505\\nVwar_maya\\np506\\nssVkey\\np507\\nVfilesystem.variant\\np508\\nsa(dp509\\nVvariables\\np510\\n(dp511\\nVindex\\np512\\nNsVversion\\np513\\nV1.7.1\\np514\\nsVrepository_type\\np515\\nVfilesystem\\np516\\nsVlocation\\np517\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np518\\nsVname\\np519\\nVwar_maya_common\\np520\\nssVkey\\np521\\nVfilesystem.variant\\np522\\nsa(dp523\\nVvariables\\np524\\n(dp525\\nVindex\\np526\\nNsVversion\\np527\\nV0.14\\np528\\nsVrepository_type\\np529\\nVfilesystem\\np530\\nsVlocation\\np531\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np532\\nsVname\\np533\\nVdocutils\\np534\\nssVkey\\np535\\nVfilesystem.variant\\np536\\nsa(dp537\\nVvariables\\np538\\n(dp539\\nVindex\\np540\\nI0\\nsVversion\\np541\\nV4.04.1\\np542\\nsVrepository_type\\np543\\nVfilesystem\\np544\\nsVlocation\\np545\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np546\\nsVname\\np547\\nVwmPolyGoodies\\np548\\nssVkey\\np549\\nVfilesystem.variant\\np550\\nsa(dp551\\nVvariables\\np552\\n(dp553\\nVindex\\np554\\nNsVversion\\np555\\nV4.6.1\\np556\\nsVrepository_type\\np557\\nVfilesystem\\np558\\nsVlocation\\np559\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np560\\nsVname\\np561\\nVwar_maya_validation\\np562\\nssVkey\\np563\\nVfilesystem.variant\\np564\\nsa(dp565\\nVvariables\\np566\\n(dp567\\nVindex\\np568\\nNsVversion\\np569\\nV2.5.1\\np570\\nsVrepository_type\\np571\\nVfilesystem\\np572\\nsVlocation\\np573\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np574\\nsVname\\np575\\nVwar_ocio\\np576\\nssVkey\\np577\\nVfilesystem.variant\\np578\\nsa(dp579\\nVvariables\\np580\\n(dp581\\nVindex\\np582\\nI0\\nsVversion\\np583\\nV7.3.1\\np584\\nsVrepository_type\\np585\\nVfilesystem\\np586\\nsVlocation\\np587\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np588\\nsVname\\np589\\nVrv\\np590\\nssVkey\\np591\\nVfilesystem.variant\\np592\\nsa(dp593\\nVvariables\\np594\\n(dp595\\nVindex\\np596\\nNsVversion\\np597\\nV4.2.0\\np598\\nsVrepository_type\\np599\\nVfilesystem\\np600\\nsVlocation\\np601\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np602\\nsVname\\np603\\nVwar_scene_maya\\np604\\nssVkey\\np605\\nVfilesystem.variant\\np606\\nsa(dp607\\nVvariables\\np608\\n(dp609\\nVindex\\np610\\nI0\\nsVversion\\np611\\nV1.8.1\\np612\\nsVrepository_type\\np613\\nVfilesystem\\np614\\nsVlocation\\np615\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np616\\nsVname\\np617\\nVwmModels\\np618\\nssVkey\\np619\\nVfilesystem.variant\\np620\\nsa(dp621\\nVvariables\\np622\\n(dp623\\nVindex\\np624\\nI0\\nsVversion\\np625\\nV6.17.1\\np626\\nsVrepository_type\\np627\\nVfilesystem\\np628\\nsVlocation\\np629\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np630\\nsVname\\np631\\nVwmMisc\\np632\\nssVkey\\np633\\nVfilesystem.variant\\np634\\nsa(dp635\\nVvariables\\np636\\n(dp637\\nVindex\\np638\\nI0\\nsVversion\\np639\\nV2.6.1\\np640\\nsVrepository_type\\np641\\nVfilesystem\\np642\\nsVlocation\\np643\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np644\\nsVname\\np645\\nVwmVertCopy\\np646\\nssVkey\\np647\\nVfilesystem.variant\\np648\\nsa(dp649\\nVvariables\\np650\\n(dp651\\nVindex\\np652\\nI0\\nsVversion\\np653\\nV0.33.11\\np654\\nsVrepository_type\\np655\\nVfilesystem\\np656\\nsVlocation\\np657\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np658\\nsVname\\np659\\nVAsfAmc\\np660\\nssVkey\\np661\\nVfilesystem.variant\\np662\\nsa(dp663\\nVvariables\\np664\\n(dp665\\nVindex\\np666\\nI0\\nsVversion\\np667\\nV1.51.2\\np668\\nsVrepository_type\\np669\\nVfilesystem\\np670\\nsVlocation\\np671\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np672\\nsVname\\np673\\nVwmAnim\\np674\\nssVkey\\np675\\nVfilesystem.variant\\np676\\nsa(dp677\\nVvariables\\np678\\n(dp679\\nVindex\\np680\\nNsVversion\\np681\\nV1.2.1\\np682\\nsVrepository_type\\np683\\nVfilesystem\\np684\\nsVlocation\\np685\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np686\\nsVname\\np687\\nVweta_cre\\np688\\nssVkey\\np689\\nVfilesystem.variant\\np690\\nsa(dp691\\nVvariables\\np692\\n(dp693\\nVindex\\np694\\nNsVversion\\np695\\nV0.2.0\\np696\\nsVrepository_type\\np697\\nVfilesystem\\np698\\nsVlocation\\np699\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np700\\nsVname\\np701\\nVweta_maya_models\\np702\\nssVkey\\np703\\nVfilesystem.variant\\np704\\nsasVnum_loaded_packages\\np705\\nI194\\nsVsolve_time\\np706\\nF2.2200000286102295\\nsVimplicit_packages\\np707\\n(lp708\\nV~platform==windows\\np709\\naV~arch==AMD64\\np710\\naV~os==windows-10.0.18362\\np711\\nasVparent_suite_path\\np712\\nNsVgraph\\np713\\nV{'nodes': [((('fillcolor', '#AAFFAA'), ('fontsize', 10), ('style', 'filled')), [('_62', 'wmModels-1.8.1[0]'), ('_63', 'wmMisc-6.17.1[0]'), ('_60', 'rv-7.3.1[0]'), ('_61', 'war_scene_maya-4.2.0[]'), ('_66', 'wmAnim-1.51.2[0]'), ('_67', 'weta_cre-1.2.1[]'), ('_64', 'wmVertCopy-2.6.1[0]'), ('_65', 'AsfAmc-0.33.11[0]'), ('_68', 'weta_maya_models-0.2.0[]'), ('_19', 'maya_common_fishbowl-0.1.0[]'), ('_39', 'war-1.0.0[]'), ('_38', 'shotgun_api3-3.0.40[]'), ('_31', 'python-2.7.14[]'), ('_30', 'anytree-2.2.2[]'), ('_33', 'functools32-3.2.3.post2[]'), ('_32', 'p4python-2017.2.1615960[0]'), ('_35', 'rez_api-2.47.2[0]'), ('_34', 'jsonschema-2.6.0[0]'), ('_37', 'war_qt-1.4.0[]'), ('_36', 'qt_py-1.2.2[]'), ('_59', 'war_ocio-2.5.1[]'), ('_58', 'war_maya_validation-4.6.1[]'), ('_53', 'war_maya_blendshapeRecv-2.1.1[1]'), ('_52', 'war_compass-0.3.0[]'), ('_51', 'war_anim-1.0.6[]'), ('_50', 'war_machine-1.0.5[]'), ('_57', 'wmPolyGoodies-4.04.1[0]'), ('_56', 'docutils-0.14[]'), ('_55', 'war_maya_common-1.7.1[]'), ('_54', 'war_maya-1.0.0[]'), ('_28', 'vray_for_maya-4.12.1.1[0]'), ('_29', 'six-1.10.0[]'), ('_26', 'mtoa-2019.2.0[0]'), ('_27', 'chaosgroup_license-1.0.0[]'), ('_24', 'maya_live_link-2.0[3]'), ('_25', 'mgear-3.1.1[0]'), ('_22', 'autodesk_license-1.0.0[]'), ('_23', 'maya-2019.2.0[0]'), ('_20', 'platform-windows[]'), ('_21', 'arch-AMD64[]'), ('_48', 'war_unreal-1.3.3[]'), ('_49', 'war_scene-4.4.0[]'), ('_40', 'ffmpeg-4.0.2[0]'), ('_41', 'enum34-1.1.6[]'), ('_42', 'future-0.16.0[0]'), ('_43', 'ffmpeg_python-0.2.0[]'), ('_44', 'requests-2.14.2[]'), ('_45', 'war_foundations-2.36.1[]'), ('_46', 'war_menu-1.4.1[]'), ('_47', 'war_assets-2.4.0[]')]), ((('fillcolor', '#F6F6F6'), ('fontsize', 10), ('style', 'filled,dashed')), [('_99', 'war_maya_common-1'), ('_98', 'docutils-0.14'), ('_97', 'war_maya-1'), ('_96', 'war_scene-4'), ('_95', 'war_machine-1'), ('_94', 'war_unreal-1'), ('_93', 'war_assets-2'), ('_92', 'war_foundations'), ('_91', 'enum34'), ('_90', 'war_qt-1'), ('_69', 'autodesk_license-1.0.0'), ('_88', 'anytree-2.2.2'), ('_89', 'war_foundations-2'), ('_84', 'requests-2.14.2'), ('_85', 'rez_api-2.47.2'), ('_86', 'war-1'), ('_87', 'shotgun_api3'), ('_80', 'enum34-1.1.6'), ('_81', 'ffmpeg_python-0.2.0'), ('_82', 'jsonschema-2.6.0'), ('_83', 'p4python-2017.2.1615960'), ('_108', 'wmVertCopy-2.6.1'), ('_107', 'wmModels-1.8.1'), ('_102', 'shotgun_api3-3.0.40'), ('_103', 'war_assets-2.1+'), ('_104', 'AsfAmc-0.33.11'), ('_105', 'wmAnim-1.51.2'), ('_106', 'wmMisc-6.17.1'), ('_79', 'future-0.16.0'), ('_78', 'ffmpeg-4.0.2'), ('_75', 'python-2.7'), ('_74', 'six-1.10.0'), ('_77', 'qt_py-1.2.2'), ('_76', 'functools32-3.2.3.post2'), ('_71', 'arch-AMD64'), ('_70', 'platform-windows'), ('_73', 'chaosgroup_license-1.0.0'), ('_72', 'maya-2019'), ('_100', 'wmPolyGoodies-4.04'), ('_101', 'rv-7.3.1')]), ((('fillcolor', '#FFFFAA'), ('fontsize', 10), ('style', 'filled,dashed')), [('_9', 'war_maya_blendshapeRecv-2'), ('_8', 'war_compass-0.3.0'), ('_7', 'war_anim-1.0.6'), ('_6', 'vray_for_maya-4.12.1.1'), ('_5', 'mtoa-2019.2.0'), ('_4', 'mgear-3.1.1'), ('_3', 'maya-2019.2.0'), ('_2', 'maya_live_link-2.0'), ('_1', 'maya_common_fishbowl-0.1.0'), ('_17', '~arch==AMD64'), ('_16', '~platform==windows'), ('_15', 'weta_maya_models-0.2.0'), ('_14', 'weta_cre-1.2.1'), ('_13', 'war_scene_maya-4'), ('_12', 'war_ocio-2'), ('_11', 'war_menu-1'), ('_10', 'war_maya_validation-4'), ('_18', '~os==windows-10.0.18362')])], 'edges': [((('arrowsize', '0.5'),), [('_99', '_55'), ('_98', '_56'), ('_97', '_54'), ('_96', '_49'), ('_95', '_50'), ('_94', '_48'), ('_93', '_47'), ('_92', '_45'), ('_91', '_41'), ('_90', '_37'), ('_62', '_70'), ('_62', '_71'), ('_62', '_72'), ('_63', '_70'), ('_63', '_71'), ('_63', '_72'), ('_60', '_70'), ('_60', '_71'), ('_61', '_80'), ('_61', '_77'), ('_61', '_101'), ('_61', '_102'), ('_61', '_103'), ('_61', '_99'), ('_61', '_96'), ('_61', '_11'), ('_61', '_94'), ('_66', '_70'), ('_66', '_71'), ('_66', '_72'), ('_67', '_104'), ('_67', '_105'), ('_67', '_106'), ('_67', '_107'), ('_67', '_108'), ('_64', '_70'), ('_64', '_71'), ('_64', '_72'), ('_65', '_70'), ('_65', '_71'), ('_65', '_72'), ('_68', '_11'), ('_69', '_22'), ('_88', '_30'), ('_89', '_45'), ('_84', '_44'), ('_85', '_35'), ('_86', '_39'), ('_87', '_38'), ('_80', '_41'), ('_81', '_43'), ('_82', '_34'), ('_83', '_32'), ('_108', '_64'), ('_9', '_53'), ('_8', '_52'), ('_7', '_51'), ('_6', '_28'), ('_5', '_26'), ('_4', '_25'), ('_3', '_23'), ('_2', '_24'), ('_1', '_19'), ('_107', '_62'), ('_17', '_21'), ('_16', '_20'), ('_15', '_68'), ('_14', '_67'), ('_13', '_61'), ('_12', '_59'), ('_11', '_46'), ('_10', '_58'), ('_102', '_38'), ('_103', '_47'), ('_104', '_65'), ('_105', '_66'), ('_106', '_63'), ('_30', '_74'), ('_32', '_70'), ('_32', '_71'), ('_32', '_75'), ('_35', '_70'), ('_35', '_71'), ('_35', '_75'), ('_34', '_76'), ('_34', '_70'), ('_34', '_71'), ('_34', '_75'), ('_37', '_77'), ('_58', '_98'), ('_58', '_89'), ('_58', '_99'), ('_58', '_11'), ('_58', '_90'), ('_58', '_100'), ('_53', '_70'), ('_53', '_71'), ('_53', '_72'), ('_52', '_89'), ('_51', '_89'), ('_51', '_95'), ('_51', '_96'), ('_51', '_11'), ('_50', '_89'), ('_57', '_70'), ('_57', '_71'), ('_57', '_72'), ('_55', '_74'), ('_55', '_89'), ('_55', '_97'), ('_28', '_73'), ('_28', '_70'), ('_28', '_71'), ('_28', '_72'), ('_26', '_3'), ('_26', '_70'), ('_26', '_71'), ('_24', '_70'), ('_24', '_71'), ('_24', '_72'), ('_25', '_70'), ('_25', '_71'), ('_23', '_69'), ('_23', '_70'), ('_23', '_71'), ('_48', '_92'), ('_49', '_80'), ('_49', '_93'), ('_49', '_89'), ('_49', '_94'), ('_40', '_70'), ('_40', '_71'), ('_42', '_70'), ('_42', '_71'), ('_42', '_75'), ('_43', '_78'), ('_43', '_79'), ('_43', '_74'), ('_45', '_80'), ('_45', '_81'), ('_45', '_82'), ('_45', '_83'), ('_45', '_84'), ('_45', '_85'), ('_45', '_74'), ('_45', '_86'), ('_45', '_87'), ('_46', '_88'), ('_46', '_74'), ('_46', '_89'), ('_46', '_90'), ('_47', '_74'), ('_47', '_91'), ('_79', '_42'), ('_78', '_40'), ('_75', '_31'), ('_74', '_29'), ('_77', '_36'), ('_76', '_33'), ('_71', '_21'), ('_70', '_20'), ('_73', '_27'), ('_72', '_23'), ('_100', '_57'), ('_101', '_60')])]}\\np714\\nsVpackage_paths\\np715\\n(lp716\\nVC:\\\\u005cUsers\\\\u005cnathan\\\\u005cPackages\\np717\\naVC:\\\\u005cUsers\\\\u005cnathan\\\\u005cUserPackages\\np718\\naVY:\\\\u005c\\np719\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cFishbowl\\np720\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cPerforce\\np721\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cProjects\\np722\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cThirdParty\\np723\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cWeta\\np724\\naVS:\\\\u005cPackages\\\\u005cFishbowl\\np725\\naVS:\\\\u005cPackages\\\\u005cPerforce\\np726\\naVS:\\\\u005cPackages\\\\u005cProjects\\np727\\naVS:\\\\u005cPackages\\\\u005cThirdParty\\np728\\naVS:\\\\u005cPackages\\\\u005cWeta\\np729\\nasVplatform\\np730\\nVwindows\\np731\\nsVrez_path\\np732\\nVc:\\\\u005cprogra~1\\\\u005crez\\\\u005clib\\\\u005csite-packages\\\\u005crez\\np733\\nsVpatch_locks\\np734\\n(dp735\\nsVdefault_patch_lock\\np736\\nVno_lock\\np737\\nsVsuite_context_name\\np738\\nNsVserialize_version\\np739\\nV4.3\\np740\\nsVtimestamp\\np741\\nI1587509795\\nsVhost\\np742\\nVSNAPE\\np743\\nsVuser\\np744\\nVnathan\\np745\\nsVload_time\\np746\\nF0.0\\nsVpackage_filter\\np747\\n(lp748\\nsVarch\\np749\\nVAMD64\\np750\\nsVbuilding\\np751\\nI00\\nsVrequested_timestamp\\np752\\nNsVpackage_orderers\\np753\\nNsVpackage_requests\\np754\\n(lp755\\nVmaya_common_fishbowl-0.1.0\\np756\\naVmaya_live_link-2.0\\np757\\naVmaya-2019.2.0\\np758\\naVmgear-3.1.1\\np759\\naVmtoa-2019.2.0\\np760\\naVvray_for_maya-4.12.1.1\\np761\\naVwar_anim-1.0.6\\np762\\naVwar_compass-0.3.0\\np763\\naVwar_maya_blendshapeRecv-2\\np764\\naVwar_maya_validation-4\\np765\\naVwar_menu-1\\np766\\naVwar_ocio-2\\np767\\naVwar_scene_maya-4\\np768\\naVweta_cre-1.2.1\\np769\\naVweta_maya_models-0.2.0\\np770\\nasVfailure_description\\np771\\nNsVcreated\\np772\\nI1587509795\\nsVstatus\\np773\\nVsolved\\np774\\nsVfrom_cache\\np775\\nI00\\nsVcaching\\np776\\nI01\\nsVos\\np777\\nVwindows-10.0.18362\\np778\\ns.\"\nendStream\nendChannel\nendAssociations\n" 
		-scn;
// End of Ctrl.ma
