# Architecture and Project Decisions

This document records important decisions made during the
development of the Windows-to-Android conversion template.

## Decision 001 — Reusable GitHub Template

Status: Accepted

The project will be developed as a reusable GitHub template
that can be copied for individual conversion projects.

Reason:
Separate projects must be able to use the same tested
automation without interfering with one another.

## Decision 002 — Phone-Friendly Operation

Status: Accepted

The primary management interface will be GitHub's website
and GitHub Actions.

Reason:
The workflow should be manageable from an Android phone
without requiring Android Studio on a local computer.

## Decision 003 — ZIP-Based Project Intake

Status: Accepted

The initial workflow will accept ZIP archives containing
Windows application source projects.

Reason:
ZIP uploads provide a simple handover method that does
not require local development tools.

## Decision 004 — Preserve Original Source

Status: Accepted

The original uploaded source must remain separate from
the converted project.

Reason:
This enables recovery, comparison, and troubleshooting.

## Decision 005 — Compatibility Before Conversion

Status: Accepted

The workflow must inspect the application and produce
a compatibility assessment before attempting conversion.

Reason:
Windows applications use different frameworks and
cannot all follow the same conversion process.

## Decision 006 — Approval Before Major Changes

Status: Accepted

Substantial modifications must require an explicit
approval step.

Reason:
The user must retain control over conversion strategy,
feature changes, and significant dependencies.

## Decision 007 — Reuse Existing Android Workflows

Status: Accepted

Where practical, the project should reuse or adapt
the user's existing Android build and testing workflows.

Reason:
This reduces duplication and supports consistent builds.

## Decision 008 — Optional AI Integration

Status: Accepted

AI-assisted conversion will be optional and must use
an explicitly configured service or implementation process.

Reason:
GitHub Actions does not automatically provide a free
AI coding agent.

## Decision 009 — Security During Inspection

Status: Accepted

Uploaded projects must undergo safe archive and file
inspection before potentially executable build scripts
or application code are run.

Reason:
Untrusted source projects may contain malicious scripts
or unsafe archive entries.

## Decision 010 — Build Success Is Not Device Validation

Status: Accepted

The workflow must report compilation, automated testing,
emulator testing, and physical-device testing separately.

Reason:
An APK that compiles successfully may still fail at runtime.

## Future Decisions

Record future architectural changes below.

Each decision should include:
- Decision number.
- Status.
- Description.
- Reason.
- Consequences, where relevant.
