// src/App.tsx
import { marked } from 'marked';
import { useEffect, useMemo, useRef, useState } from 'react';
import './App.css';


type BackendStatus = 'checking' | 'connected' | 'disconnected';
type ActiveTab = 'blog' | 'linkedin' | 'memory';

type MemoryType = 'blog' | 'linkedin';

type MemoryPostSummary = {
  id: number;
  created_at: string;
  type: MemoryType;
  topic: string;
  title: string;
};

type MemoryPostDetail = MemoryPostSummary & {
  content: string;
};

function App() {
  const [topic, setTopic] = useState<string>('digital detox');
  const [output, setOutput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [latestBlog, setLatestBlog] = useState<string>('');
  const [latestLinkedIn, setLatestLinkedIn] = useState<string>('');
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');
  const [activeTab, setActiveTab] = useState<ActiveTab>('blog');

  // Memory tab state
  const [memoryQuery, setMemoryQuery] = useState<string>('');
  const [memoryFilterType, setMemoryFilterType] = useState<'all' | MemoryType>('all');
  const [memoryPosts, setMemoryPosts] = useState<MemoryPostSummary[]>([]);
  const [memorySelected, setMemorySelected] = useState<MemoryPostDetail | null>(null);
  const [memoryLoading, setMemoryLoading] = useState<boolean>(false);
  const [memoryError, setMemoryError] = useState<string>('');

  const apiBase = useMemo(() => 'http://localhost:8000', []);

  const clearOutput = () => {
    setOutput('');
  };

  // Test backend connection
  const testConnection = async () => {
    try {
      const response = await fetch(`${apiBase}/health`);
      const data = await response.json();
      if (data.status === 'healthy') {
        setBackendStatus('connected');
        return true;
      }
    } catch (err) {
      console.error('Backend connection failed:', err);
      setBackendStatus('disconnected');
    }
    return false;
  };

  // Load the latest content on startup
  useEffect(() => {
    const initializeApp = async () => {
      // Test backend connection first
      const isConnected = await testConnection();

      if (isConnected) {
        try {
          // Load blog
          const blogResponse = await fetch(`${apiBase}/latest-blog`);
          const blogData = await blogResponse.json();

          if (blogData.error) {
            setLatestBlog(`Backend connected, but no blog found: ${blogData.error}`);
          } else {
            setLatestBlog(blogData.content || 'No blog content found.');
          }

          // Load LinkedIn post
          const linkedinResponse = await fetch(`${apiBase}/latest-linkedin`);
          const linkedinData = await linkedinResponse.json();

          if (linkedinData.error) {
            setLatestLinkedIn(`Backend connected, but no LinkedIn post found: ${linkedinData.error}`);
          } else {
            setLatestLinkedIn(linkedinData.content || 'No LinkedIn post found.');
          }
        } catch (err) {
          setLatestBlog('Backend connected, but failed to load content.');
          setLatestLinkedIn('Backend connected, but failed to load LinkedIn post.');
        }
      } else {
        setLatestBlog('Backend not connected. Please ensure the FastAPI server is running on port 8000.');
        setLatestLinkedIn('Backend not connected. Please ensure the FastAPI server is running on port 8000.');
      }
    };

    initializeApp();
  }, [apiBase]);

  // Memory helpers
  const loadMemoryList = async () => {
    if (backendStatus !== 'connected') return;
    setMemoryLoading(true);
    setMemoryError('');
    try {
      const qs = new URLSearchParams();
      if (memoryFilterType !== 'all') qs.append('filter_type', memoryFilterType);
      qs.append('limit', '50');
      const res = await fetch(`${apiBase}/memory/list?${qs.toString()}`);
      const data = await res.json();
      if (data.error) {
        setMemoryError(String(data.error));
        setMemoryPosts([]);
      } else {
        setMemoryPosts(Array.isArray(data.posts) ? data.posts : []);
      }
    } catch (e) {
      setMemoryError('Failed to load memory list');
      setMemoryPosts([]);
    } finally {
      setMemoryLoading(false);
    }
  };

  const searchMemory = async (q: string) => {
    if (backendStatus !== 'connected') return;
    if (!q.trim()) {
      return loadMemoryList();
    }
    setMemoryLoading(true);
    setMemoryError('');
    try {
      const qs = new URLSearchParams();
      qs.append('q', q);
      qs.append('limit', '50');
      const res = await fetch(`${apiBase}/memory/search?${qs.toString()}`);
      const data = await res.json();
      if (data.error) {
        setMemoryError(String(data.error));
        setMemoryPosts([]);
      } else {
        setMemoryPosts(Array.isArray(data.posts) ? data.posts : []);
      }
    } catch (e) {
      setMemoryError('Search failed');
      setMemoryPosts([]);
    } finally {
      setMemoryLoading(false);
    }
  };

  const loadMemoryPost = async (id: number) => {
    if (backendStatus !== 'connected') return;
    setMemoryLoading(true);
    setMemoryError('');
    try {
      const res = await fetch(`${apiBase}/memory/post/${id}`);
      const data = await res.json();
      if (data.error) {
        setMemoryError(String(data.error));
        setMemorySelected(null);
      } else {
        setMemorySelected(data as MemoryPostDetail);
      }
    } catch (e) {
      setMemoryError('Failed to load post');
      setMemorySelected(null);
    } finally {
      setMemoryLoading(false);
    }
  };

  // When switching to Memory tab, load initial list
  useEffect(() => {
    if (activeTab === 'memory' && backendStatus === 'connected') {
      if (memoryQuery.trim()) {
        searchMemory(memoryQuery);
      } else {
        loadMemoryList();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, backendStatus]);

  // Debounced search for memory
  const debounceRef = useRef<number | null>(null);
  useEffect(() => {
    if (activeTab !== 'memory' || backendStatus !== 'connected') return;
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      if (memoryQuery.trim()) {
        searchMemory(memoryQuery);
      } else {
        loadMemoryList();
      }
    }, 300);
    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [memoryQuery, memoryFilterType]);

  const openSelectedInTab = () => {
    if (!memorySelected) return;
    if (memorySelected.type === 'blog') {
      setLatestBlog(memorySelected.content);
      setActiveTab('blog');
    } else {
      setLatestLinkedIn(memorySelected.content);
      setActiveTab('linkedin');
    }
  };

  const runCrew = async () => {
    if (backendStatus !== 'connected') {
      setOutput('❌ Backend not connected. Please ensure the FastAPI server is running.\n');
      return;
    }

    setLoading(true);
    setOutput('🚀 Starting crew execution...\n');

    try {
      const response = await fetch(`${apiBase}/run-crew-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body reader available');
      }

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          // Process completed, refresh content
          try {
            const blogResponse = await fetch(`${apiBase}/latest-blog`);
            const blogData = await blogResponse.json();
            setLatestBlog(blogData.content || 'No blog content found.');

            const linkedinResponse = await fetch(`${apiBase}/latest-linkedin`);
            const linkedinData = await linkedinResponse.json();
            setLatestLinkedIn(linkedinData.content || 'No LinkedIn post found.');

            // Refresh memory list if on memory tab
            if (activeTab === 'memory') {
              if (memoryQuery.trim()) await searchMemory(memoryQuery); else await loadMemoryList();
            }
          } catch (err) {
            console.error('Failed to refresh content:', err);
          }

          setOutput(prev => prev + '\n✨ Crew execution completed!\n');
          setLoading(false);
          break;
        }

        const chunk = decoder.decode(value);
        if (chunk.trim()) {
          setOutput(prev => prev + chunk);
        }
      }
    } catch (err) {
      setOutput(prev => prev + `❌ Connection error: ${err}\nPlease ensure the backend is running on port 8000.\n`);
      setLoading(false);
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'connected': return '✅ Backend Connected';
      case 'disconnected': return '❌ Backend Disconnected';
      default: return '🔄 Checking Connection...';
    }
  };

  const MemoryTab = () => (
    <div style={{ display: 'flex', gap: 16 }}>
      {/* Left: controls + list */}
      <div style={{ width: '40%' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <select
            value={memoryFilterType}
            onChange={(e) => setMemoryFilterType(e.target.value as 'all' | MemoryType)}
            disabled={backendStatus !== 'connected'}
            style={{ padding: '6px 8px' }}
          >
            <option value="all">All</option>
            <option value="blog">Blog</option>
            <option value="linkedin">LinkedIn</option>
          </select>
          <input
            type="text"
            value={memoryQuery}
            onChange={(e) => setMemoryQuery(e.target.value)}
            placeholder="Search memory (FTS)"
            disabled={backendStatus !== 'connected'}
            style={{ flex: 1 }}
          />
        </div>

        {memoryError && (
          <div style={{ color: '#b00020', marginBottom: 8 }}>Error: {memoryError}</div>
        )}

        <div style={{
          border: '1px solid #dee2e6', borderRadius: 8, background: '#fff',
          maxHeight: 420, overflowY: 'auto', textAlign: 'left'
        }}>
          {memoryLoading && (
            <div style={{ padding: 12, fontStyle: 'italic', color: '#666' }}>Loading…</div>
          )}
          {!memoryLoading && memoryPosts.length === 0 && (
            <div style={{ padding: 12, color: '#666' }}>No posts</div>
          )}
          {!memoryLoading && memoryPosts.map((post) => (
            <div
              key={post.id}
              onClick={() => loadMemoryPost(post.id)}
              style={{
                padding: 12,
                borderBottom: '1px solid #eee',
                cursor: 'pointer',
                background: memorySelected?.id === post.id ? '#e3f2fd' : 'transparent'
              }}
            >
              <div style={{ fontWeight: 600 }}>{post.title || '(untitled)'}</div>
              <div style={{ fontSize: 12, color: '#666' }}>
                {post.type.toUpperCase()} • {post.topic || '—'} • {new Date(post.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right: preview */}
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>Preview</h2>
          <div>
            <button
              onClick={openSelectedInTab}
              disabled={!memorySelected}
              style={{ marginRight: 8 }}
            >
              Open in {memorySelected?.type === 'blog' ? 'Blog' : 'LinkedIn'} tab
            </button>
            <button onClick={() => {
              setMemorySelected(null);
              if (memoryQuery.trim()) searchMemory(memoryQuery); else loadMemoryList();
            }}>Refresh</button>
          </div>
        </div>
        <div className="markdown" style={{
          minHeight: 360,
          border: '1px solid #dee2e6', borderRadius: 8, background: '#fff',
          padding: 16
        }}
          dangerouslySetInnerHTML={{ __html: marked(memorySelected?.content || 'Select a post from the left list.') }}
        />
      </div>
    </div>
  );

  return (
    <div className="container">
      <h1>Mindful Tech Crew</h1>
      <p>Generate mindful tech content locally — no cloud, no tracking.</p>

      {/* Backend Status Indicator */}
      <div className={`status-bar ${
        backendStatus === 'connected' ? 'status-connected' :
        backendStatus === 'disconnected' ? 'status-disconnected' : 'status-checking'
      }`}>
        {getStatusText()}
        {backendStatus === 'disconnected' && (
          <button
            onClick={testConnection}
            style={{ marginLeft: '10px', padding: '4px 8px', fontSize: '12px' }}
          >
            Retry Connection
          </button>
        )}
      </div>

      <div className="input-group">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic (e.g., digital detox)"
          disabled={loading || backendStatus !== 'connected'}
        />
        <button 
          onClick={runCrew} 
          disabled={loading || backendStatus !== 'connected'}
        >
          {loading ? 'Running Crew...' : 'Run Crew'}
        </button>
      </div>

      {output && (
        <div className="output">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h2 style={{ margin: 0 }}>Live Output</h2>
            <button
              onClick={clearOutput}
              style={{
                padding: '4px 12px',
                fontSize: '12px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Clear
            </button>
          </div>
          <div className="live-output">
            {output}
          </div>
        </div>
      )}

      <div className="content-tabs">
        <div className="tab-buttons">
          <button
            onClick={() => setActiveTab('blog')}
            className={`tab-button ${activeTab === 'blog' ? 'active' : ''}`}
          >
            📝 Blog
          </button>
          <button
            onClick={() => setActiveTab('linkedin')}
            className={`tab-button ${activeTab === 'linkedin' ? 'active' : ''}`}
          >
            📱 LinkedIn Post
          </button>
          <button
            onClick={() => setActiveTab('memory')}
            className={`tab-button ${activeTab === 'memory' ? 'active' : ''}`}
          >
            🧠 Memory
          </button>
        </div>

        {activeTab === 'blog' && (
          <div className="blog-content">
            <h2>Latest Blog</h2>
            <div className="markdown" dangerouslySetInnerHTML={{ __html: marked(latestBlog) }} />
          </div>
        )}

        {activeTab === 'linkedin' && (
          <div className="linkedin-content">
            <h2>LinkedIn Post</h2>
            <div className="markdown" dangerouslySetInnerHTML={{ __html: marked(latestLinkedIn) }} />
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              fontSize: '14px',
              color: '#666'
            }}>
              💡 <strong>Tip:</strong> Copy the content above and paste it into LinkedIn!
            </div>
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="memory-content">
            <MemoryTab />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
