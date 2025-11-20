# Changelog Documentation

This project maintains **two separate changelogs** with different purposes:

## CHANGELOG.md - Release Notes (High-Level)

**Purpose**: High-level release tracking for production releases

**Audience**: Users, stakeholders, project managers

**Content**:
- Major feature releases
- Breaking changes
- Key improvements
- Impact summaries
- Configuration examples
- Backward compatibility notes

**Format**: Clean, concise, marketing-friendly

**Updates**: Only when features are fully tested and production-ready

**Example Entry**:
```markdown
#### Web Search Enhancement - Trafilatura Integration (v1.1)

**Status**: ✅ Complete | 🚧 Testing Pending

**What Changed**: Enhanced web search with Trafilatura...

**Impact**:
- 10x More Content
- Better RAG Responses
- Zero Cost

**Files Modified**: 9 files, ~800 lines
```

## CHANGELOG_DEV.md - Development Log (Detailed)

**Purpose**: Detailed implementation tracking during active development

**Audience**: Developers, testers, technical contributors

**Content**:
- Implementation checklists
- Technical specifications
- Testing requirements
- Known issues & limitations
- Performance benchmarks
- Architecture diagrams
- Code snippets
- Troubleshooting notes
- Work-in-progress status

**Format**: Detailed, technical, granular

**Updates**: Continuous during development, archived when stable

**Example Entry**:
```markdown
#### Phase 3: Testing 🚧 PENDING

- [ ] Unit Tests - TrafilaturaProvider
  - [ ] Test provider initialization
  - [ ] Test trust scoring
  - [ ] Mock Trafilatura functions
  - Target file: tests/test_trafilatura_provider.py

- [ ] Integration Tests - Hybrid Mode
  - [ ] Test DuckDuckGo + Trafilatura
  - [ ] Test fallback scenarios
```

## Workflow

### During Active Development

1. **Work in progress** → Update CHANGELOG_DEV.md
   - Check off tasks as completed
   - Document issues encountered
   - Track technical decisions
   - Note performance metrics

2. **Feature complete** → Add high-level entry to CHANGELOG.md
   - Summarize what changed
   - Highlight impact
   - Link to CHANGELOG_DEV.md for details

### Before Release

1. **Testing complete** → Update status in both changelogs
   - CHANGELOG.md: Change status from "Testing Pending" to "Complete"
   - CHANGELOG_DEV.md: Check off all testing items

2. **Production deployment** → Archive development log
   - Condense CHANGELOG_DEV.md into CHANGELOG.md
   - Mark CHANGELOG_DEV.md section as "Historical"

## When to Use Which Changelog

### Use CHANGELOG.md When:
- User asks "What's new?"
- Preparing release notes
- Documenting breaking changes
- Communicating to non-technical stakeholders
- Creating marketing materials

### Use CHANGELOG_DEV.md When:
- Planning implementation work
- Tracking testing progress
- Debugging issues
- Onboarding new developers
- Conducting code reviews
- Performance tuning

## Navigation

- [CHANGELOG.md](CHANGELOG.md) - High-level release notes
- [CHANGELOG_DEV.md](CHANGELOG_DEV.md) - Detailed development log

## Benefits

**Two-Changelog Approach**:
- ✅ Clean release notes without implementation noise
- ✅ Detailed tracking without cluttering main changelog
- ✅ Easy to find information (choose right log for audience)
- ✅ Work-in-progress friendly (CHANGELOG_DEV.md)
- ✅ Production-ready friendly (CHANGELOG.md)

**Single-Changelog Approach** (What We Avoid):
- ❌ Release notes cluttered with TODO items
- ❌ Users confused by technical implementation details
- ❌ Hard to find high-level summaries
- ❌ Mixing audiences (users vs developers)
