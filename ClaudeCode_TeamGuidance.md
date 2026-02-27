# Minimal Guidance for Claude Code Users

**Author:** Nathan Askins
**Date:** 2026-01-27
**Scope:** Security, quality, and organization guidance for team collaboration

## Executive Summary

This document provides minimal, essential guidance for team members new to Claude Code. The philosophy is deliberately light-touch: enough guardrails to prevent security incidents and ineffective usage, while preserving space for organic discovery and personal workflow development.

The guidance is organized into five categories:
1. **Security DOs and DON'Ts** - Non-negotiable practices to protect credentials, code quality, and organizational assets
2. **Outcome-Focused Guidance** - Patterns that distinguish effective from ineffective Claude Code usage
3. **Organizational Considerations** - What stays in your control
4. **Quality Standards for Team Alignment** - Code style and review mindset for merge compatibility
5. **Organization Standards for Team Alignment** - File naming and structure for codebase collaboration

## Part 1: Security DOs and DON'Ts

### NEVER (Hard Rules)

| DON'T | Why It Matters |
|-------|----------------|
| **Never paste credentials, API keys, or secrets into prompts** | Claude Code conversations may be logged or analyzed. Treat the prompt like a public channel. |
| **Never approve code changes without understanding them** | Claude Code can make mistakes. You are accountable for what gets committed, not Claude. |
| **Never commit .env, credentials.json, or secrets files** | Claude may suggest adding files to git that should never be tracked. Review every commit. |
| **Never skip code review because "Claude wrote it"** | AI-generated code requires the same review rigor as human code. Often more. |
| **Never let Claude push to production without your explicit review** | Claude can execute git commands. Understand what's being pushed before approving. |

### ALWAYS (Hard Rules)

| DO | Why It Matters |
|----|----------------|
| **Keep credentials in environment variables or secrets files** | Reference them by name, never by value. Say "use the API key from .env" not the actual key. |
| **Review every file change before accepting** | Use the diff view. Understand what changed. Reject changes you don't understand. |
| **Understand before approving** | If Claude suggests something you don't understand, ask it to explain. Don't approve mystery code. |
| **Verify Claude's claims about external systems** | If Claude says "this API returns X" - verify it. Claude can be confidently wrong. |
| **Use your own judgment for destructive operations** | Deleting files, dropping tables, force-pushing - these require your explicit decision, not delegation. |

## Part 2: Outcome-Focused Guidance

### What Makes Claude Code Effective

These are not rules - they are patterns observed in effective usage. Discover what works for you.

**1. Be Specific About Context**

Claude Code works on your codebase. It sees your files. But it doesn't know:
- Why you're making this change
- What the business requirements are
- What you've already tried
- What constraints exist

The more context you provide, the better the results. But you'll discover your own balance - some people front-load context, others iterate.

**2. Iterate Rather Than Expecting Perfection**

First responses are starting points, not final products. Effective users:
- Treat Claude's output as a draft
- Provide feedback on what didn't work
- Refine through conversation
- Know when to take over manually

**3. Understand Your Authority**

You are the decision-maker. Claude Code is a tool. This means:
- You decide what gets committed
- You decide what approach to take
- You can reject any suggestion
- You can redirect at any time

Don't feel obligated to follow Claude's suggestions if they don't feel right.

**4. Know When Claude Struggles**

Claude Code tends to be less effective when:
- The context is too large for it to hold in memory
- The problem requires knowledge of systems Claude can't access
- The codebase has unusual or undocumented conventions
- The task requires real-time data or external verification

Recognizing these situations saves time.

**5. Know When Claude Excels**

Claude Code tends to be highly effective for:
- Boilerplate and scaffolding
- Explaining unfamiliar code
- Suggesting refactoring approaches
- Writing tests for existing code
- Documentation generation
- Exploring "what if" scenarios quickly

### Anti-Patterns to Avoid

These patterns tend to produce poor outcomes:

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Accepting all suggestions without review | Review changes line by line |
| Asking Claude to "just fix it" with no context | Describe what's wrong and what you expect |
| Ignoring Claude's questions | Answer them - they often reveal important clarifications |
| Fighting with Claude when it's stuck | Take over manually, or try a fresh conversation |
| Using Claude for tasks you don't understand | Use Claude to learn, then apply what you've learned |

## Part 3: Organizational Considerations

### What Stays in Your Control

- **Commits**: You decide what gets committed, when, and with what message
- **Merges**: You decide when code is ready for integration
- **Deployment**: You decide when and what goes to production
- **Architecture**: Major decisions require human judgment

### Code Quality Expectations

