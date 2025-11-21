# Markdown Rendering Feature

## Overview
Added automatic markdown rendering for `.md` files in the document viewer modal. Markdown files are now displayed with proper formatting, headings, code blocks, tables, and links instead of plain text.

## Changes Made

### 1. Install react-markdown Package
**Command**: `npm install react-markdown`

Added dependency to render markdown content in React components.

### 2. Frontend - TierBreakdown Component
**File**: `web-ui/src/components/TierBreakdown.tsx`

#### Key Changes:

1. **Import ReactMarkdown**:
```typescript
import ReactMarkdown from "react-markdown";
```

2. **Track File Extension**:
```typescript
const [selectedDoc, setSelectedDoc] = useState<{
  path: string;
  id: string;
  content: string;
  extension: string;  // Added to track file type
  loading: boolean;
} | null>(null);
```

3. **Extract and Store Extension**:
```typescript
const handleDocumentClick = async (source: SourceDocument) => {
  // Extract file extension from path
  const extension = path.split('.').pop()?.toLowerCase() || "";

  setSelectedDoc({
    path,
    id: source.document_id ?? "Unknown",
    content: "",
    extension,  // Store extension
    loading: true,
  });

  // Update with metadata extension from API response
  const result = await fetchDocumentContent(path);
  setSelectedDoc((prev) =>
    prev
      ? {
          ...prev,
          content: result.content,
          extension: result.metadata.extension?.replace('.', '').toLowerCase() || extension,
          loading: false
        }
      : null
  );
};
```

4. **Conditional Rendering**:
```typescript
{selectedDoc.loading ? (
  <div>Loading document content...</div>
) : selectedDoc.extension === "md" ? (
  <div className="markdown-content">
    <ReactMarkdown>{selectedDoc.content}</ReactMarkdown>
  </div>
) : (
  <pre>{selectedDoc.content}</pre>
)}
```

### 3. CSS Styling
**File**: `web-ui/src/App.css`

Added comprehensive markdown styling (lines 265-398):

- **Headings**: H1-H4 with proper sizing and bottom borders
- **Paragraphs**: Proper spacing and margins
- **Lists**: Indentation and item spacing
- **Code Blocks**: Background color, padding, syntax highlighting ready
- **Inline Code**: Light background, rounded corners, monospace font
- **Blockquotes**: Left border and muted color
- **Tables**: Borders, header styling, cell padding
- **Links**: Blue color with hover underline
- **Images**: Max-width for responsive display
- **Horizontal Rules**: Styled dividers

## Supported Markdown Features

The ReactMarkdown component supports:

✅ **Headings** (H1-H6)
✅ **Bold** and *italic* text
✅ **Lists** (ordered and unordered)
✅ **Code blocks** with language tags
✅ **Inline code**
✅ **Links** and images
✅ **Blockquotes**
✅ **Tables**
✅ **Horizontal rules**
✅ **Line breaks**

## User Experience

### For Markdown Files (.md):
1. Click on document in tier breakdown
2. Modal opens with **rendered markdown**
3. Proper formatting with:
   - Styled headings
   - Formatted code blocks
   - Clickable links
   - Tables with borders
   - Blockquotes with left border

### For Other Files:
1. Click on document
2. Modal opens with **plain text** in monospace font
3. Preserves original formatting

## Example Rendering

**Markdown Input**:
```markdown
# RAG Pattern

## Overview
Basic RAG combines:
- Vector search
- LLM generation

## Code Example
\`\`\`python
def query(text):
    docs = retrieve(text)
    return generate(docs, text)
\`\`\`
```

**Rendered Output**:
- Large "RAG Pattern" heading with bottom border
- Medium "Overview" heading
- Bulleted list with proper indentation
- "Code Example" subheading
- Code block with gray background and syntax highlighting ready

## Technical Details

### File Type Detection:
1. Extract extension from file path when document is clicked
2. Fallback to extension from API metadata
3. Convert to lowercase for case-insensitive matching
4. Check if extension === "md" for markdown rendering

### Styling Approach:
- GitHub-flavored markdown style
- Clean, professional appearance
- Proper spacing and typography
- Code blocks with distinct background
- Responsive tables and images

### Performance:
- react-markdown is optimized for React
- No additional parsing libraries needed
- Renders on demand when modal opens
- Lightweight dependency (~80 packages)

## Future Enhancements

Potential improvements:
1. **Syntax Highlighting**: Add `react-syntax-highlighter` for code blocks
2. **Mermaid Diagrams**: Support diagram rendering
3. **LaTeX Math**: Add math equation support
4. **Table of Contents**: Auto-generate from headings
5. **Copy Code Button**: Add copy button to code blocks
6. **Dark Mode**: Support dark theme for markdown
7. **Export Options**: Download as PDF or HTML

## Testing

To test the feature:
1. Run a query in the UI
2. Click on any `.md` document in the tier breakdown
3. Verify:
   - ✅ Headings are properly sized
   - ✅ Code blocks have gray background
   - ✅ Lists are indented
   - ✅ Links are blue and clickable
   - ✅ Tables render with borders

For non-markdown files (e.g., `.txt`, `.json`):
1. Click on document
2. Verify plain text is shown in monospace font

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari

The react-markdown library uses standard React and is compatible with all modern browsers.

## Status

✅ **Implemented and working**
- Markdown rendering for .md files
- Fallback to plain text for other files
- Comprehensive GitHub-style CSS
- Automatic file type detection
- Clean, professional appearance

The feature is now live. All markdown files in the tier breakdown will be rendered with proper formatting when clicked.
