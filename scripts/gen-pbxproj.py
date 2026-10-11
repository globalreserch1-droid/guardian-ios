#!/usr/bin/env python3
"""Generate Guardian.xcodeproj/project.pbxproj with deterministic UUIDs."""
import uuid

NS = uuid.uuid5(uuid.NAMESPACE_DNS, "blanketguard.guardian.ios")

def uid(name):
    return uuid.uuid5(NS, name).hex[:24].upper()

# --- identifiers -------------------------------------------------------------
ID = {}
for n in [
    "PBXProject", "PBXNativeTarget",
    "PBXGroup:main", "PBXGroup:Guardian", "PBXGroup:Products",
    "PBXSourcesBuildPhase", "PBXResourcesBuildPhase", "PBXFrameworksBuildPhase",
    "XCConfigurationList:project", "XCConfigurationList:target",
    "XCBuildConfiguration:project:Debug", "XCBuildConfiguration:project:Release",
    "XCBuildConfiguration:target:Debug", "XCBuildConfiguration:target:Release",
    "PBXFileReference:Guardian.app",
    "PBXFileReference:AppDelegate.swift", "PBXFileReference:ViewController.swift",
    "PBXFileReference:Info.plist", "PBXFileReference:Assets.xcassets",
    "PBXFileReference:www",
    "PBXFileReference:WebKit.framework", "PBXFileReference:CoreLocation.framework",
    "PBXFileReference:MessageUI.framework", "PBXFileReference:UserNotifications.framework",
    "PBXBuildFile:AppDelegate.swift", "PBXBuildFile:ViewController.swift",
    "PBXBuildFile:Assets.xcassets", "PBXBuildFile:www",
    "PBXBuildFile:WebKit.framework", "PBXBuildFile:CoreLocation.framework",
    "PBXBuildFile:MessageUI.framework", "PBXBuildFile:UserNotifications.framework",
]:
    ID[n] = uid(n)

swift_flags = """isa = PBXBuildFile; fileRef = %s; """ % "{}"

objects = []

# --- PBXBuildFile ------------------------------------------------------------
buildfiles = [
    ("PBXBuildFile:AppDelegate.swift", "PBXFileReference:AppDelegate.swift", None),
    ("PBXBuildFile:ViewController.swift", "PBXFileReference:ViewController.swift", None),
    ("PBXBuildFile:Assets.xcassets", "PBXFileReference:Assets.xcassets", None),
    ("PBXBuildFile:www", "PBXFileReference:www", None),
    ("PBXBuildFile:WebKit.framework", "PBXFileReference:WebKit.framework", None),
    ("PBXBuildFile:CoreLocation.framework", "PBXFileReference:CoreLocation.framework", None),
    ("PBXBuildFile:MessageUI.framework", "PBXFileReference:MessageUI.framework", None),
    ("PBXBuildFile:UserNotifications.framework", "PBXFileReference:UserNotifications.framework", None),
]
for b, f, _ in buildfiles:
    objects.append(
        "\t\t%s /* %s */ = {isa = PBXBuildFile; fileRef = %s /* %s */; };" % (
            ID[b], b.split(":", 1)[1], ID[f], f.split(":", 1)[1]))

# --- PBXFileReference --------------------------------------------------------
filerefs = [
    ("PBXFileReference:Guardian.app", "Guardian.app", "wrapper.application", None, None),
    ("PBXFileReference:AppDelegate.swift", "AppDelegate.swift", "sourcecode.swift", "AppDelegate.swift", None),
    ("PBXFileReference:ViewController.swift", "ViewController.swift", "sourcecode.swift", "ViewController.swift", None),
    ("PBXFileReference:Info.plist", "Info.plist", "text.plist.xml", "Info.plist", None),
    ("PBXFileReference:Assets.xcassets", "Assets.xcassets", "folder.assetcatalog", "Assets.xcassets", None),
    ("PBXFileReference:www", "www", "folder", "www", None),
    ("PBXFileReference:WebKit.framework", "WebKit.framework", "wrapper.framework",
     "System/Library/Frameworks/WebKit.framework", "SDKROOT"),
    ("PBXFileReference:CoreLocation.framework", "CoreLocation.framework", "wrapper.framework",
     "System/Library/Frameworks/CoreLocation.framework", "SDKROOT"),
    ("PBXFileReference:MessageUI.framework", "MessageUI.framework", "wrapper.framework",
     "System/Library/Frameworks/MessageUI.framework", "SDKROOT"),
    ("PBXFileReference:UserNotifications.framework", "UserNotifications.framework", "wrapper.framework",
     "System/Library/Frameworks/UserNotifications.framework", "SDKROOT"),
]
for key, name, ftype, path, srctree in filerefs:
    if key == "PBXFileReference:Guardian.app":
        objects.append(
            "\t\t%s /* %s */ = {isa = PBXFileReference; explicitFileType = %s; "
            "includeInIndex = 0; path = %s; sourceTree = BUILT_PRODUCTS_DIR; };" % (
                ID[key], name, ftype, name))
    elif srctree:
        objects.append(
            "\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = %s; "
            "name = %s; path = \"%s\"; sourceTree = %s; };" % (
                ID[key], name, ftype, name, path, srctree))
    else:
        objects.append(
            "\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = %s; "
            "path = %s; sourceTree = \"<group>\"; };" % (
                ID[key], name, ftype, path or name))

