# Clickable Document Links Feature

## Overview
Added clickable document links to the 3-Tier Retrieval Breakdown component. When users click on a document, a modal displays the full content fetched from the backend API.

## Changes Made

### 1. Frontend - TierBreakdown Component
**File**: `web-ui/src/components/TierBreakdown.tsx`

#### Added Features:
- **Clickable Documents**: All document items in the tier breakdown are now clickable with hover effects
- **Modal Dialog**: Full-screen modal to display document content
- **Loading State**: Shows "Loading document content..." while fetching
- **Error Handling**: Displays error messages if document fetch fails
- **Visual Feedback**:
  - Cursor changes to pointer on hover
  - Border color changes to match tier color
  - Slight horizontal translation on hover
  - Document icon (📄) added to each item

#### Key Code Changes:
```typescript
// State for selected document
const [selectedDoc, setSelectedDoc] = useState<{
  path: string;
  id: string;
  content: string;
  loading: boolean;
} | null>(null);

// Click handler to fetch and display document
const handleDocumentClick = async (source: SourceDocument) => {
  const path = source.source_path;
  if (!path) return;

  setSelectedDoc({
    path,
    id: source.document_id ?? "Unknown",
    content: "",
    loading: true,
  });

  try {
    const result = await fetchDocumentContent(path);
    setSelectedDoc((prev) =>
      prev
        ? { ...prev, content: result.content, loading: false }
        : null
    );
  } catch (error) {
    // Error handling
  }
};
```

### 2. Frontend - API Client
**File**: `web-ui/src/lib/api.ts`

Added new function to fetch document content:
```typescript
export async function fetchDocumentContent(
  documentPath: string
): Promise<{ content: string; metadata: Record<string, unknown> }> {
  const response = await fetch(
    `${API_BASE_URL}/document/content?path=${encodeURIComponent(documentPath)}`
  );
  return handleResponse<{ content: string; metadata: Record<string, unknown> }>(response);
}
```

### 3. Backend - API Endpoint
**File**: `src/api_server.py` (lines 365-412)

Added new GET endpoint `/document/content`:
```python
@app.get("/document/content")
async def get_document_content(path: str):
    """
    Fetch the full content of a document by its file path.

    Args:
        path: File path to the document

    Returns:
        Document content and metadata
    """
    from pathlib import Path

    try:
        # Resolve to absolute path
        doc_path = Path(path).resolve()

        # Check if file exists
        if not doc_path.exists() or not doc_path.is_file():
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Read file content (with fallback for encoding errors)
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(doc_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='replace')

        metadata = {
            "path": str(doc_path),
            "name": doc_path.name,
            "size": doc_path.stat().st_size,
            "extension": doc_path.suffix,
        }

        return {
            "content": content,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")
```

## User Experience

### Before
- Document IDs were displayed as plain text
- No way to view full document content from UI
- Users had to manually navigate to files

### After
1. **Hover**: Document items show visual feedback (color change, slight movement)
2. **Click**: Modal opens with loading indicator
3. **View**: Full document content displayed in scrollable modal
4. **Close**: Click outside modal, click X button, or click Close button

## Modal Features

- **Responsive Design**: Max width 900px, 90% viewport height
- **Scrollable Content**: Long documents scroll within modal
- **Header**: Shows document ID and file path
- **Formatted Content**: Monospace font with proper line wrapping
- **Easy Dismissal**: Multiple ways to close (ESC key not implemented yet)
- **Backdrop**: Semi-transparent dark overlay

## API Testing

Test the endpoint directly:
```bash
curl "http://localhost:8000/document/content?path=/path/to/document.md"
```

Response format:
```json
{
  "content": "Full document text...",
  "metadata": {
    "path": "/full/path/to/document.md",
    "name": "document.md",
    "size": 9152,
    "extension": ".md"
  }
}
```

## Security Considerations

- Path is resolved to absolute path to prevent directory traversal
- File existence is verified before reading
- UTF-8 encoding with fallback for binary files
- HTTP 404 returned for missing files
- HTTP 500 for read errors with sanitized error messages

## Future Enhancements

Potential improvements:
1. Add ESC key handler to close modal
2. Support markdown rendering instead of plain text
3. Add syntax highlighting for code files
4. Add copy-to-clipboard button
5. Show file metadata in modal (size, modified date)
6. Add navigation between documents (prev/next)
7. Cache fetched documents to avoid re-fetching

## Status

✅ **Implemented and tested**
- Frontend component with clickable links
- Modal dialog with full content display
- Backend API endpoint for document fetching
- Error handling and loading states
- Visual feedback and hover effects

The feature is now live and working. Users can click any document in the tier breakdown to view its full content.
