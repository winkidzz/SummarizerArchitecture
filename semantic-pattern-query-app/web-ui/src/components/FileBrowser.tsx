import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { fetchDirectoryContents, fetchDocumentContent } from "../lib/api";

interface FileItem {
  name: string;
  path: string;
  type: "file" | "directory";
  extension?: string;
}

interface FileBrowserProps {
  initialPath?: string;
  title: string;
}

const FileBrowser = ({ initialPath = "", title }: FileBrowserProps) => {
  const [currentPath, setCurrentPath] = useState<string>(initialPath);
  const [items, setItems] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<{
    name: string;
    path: string;
    content: string;
    extension: string;
    loading: boolean;
  } | null>(null);

  useEffect(() => {
    loadDirectory(currentPath);
  }, [currentPath]);

  const loadDirectory = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const contents = await fetchDirectoryContents(path);
      setItems(contents.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load directory");
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = async (item: FileItem) => {
    if (item.type === "directory") {
      // Navigate to directory
      setCurrentPath(item.path);
      setSelectedFile(null);
    } else {
      // Load file content
      const extension = item.extension || item.path.split('.').pop()?.toLowerCase() || "";

      setSelectedFile({
        name: item.name,
        path: item.path,
        content: "",
        extension,
        loading: true,
      });

      try {
        const result = await fetchDocumentContent(item.path);
        setSelectedFile({
          name: item.name,
          path: item.path,
          content: result.content,
          extension: result.metadata.extension?.replace('.', '').toLowerCase() || extension,
          loading: false,
        });
      } catch (err) {
        setSelectedFile({
          name: item.name,
          path: item.path,
          content: `Error loading file: ${err instanceof Error ? err.message : "Unknown error"}`,
          extension,
          loading: false,
        });
      }
    }
  };

  const handleBackClick = () => {
    setSelectedFile(null);
  };

  const navigateUp = () => {
    const pathParts = currentPath.split('/').filter(Boolean);
    pathParts.pop();
    setCurrentPath(pathParts.join('/'));
    setSelectedFile(null);
  };

  const getFileIcon = (item: FileItem): string => {
    if (item.type === "directory") return "📁";
    const ext = item.extension?.toLowerCase();
    if (ext === "md") return "📝";
    if (ext === "json") return "📋";
    if (ext === "py") return "🐍";
    if (ext === "ts" || ext === "tsx" || ext === "js" || ext === "jsx") return "⚛️";
    return "📄";
  };

  // If a file is selected, show its content
  if (selectedFile) {
    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">{title}</p>
            <h2>{selectedFile.name}</h2>
          </div>
          <button
            onClick={handleBackClick}
            style={{
              padding: "6px 12px",
              backgroundColor: "#6b7280",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            ← Back to list
          </button>
        </div>

        <div style={{ padding: "16px" }}>
          <p style={{ fontSize: "0.75rem", color: "#6b7280", marginBottom: "16px" }}>
            {selectedFile.path}
          </p>

          {selectedFile.loading ? (
            <div style={{ textAlign: "center", padding: "40px", color: "#6b7280" }}>
              Loading file content...
            </div>
          ) : selectedFile.extension === "md" ? (
            <div className="markdown-content">
              <ReactMarkdown>{selectedFile.content}</ReactMarkdown>
            </div>
          ) : (
            <pre
              style={{
                whiteSpace: "pre-wrap",
                wordWrap: "break-word",
                fontFamily: "ui-monospace, monospace",
                fontSize: "0.875rem",
                lineHeight: "1.6",
                margin: 0,
                backgroundColor: "#f6f8fa",
                padding: "16px",
                borderRadius: "6px",
              }}
            >
              {selectedFile.content}
            </pre>
          )}
        </div>
      </section>
    );
  }

  // Show directory listing
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">{title}</p>
          <h2>Browse files</h2>
        </div>
        {currentPath && (
          <button
            onClick={navigateUp}
            style={{
              padding: "6px 12px",
              backgroundColor: "#6b7280",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            ⬆ Up
          </button>
        )}
      </div>

      {loading ? (
        <div style={{ padding: "40px", textAlign: "center", color: "#6b7280" }}>
          Loading directory...
        </div>
      ) : error ? (
        <div style={{ padding: "16px" }}>
          <p style={{ color: "#dc2626" }}>Error: {error}</p>
        </div>
      ) : (
        <div style={{ padding: "16px" }}>
          {currentPath && (
            <p style={{ fontSize: "0.75rem", color: "#6b7280", marginBottom: "12px" }}>
              Current path: {currentPath || "/"}
            </p>
          )}

          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {items.length === 0 ? (
              <li style={{ padding: "20px", textAlign: "center", color: "#6b7280" }}>
                No files or folders found
              </li>
            ) : (
              items.map((item, index) => (
                <li
                  key={`${item.path}-${index}`}
                  onClick={() => handleItemClick(item)}
                  style={{
                    padding: "12px 16px",
                    marginBottom: "8px",
                    backgroundColor: "white",
                    borderRadius: "6px",
                    border: "1px solid #e5e7eb",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#f9fafb";
                    e.currentTarget.style.borderColor = "#3b82f6";
                    e.currentTarget.style.transform = "translateX(4px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "white";
                    e.currentTarget.style.borderColor = "#e5e7eb";
                    e.currentTarget.style.transform = "translateX(0)";
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "1.25rem" }}>{getFileIcon(item)}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: "500", fontSize: "0.9rem", color: "#1f2937" }}>
                        {item.name}
                      </div>
                      {item.type === "directory" && (
                        <div style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "2px" }}>
                          Click to open folder
                        </div>
                      )}
                    </div>
                    {item.type === "directory" && (
                      <span style={{ color: "#9ca3af", fontSize: "1rem" }}>→</span>
                    )}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </section>
  );
};

export default FileBrowser;