# --- Build phases ------------------------------------------------------------
objects.append(
    "\t\t%s /* Sources */ = {isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; "
    "files = (\n\t\t\t%s /* AppDelegate.swift in Sources */,\n"
    "\t\t\t%s /* ViewController.swift in Sources */,\n\t\t); runOnlyForDeploymentPostprocessing = 0; };" % (
        ID["PBXSourcesBuildPhase"], ID["PBXBuildFile:AppDelegate.swift"],
        ID["PBXBuildFile:ViewController.swift"]))
objects.append(
    "\t\t%s /* Frameworks */ = {isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; "
    "files = (\n\t\t\t%s /* WebKit.framework in Frameworks */,\n"
    "\t\t\t%s /* CoreLocation.framework in Frameworks */,\n"
    "\t\t\t%s /* MessageUI.framework in Frameworks */,\n"
    "\t\t\t%s /* UserNotifications.framework in Frameworks */,\n\t\t); "
    "runOnlyForDeploymentPostprocessing = 0; };" % (
        ID["PBXFrameworksBuildPhase"], ID["PBXBuildFile:WebKit.framework"],
        ID["PBXBuildFile:CoreLocation.framework"],
        ID["PBXBuildFile:MessageUI.framework"],
        ID["PBXBuildFile:UserNotifications.framework"]))
objects.append(
    "\t\t%s /* Resources */ = {isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; "
    "files = (\n\t\t\t%s /* Assets.xcassets in Resources */,\n"
    "\t\t\t%s /* www in Resources */,\n\t\t); runOnlyForDeploymentPostprocessing = 0; };" % (
        ID["PBXResourcesBuildPhase"], ID["PBXBuildFile:Assets.xcassets"],
        ID["PBXBuildFile:www"]))

# --- Groups ------------------------------------------------------------------
objects.append(
    "\t\t%s = {isa = PBXGroup; children = (\n\t\t\t%s /* Guardian */,\n"
    "\t\t\t%s /* Products */,\n\t\t); sourceTree = \"<group>\"; };" % (
        ID["PBXGroup:main"], ID["PBXGroup:Guardian"], ID["PBXGroup:Products"]))
objects.append(
    "\t\t%s /* Guardian */ = {isa = PBXGroup; children = (\n"
    "\t\t\t%s /* AppDelegate.swift */,\n\t\t\t%s /* ViewController.swift */,\n"
    "\t\t\t%s /* Info.plist */,\n\t\t\t%s /* Assets.xcassets */,\n"
    "\t\t\t%s /* www */,\n\t\t); path = Guardian; sourceTree = \"<group>\"; };" % (
        ID["PBXGroup:Guardian"], ID["PBXFileReference:AppDelegate.swift"],
        ID["PBXFileReference:ViewController.swift"], ID["PBXFileReference:Info.plist"],
        ID["PBXFileReference:Assets.xcassets"], ID["PBXFileReference:www"]))
objects.append(
    "\t\t%s /* Products */ = {isa = PBXGroup; children = (\n\t\t\t%s /* Guardian.app */,\n"
    "\t\t); name = Products; sourceTree = \"<group>\"; };" % (
        ID["PBXGroup:Products"], ID["PBXFileReference:Guardian.app"]))

# --- Target ------------------------------------------------------------------
objects.append(
    "\t\t%s /* Guardian */ = {isa = PBXNativeTarget; buildConfigurationList = %s /* "
    "Build configuration list for PBXNativeTarget \"Guardian\" */; buildPhases = (\n"
    "\t\t\t%s /* Sources */,\n\t\t\t%s /* Frameworks */,\n\t\t\t%s /* Resources */,\n"
    "\t\t); buildRules = (\n\t\t); dependencies = (\n\t\t); name = Guardian; "
    "productName = Guardian; productReference = %s /* Guardian.app */; "
    "productType = \"com.apple.product-type.application\"; };" % (
        ID["PBXNativeTarget"], ID["XCConfigurationList:target"],
        ID["PBXSourcesBuildPhase"], ID["PBXFrameworksBuildPhase"],
        ID["PBXResourcesBuildPhase"], ID["PBXFileReference:Guardian.app"]))