Code written with Claude Code assistance is held to the same standard as any other code:
- Must pass code review
- Must have appropriate tests
- Must follow team conventions
- Must be maintainable by humans

"Claude wrote it" is not a justification for lower quality.

### Sharing and Learning

- Share useful prompts and patterns with teammates
- Discuss what's working and what isn't
- Don't assume your approach is the only valid one
- Learn from each other's discoveries

## Part 4: Quality Standards for Team Alignment

These standards ensure code produced with Claude Code assistance can merge cleanly with the team codebase.

### Code Style (Non-Negotiable for Merge Compatibility)

| Element | Standard |
|---------|----------|
| **Indentation** | Tabs, not spaces (all languages) |
| **Python functions/variables** | snake_case |
| **Python classes** | PascalCase |
| **Python constants** | UPPER_SNAKE_CASE |
| **Configurable scripts** | Use a Config class for settings |
| **Windows console scripts** | Must wait for user input before exiting |

### Code Review Mindset

When reviewing Claude-generated code, check for:

- **Modularity**: Single-responsibility functions/classes
- **Readability**: Self-documenting with clear naming
- **DRY principle**: No code duplication
- **Error handling**: Graceful failures with user-friendly messages

### Security Checklist

| Security Risk | Required Practice |
|---------------|-------------------|
| SQL injection | Always use parameterized queries |
| Path traversal | Validate and sanitize file paths |
| Command injection | Never use `shell=True` with user input |
| Credential exposure | Never hardcode credentials or API keys |
| Input validation | Validate all external input |

### Anti-Patterns to Flag

Code reviewers should flag these patterns for revision:

| Anti-Pattern | Problem |
|--------------|---------|
| Mutable default arguments | `def f(items=[])` - defaults persist across calls |
| Bare except clauses | `except:` catches everything including KeyboardInterrupt |
| SELECT * in SQL | Returns unnecessary data, breaks on schema changes |
| String concatenation for SQL | `f"SELECT * FROM {table}"` - SQL injection risk |

## Part 5: Organization Standards for Team Alignment

These standards ensure file organization is consistent across team contributions.

### Directory Naming

| Convention | Examples |
|------------|----------|
| PascalCase for directories | AgentWork/, TeamKnowledge/, Scripts/ |
| Dot-prefix for system folders | .staging/, .cache/, .archive/ |
| Never underscore-prefix | ~~_staging/~~ causes Markdown rendering issues |

### File Naming by Type

| File Type | Convention | Example |
|-----------|------------|---------|
| Python scripts | snake_case.py | data_processor.py |
| Markdown docs | PascalCase.md | WorkflowGuide.md |
| JSON configs | PascalCase.json | ProjectSettings.json |
| Reports | Description_YYYY-MM-DD.md | StatusUpdate_2026-01-27.md |

**Critical**: Timestamps are ALWAYS suffixes, never prefixes.

### File Versioning Convention

| Situation | What to Do |
|-----------|------------|
| Working file | Keep the base name (no version suffix) |
| Before editing | Create a versioned backup (file_v1.2.ext) |
| Making changes | Edit the base file, not the version |

### Documentation Rules

| Rule | Rationale |
|------|-----------|
| Author attribution: Nathan Askins | External stakeholders see this work |
| No horizontal rules (---) in markdown | Use headings for section separation instead |

## Summary: The Minimal Rules

If you remember nothing else:

**Security:**
1. **Never expose credentials** - treat prompts like public channels
2. **Always review changes** - you're accountable for what gets committed
3. **Understand before approving** - don't accept mystery code

**Effectiveness:**
4. **Iterate and refine** - first responses are starting points
5. **Stay in control** - Claude is a tool, you're the decision-maker

**Team Collaboration:**
6. **Use tabs for indentation** - non-negotiable for merge compatibility
7. **Follow naming conventions** - snake_case for Python, PascalCase for docs
8. **Timestamp suffix, not prefix** - Description_YYYY-MM-DD.md

Everything else is for you to discover.

## Sources Referenced

| File | Section |
|------|---------|
| C:\cl\Governance\UniversalPermissions.json | Safety guardrails, absolute prohibitions |
| C:\cl\Governance\SpockStandards.json | Code quality standards, anti-patterns, security checklist |
| C:\cl\Governance\AlfredStandards.json | File naming, directory structure, versioning conventions |
| C:\cl\TeamKnowledge\BestPractices\Security_Guidelines_LLM_Access.md | Credential security patterns |
| C:\cl\TeamKnowledge\BestPractices\MacGyver_Git_Operations_Guide.md | Git operation safety |
