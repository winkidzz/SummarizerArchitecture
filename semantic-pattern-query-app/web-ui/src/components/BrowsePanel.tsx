import { useState } from "react";
import FileBrowser from "./FileBrowser";

const BrowsePanel = () => {
  const [activeBrowser, setActiveBrowser] = useState<string | null>(null);

  const browsers = [
    {
      id: "patterns",
      title: "📁 RAG Patterns",
      path: "/Users/sanantha/SummarizerArchitecture/pattern-library/patterns",
      icon: "📁",
    },
    {
      id: "use-cases",
      title: "💼 Use Cases",
      path: "/Users/sanantha/SummarizerArchitecture/pattern-library/use-cases",
      icon: "💼",
    },
    {
      id: "vendor-guides",
      title: "🏢 Vendor Guides",
      path: "/Users/sanantha/SummarizerArchitecture/pattern-library/vendor-guides",
      icon: "🏢",
    },
  ];

  if (activeBrowser) {
    const browser = browsers.find((b) => b.id === activeBrowser);
    if (browser) {
      return (
        <div>
          <button
            onClick={() => setActiveBrowser(null)}
            style={{
              padding: "8px 16px",
              backgroundColor: "#6b7280",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.875rem",
              marginBottom: "16px",
            }}
          >
            ← Back to browse menu
          </button>
          <FileBrowser initialPath={browser.path} title={browser.title} />
        </div>
      );
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Browse Library</p>
          <h2>📖 Pattern Library</h2>
        </div>
      </div>

      <div style={{ padding: "16px" }}>
        <p style={{ fontSize: "0.85rem", color: "#6b7280", marginBottom: "16px" }}>
          Browse patterns, use cases, and vendor guides directly
        </p>

        {browsers.map((browser) => (
          <button
            key={browser.id}
            onClick={() => setActiveBrowser(browser.id)}
            style={{
              display: "block",
              width: "100%",
              padding: "12px 16px",
              backgroundColor: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "6px",
              textAlign: "left",
              fontSize: "0.875rem",
              marginBottom: "8px",
              cursor: "pointer",
              transition: "background-color 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#2563eb";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#3b82f6";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.25rem" }}>{browser.icon}</span>
              <span>{browser.title}</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
};

export default BrowsePanel;
