# Windows-to-Android Conversion Template

## 1. Purpose

This repository is a reusable GitHub template for inspecting,
analyzing, converting, porting, or rebuilding Windows applications
for Android.

The objective is to automate as much of the process as practical
using GitHub Actions, reusable scripts, automated testing, and
optional AI-assisted development.

## 2. Primary Objectives

- Accept Windows application source projects as ZIP uploads.
- Safely extract and inspect submitted projects.
- Identify programming languages, frameworks, dependencies,
  build systems, and application entry points.
- Assess Android compatibility.
- Generate compatibility reports and conversion plans.
- Recommend an appropriate conversion strategy.
- Require approval before significant modifications.
- Preserve the original source code.
- Reuse existing Android build and testing workflows where practical.
- Generate Android APK artifacts when the converted project
  supports Android.
- Produce clear reports, logs, and handover documentation.

## 3. Supported Conversion Strategies

The workflow should evaluate four strategies:

1. Existing cross-platform Android build.
2. Porting reusable application code to Android.
3. Rebuilding the application using an Android-compatible framework.
4. Reusing a suitable existing web interface through an Android WebView.

The workflow must not assume that every Windows application
can be converted directly.

## 4. Initial Input Requirements

The system should support:

- ZIP archives containing application source code.
- Public GitHub repository source archives.
- Project documentation and build instructions.
- Optional application logos and other permitted assets.
- Optional user-provided conversion requirements.

Precompiled Windows executables may be inspected separately,
but their presence does not guarantee that the application
can be ported to Android.

## 5. Automation Requirements

GitHub Actions should progressively automate:

- Input validation.
- Safe archive extraction.
- Project and framework detection.
- Dependency inspection.
- Compatibility analysis.
- Conversion planning.
- Android project validation.
- Available automated tests.
- APK compilation.
- Artifact publication.
- Failure reporting and handover documentation.

AI-assisted code modification must be treated as a separate,
configurable capability.

## 6. Approval Requirements

The workflow must provide approval gates before:

- Replacing or substantially modifying application code.
- Changing the selected conversion strategy.
- Adding significant dependencies.
- Removing original application features.
- Publishing or distributing a converted application.

Routine validation and reporting may run automatically.

## 7. Security Requirements

- Never execute uploaded source code during initial inspection.
- Validate archive paths before extracting files.
- Reject unsafe archive entries and unexpected file types.
- Apply file-size and extraction limits.
- Do not expose secrets in logs or build artifacts.
- Never commit signing keys, passwords, or API tokens.
- Use least-privilege GitHub Actions permissions.
- Review dependencies and build scripts before execution.
- Preserve the original source separately from converted code.

## 8. Licensing Requirements

Before modifying or distributing an application:

- Identify its original licence where possible.
- Record attribution and redistribution requirements.
- Check third-party dependency licences.
- Flag missing or unclear licensing information.
- Do not assume that publicly available source code
  may be redistributed without restrictions.

## 9. Testing Requirements

The workflow should distinguish between:

- Source inspection completed.
- Static checks completed.
- Unit tests passed.
- Android compilation succeeded.
- APK artifact generated.
- Emulator tests passed.
- Physical-device testing completed.

A successful build must not be reported as proof that the
application works correctly on an Android device.

## 10. Implementation Priorities

Priority 1:
Repository structure, documentation, and safe ZIP intake.

Priority 2:
Automated project detection and compatibility reporting.

Priority 3:
Conversion plans and approval gates.

Priority 4:
Android project preparation and build integration.

Priority 5:
Optional AI-assisted code conversion.

Priority 6:
Automated testing, reporting, and reusable handovers.

## 11. Cost Requirements

Prefer free GitHub features and open-source tools where practical.

Do not assume unlimited GitHub Actions usage or free access
to commercial AI APIs.

Document any service, account, usage, or payment requirements
before enabling them.

## 12. Operating Principles

- Preserve original source code.
- Prefer the simplest viable conversion strategy.
- Avoid unnecessary dependencies.
- Use reproducible build procedures.
- Report failures honestly.
- Require human approval for consequential changes.
- Keep instructions suitable for a user working primarily
  from an Android phone.
