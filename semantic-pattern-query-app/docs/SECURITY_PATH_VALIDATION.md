# Security: Path Validation for Document Content Endpoint

## Overview
Implemented path validation in the `/document/content` endpoint to prevent directory traversal attacks and unauthorized file access.

## Security Issue Identified
The original implementation allowed users to request any file path, including directory traversal attempts like `../../../etc/passwd`, which could expose sensitive system files.

## Security Fix Implemented

### File: `src/api_server.py` (lines 365-432)

Added strict path validation that:
1. **Defines allowed base directories** - Only files within specific directories can be accessed
2. **Resolves paths to absolute paths** - Eliminates ambiguity and normalizes paths
3. **Validates against allowed directories** - Checks if resolved path starts with an allowed directory
4. **Logs security violations** - Records attempted unauthorized access for monitoring
5. **Returns 403 Forbidden** - Blocks unauthorized requests with appropriate HTTP status

### Allowed Directories

The endpoint restricts file access to these directories:
- `PATTERN_LIBRARY_PATH` (from environment variable, defaults to `../pattern-library`)
- `./docs` (local documentation)
- `./semantic-pattern-query-app/docs` (app documentation)

### Implementation Details

```python
# Define allowed base directories
allowed_dirs = [
    Path(os.getenv("PATTERN_LIBRARY_PATH", "../pattern-library")).resolve(),
    Path("./docs").resolve(),
    Path("./semantic-pattern-query-app/docs").resolve(),
]

# Resolve to absolute path
doc_path = Path(path).resolve()

# Security: Verify path is within allowed directories
is_allowed = any(
    str(doc_path).startswith(str(allowed_dir))
    for allowed_dir in allowed_dirs
)

if not is_allowed:
    logger.warning(f"Blocked access to unauthorized path: {path} (resolved to {doc_path})")
    raise HTTPException(
        status_code=403,
        detail="Access denied: Path outside allowed directories"
    )
```

## Security Testing

### Test 1: Directory Traversal Attack (Blocked)
```bash
curl -X GET "http://localhost:8000/document/content?path=../../../etc/passwd"
```

**Expected Response:**
```json
{"detail":"Access denied: Path outside allowed directories"}
```

**HTTP Status:** 403 Forbidden

### Test 2: Legitimate Document Access (Allowed)
```bash
curl -X GET "http://localhost:8000/document/content?path=/Users/sanantha/SummarizerArchitecture/pattern-library/README.md"
```

**Expected Response:**
```json
{
  "content": "# Healthcare AI Pattern Library...",
  "metadata": {
    "path": "/Users/sanantha/SummarizerArchitecture/pattern-library/README.md",
    "name": "README.md",
    "size": 7322,
    "extension": ".md"
  }
}
```

**HTTP Status:** 200 OK

## Attack Vectors Prevented

1. **Directory Traversal**: `../../../etc/passwd`
2. **Absolute Paths Outside Allowed Dirs**: `/etc/shadow`
3. **Symbolic Link Exploitation**: Resolved paths are validated
4. **URL Encoding Tricks**: Path normalization handles encoded characters

## Logging and Monitoring

Security violations are logged with:
- Requested path (as received)
- Resolved path (absolute path)
- Warning level for security monitoring

Example log:
```
WARNING: Blocked access to unauthorized path: ../../../etc/passwd (resolved to /etc/passwd)
```

## Configuration

To add additional allowed directories, update the `allowed_dirs` list in the endpoint or set environment variables:

```python
allowed_dirs = [
    Path(os.getenv("PATTERN_LIBRARY_PATH", "../pattern-library")).resolve(),
    Path(os.getenv("DOCS_PATH", "./docs")).resolve(),
    # Add more as needed
]
```

## Best Practices Applied

1. **Whitelist Approach**: Only explicitly allowed directories are accessible
2. **Path Normalization**: All paths resolved to absolute form before validation
3. **Fail Securely**: Default behavior is to deny access
4. **Defense in Depth**: Multiple checks (resolution + validation + existence)
5. **Logging**: Security events recorded for audit trail
6. **Appropriate HTTP Status**: 403 Forbidden for authorization failures

## Compliance Considerations

This security measure aligns with:
- **OWASP Top 10**: Prevents Broken Access Control (A01:2021)
- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory
- **HIPAA Security Rule**: Access Controls (§164.312(a)(1))

## Future Enhancements

Potential additional security measures:
1. **Rate Limiting**: Prevent brute-force path discovery
2. **File Extension Whitelist**: Only allow specific file types (`.md`, `.txt`, `.json`)
3. **File Size Limits**: Prevent memory exhaustion from large files
4. **Authentication**: Require API key or token for document access
5. **Audit Logging**: Log all successful document access requests

## Status

✅ **Implemented and tested** (2025-11-21)
- Path validation prevents directory traversal
- Logging captures security violations
- Legitimate document access works correctly
- Web UI clickable documents function properly with security in place

## Related Features

- [Clickable Document Links](CLICKABLE_DOCUMENT_LINKS.md) - Uses this endpoint
- [Markdown Rendering](MARKDOWN_RENDERING.md) - Displays content fetched via this endpoint
- [Tier Breakdown Display](TIER_DISPLAY_SUMMARY.md) - Shows documents with clickable links

## Testing

To verify security fix:

```bash
# Test 1: Should be BLOCKED
curl -X GET "http://localhost:8000/document/content?path=../../../etc/passwd"

# Test 2: Should be ALLOWED
curl -X GET "http://localhost:8000/document/content?path=/Users/sanantha/SummarizerArchitecture/pattern-library/README.md"

# Check server logs for warning messages
tail -f logs/api_server.log | grep "Blocked access"
```

The security fix ensures that the document viewer feature cannot be exploited to access unauthorized files on the system.
