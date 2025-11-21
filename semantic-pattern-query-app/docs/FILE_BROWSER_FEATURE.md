# File Browser Feature

## Overview
Implemented a file browser interface that allows users to browse and view pattern library documents directly in the web UI. Files are displayed in the same window with markdown rendering for `.md` files.

## Features

### 1. Directory Browsing
- Browse folders within allowed directories
- Navigate up/down directory tree
- Visual file/folder icons
- Hover effects for better UX

### 2. File Viewing
- Click any file to view its content in the same window
- Markdown files (`.md`) are rendered with proper formatting
- Other files display as plain text with monospace font
- "Back to list" button to return to directory view

### 3. Security
- All paths validated against allowed directories
- Same security model as document content endpoint
- Directory traversal attacks prevented

## Components

### Frontend Components

#### [FileBrowser.tsx](../web-ui/src/components/FileBrowser.tsx)
Main file browser component that:
- Lists directory contents
- Handles file/folder navigation
- Displays file content with markdown rendering
- Shows loading states and error messages

**Props:**
- `initialPath`: Starting directory path
- `title`: Display title for the browser

#### [BrowsePanel.tsx](../web-ui/src/components/BrowsePanel.tsx)
Navigation panel with quick links to:
- 📁 RAG Patterns directory
- 💼 Use Cases directory
- 🏢 Vendor Guides directory

### Backend API

#### GET `/directory/contents`

Lists contents of a directory within allowed base directories.

**Query Parameters:**
- `path` (string): Directory path to list (empty string returns allowed base directories)

**Response:**
```json
{
  "items": [
    {
      "name": "README.md",
      "path": "/full/path/to/README.md",
      "type": "file",
      "extension": "md"
    },
    {
      "name": "patterns",
      "path": "/full/path/to/patterns",
      "type": "directory"
    }
  ]
}
```

**Security:**
- Path validation using `validate_path_security()` helper
- Only allowed directories are accessible
- Returns 403 for unauthorized paths
- Returns 404 for non-existent directories

## User Experience

### Browse Flow

1. **Select Category**: User clicks one of the browse buttons (Patterns, Use Cases, or Vendor Guides)
2. **View Directory**: System displays list of files and folders
3. **Navigate**: User can:
   - Click folders to enter them
   - Click "⬆ Up" button to go to parent directory
   - Click files to view content
4. **View File**: Selected file opens in same window with:
   - File name as header
   - Full path shown
   - Content rendered (markdown or plain text)
   - "← Back to list" button to return
5. **Return**: Click back button to return to directory listing

### File Icons

- 📁 Directories
- 📝 Markdown files (`.md`)
- 📋 JSON files (`.json`)
- 🐍 Python files (`.py`)
- ⚛️ JavaScript/TypeScript files (`.js`, `.jsx`, `.ts`, `.tsx`)
- 📄 Other files

## Implementation Details

### Security Model

```python
def get_allowed_directories():
    """Get list of allowed base directories for security."""
    return [
        Path(os.getenv("PATTERN_LIBRARY_PATH", "../pattern-library")).resolve(),
        Path("./docs").resolve(),
        Path("./semantic-pattern-query-app/docs").resolve(),
    ]

def validate_path_security(path: str, allowed_dirs: List[Path]) -> Path:
    """
    Validate that a path is within allowed directories.
    Returns resolved absolute path or raises HTTPException.
    """
    resolved_path = Path(path).resolve()
    is_allowed = any(
        str(resolved_path).startswith(str(allowed_dir))
        for allowed_dir in allowed_dirs
    )
    if not is_allowed:
        logger.warning(f"Blocked access to unauthorized path: {path}")
        raise HTTPException(status_code=403, detail="Access denied")
    return resolved_path
```

### File Type Detection

```typescript
const getFileIcon = (item: FileItem): string => {
  if (item.type === "directory") return "📁";
  const ext = item.extension?.toLowerCase();
  if (ext === "md") return "📝";
  if (ext === "json") return "📋";
  if (ext === "py") return "🐍";
  if (ext === "ts" || ext === "tsx" || ext === "js" || ext === "jsx") return "⚛️";
  return "📄";
};
```

### Markdown vs Plain Text Rendering

```typescript
{selectedFile.extension === "md" ? (
  <div className="markdown-content">
    <ReactMarkdown>{selectedFile.content}</ReactMarkdown>
  </div>
) : (
  <pre style={{ /* monospace styling */ }}>
    {selectedFile.content}
  </pre>
)}
```

## API Endpoints Summary

| Endpoint | Method | Purpose | Security |
|----------|--------|---------|----------|
| `/directory/contents` | GET | List directory contents | Path validation |
| `/document/content` | GET | Fetch file content | Path validation |

## Directory Structure

The browser is configured to access these directories:

```
/Users/sanantha/SummarizerArchitecture/pattern-library/
├── patterns/          (RAG Patterns)
├── use-cases/         (Use Cases)
└── vendor-guides/     (Vendor Guides)
```

## Testing

### Test Directory Listing
```bash
curl "http://localhost:8000/directory/contents?path=/Users/sanantha/SummarizerArchitecture/pattern-library/use-cases"
```

**Expected Response:**
```json
{
  "items": [
    {
      "name": "README.md",
      "path": "/Users/sanantha/SummarizerArchitecture/pattern-library/use-cases/README.md",
      "type": "file",
      "extension": "md"
    },
    {
      "name": "clinical-note-generation.md",
      "path": "...",
      "type": "file",
      "extension": "md"
    }
  ]
}
```

### Test File Content
```bash
curl "http://localhost:8000/document/content?path=/Users/sanantha/SummarizerArchitecture/pattern-library/use-cases/README.md"
```

### Test Security (Should Fail)
```bash
curl "http://localhost:8000/directory/contents?path=/etc"
```

**Expected Response:**
```json
{"detail": "Access denied: Path outside allowed directories"}
```

## Integration with Existing Features

The file browser integrates seamlessly with:

1. **SourcesList Component**: Uses same document content API and markdown rendering
2. **TierBreakdown Component**: Uses same document content API
3. **Security Model**: Shares path validation with document viewer
4. **Markdown Rendering**: Reuses existing ReactMarkdown setup and CSS

## Future Enhancements

Potential improvements:

1. **Search**: Add search functionality within directories
2. **Breadcrumbs**: Show full path with clickable breadcrumbs
3. **Favorites**: Allow users to bookmark frequently accessed files
4. **File Metadata**: Show file size, last modified date
5. **Download**: Add option to download files
6. **Syntax Highlighting**: Add code syntax highlighting for source files
7. **Tree View**: Show directory tree in sidebar
8. **Keyboard Navigation**: Arrow keys to navigate files

## Status

✅ **Implemented and working** (2025-11-21)
- Directory browsing with path validation
- File viewing in same window
- Markdown rendering for `.md` files
- Security validation for all paths
- Three browse categories (Patterns, Use Cases, Vendor Guides)
- Visual file type icons
- Responsive hover effects

## Related Features

- [Clickable Document Links](CLICKABLE_DOCUMENT_LINKS.md) - Document viewer modal
- [Markdown Rendering](MARKDOWN_RENDERING.md) - Markdown display system
- [Security Path Validation](SECURITY_PATH_VALIDATION.md) - Security model

The file browser provides an intuitive way for users to explore the pattern library documentation directly within the web UI, with all security protections in place.