# --- Project -----------------------------------------------------------------
objects.append(
    "\t\t%s /* Project object */ = {isa = PBXProject; attributes = { "
    "LastUpgradeCheck = 1600; }; buildConfigurationList = %s /* Build configuration "
    "list for PBXProject \"Guardian\" */; compatibilityVersion = \"Xcode 14.0\"; "
    "developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en, ); "
    "mainGroup = %s; productRefGroup = %s /* Products */; projectDirPath = \"\"; "
    "projectRoot = \"\"; targets = (\n\t\t\t%s /* Guardian */,\n\t\t); };" % (
        ID["PBXProject"], ID["XCConfigurationList:project"],
        ID["PBXGroup:main"], ID["PBXGroup:Products"], ID["PBXNativeTarget"]))

# --- Configurations ----------------------------------------------------------
proj_common = """ALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 15.0;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_VERSION = 5.0;"""
tgt_common = """ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_IDENTITY = "";
\t\t\t\tCODE_SIGN_STYLE = Manual;
\t\t\t\tINFOPLIST_FILE = Guardian/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 15.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = "$(inherited) @executable_path/Frameworks";
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.blanketguard.guardian;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";"""
configs = [
    ("XCBuildConfiguration:project:Debug", "Debug", proj_common + """
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tONLY_ACTIVE_ARCH = YES;"""),
    ("XCBuildConfiguration:project:Release", "Release", proj_common + """
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tONLY_ACTIVE_ARCH = NO;"""),
    ("XCBuildConfiguration:target:Debug", "Debug", tgt_common + """
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tONLY_ACTIVE_ARCH = YES;"""),
    ("XCBuildConfiguration:target:Release", "Release", tgt_common + """
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tONLY_ACTIVE_ARCH = NO;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;"""),
]
for key, name, settings in configs:
    objects.append(
        "\t\t%s /* %s */ = {isa = XCBuildConfiguration; buildSettings = {\n\t\t\t\t%s\n"
        "\t\t\t}; name = %s; };" % (ID[key], name, settings, name))

objects.append(
    "\t\t%s /* Build configuration list for PBXProject \"Guardian\" */ = {"
    "isa = XCConfigurationList; buildConfigurations = (\n\t\t\t%s /* Debug */,\n"
    "\t\t\t%s /* Release */,\n\t\t); defaultConfigurationIsVisible = 0; "
    "defaultConfigurationName = Release; };" % (
        ID["XCConfigurationList:project"],
        ID["XCBuildConfiguration:project:Debug"],
        ID["XCBuildConfiguration:project:Release"]))
objects.append(
    "\t\t%s /* Build configuration list for PBXNativeTarget \"Guardian\" */ = {"
    "isa = XCConfigurationList; buildConfigurations = (\n\t\t\t%s /* Debug */,\n"
    "\t\t\t%s /* Release */,\n\t\t); defaultConfigurationIsVisible = 0; "
    "defaultConfigurationName = Release; };" % (
        ID["XCConfigurationList:target"],
        ID["XCBuildConfiguration:target:Debug"],
        ID["XCBuildConfiguration:target:Release"]))

# --- Assemble ----------------------------------------------------------------
section_order = [
    ("PBXBuildFile", "PBXBuildFile"),
    ("PBXFileReference", "PBXFileReference"),
    ("PBXFrameworksBuildPhase", "PBXFrameworksBuildPhase"),
    ("PBXGroup", "PBXGroup"),
    ("PBXNativeTarget", "PBXNativeTarget"),
    ("PBXProject", "PBXProject"),
    ("PBXResourcesBuildPhase", "PBXResourcesBuildPhase"),
    ("PBXSourcesBuildPhase", "PBXSourcesBuildPhase"),
    ("XCBuildConfiguration", "XCBuildConfiguration"),
    ("XCConfigurationList", "XCConfigurationList"),
]

def section_of(obj):
    for prefix, _ in section_order:
        if obj.strip().startswith("\t\t" + ID.get(prefix + ":x", "")[:0]):
            pass
    return None

by_section = {name: [] for _, name in section_order}
for obj in objects:
    placed = False
    for prefix, sname in section_order:
        # match by comment isa value
        if ("isa = %s;" % prefix) in obj:
            by_section[sname].append(obj)
            placed = True
            break
    if not placed:
        raise SystemExit("unplaced object: " + obj[:80])

out = []
out.append("// !$*UTF8*$!")
out.append("{")
out.append("\tarchiveVersion = 1;")
out.append("\tclasses = {")
out.append("\t};")
out.append("\tobjectVersion = 56;")
out.append("\tobjects = {")
for _, sname in section_order:
    if not by_section[sname]:
        continue
    out.append("")
    out.append("/* Begin %s section */" % sname)
    out.extend(sorted(by_section[sname]))
    out.append("/* End %s section */" % sname)
out.append("\t};")
out.append("\trootObject = %s /* Project object */;" % ID["PBXProject"])
out.append("}")

with open("project.pbxproj", "w") as f:
    f.write("\n".join(out) + "\n")
print("wrote project.pbxproj (%d objects)" % len(objects))
