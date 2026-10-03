import { useEffect, useState } from "react"

function App() {
  const [text, setText] = useState("")
  const [message, setMessage] = useState("")
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [memories, setMemories] = useState([])

  async function remember() {
    if (!text.trim()) return

    setLoading(true)
    setMessage("Saving to memory...")

    try {
      const response = await fetch("http://127.0.0.1:8000/remember", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error("Failed to save memory")
      }

      setMessage("Memory saved successfully")
      setText("")
      await loadMemories()

      setTimeout(() => {
        setMessage("")
      }, 3000)
    } catch (error) {
      console.error(error)
      setMessage("Could not save memory. Is the backend running?")
    }

    setLoading(false)
  }

  async function ask() {
    if (!question.trim()) return

    setAsking(true)
    setAnswer("")

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: question }),
      })

      if (!response.ok) {
        throw new Error("Failed to ask MemoMate")
      }

      const data = await response.json()
      setAnswer(data.answer)
    } catch (error) {
      console.error(error)
      setAnswer("Something went wrong. Is the backend running?")
    }

    setAsking(false)
  }

  async function loadMemories() {
    try {
      const response = await fetch("http://127.0.0.1:8000/memories")
      const data = await response.json()
      setMemories(data.memories)
    } catch (error) {
      console.error("Could not load memories:", error)
    }
  }

  useEffect(() => {
    loadMemories()
  }, [])

  const tasks = memories.filter((memory) => memory.type === "task")
  const ideas = memories.filter((memory) => memory.type === "idea")
  const people = memories.filter((memory) => memory.type === "person")
  const notes = memories.filter((memory) => memory.type === "note")

  function renderMemoryGroup(title, icon, items, emptyText) {
    return (
      <div className="memory-panel">
        <div className="memory-panel-header">
          <div className="memory-title">
            <span className="memory-icon">{icon}</span>
            <div>
              <h3>{title}</h3>
              <span>{items.length} {items.length === 1 ? "memory" : "memories"}</span>
            </div>
          </div>
        </div>

        <div className="memory-list">
          {items.length === 0 ? (
            <div className="empty-memory">
              <span>—</span>
              <p>{emptyText}</p>
            </div>
          ) : (
            items.slice(0, 6).map((memory) => (
              <div className="memory-row" key={memory.id}>
                <span className="memory-dot"></span>
                <p>{memory.content}</p>
              </div>
            ))
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="app">

      {/* Background decoration */}
      <div className="ambient ambient-one"></div>
      <div className="ambient ambient-two"></div>

      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">M</div>
          <div>
            <strong>MemoMate</strong>
            <span>Personal AI memory</span>
          </div>
        </div>

        <div className="status-pill">
          <span className="status-dot"></span>
          Local AI active
        </div>
      </header>
      <main className="container">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span>✦</span>
              YOUR SECOND BRAIN
            </div>

            <h1>
              Your thoughts,
              <br />
              <span>remembered.</span>
            </h1>

            <p>
              Tell MemoMate what matters. It remembers tasks, ideas,
              people and context so you can find them when you need them.
            </p>
          </div>

          <div className="hero-stats">
            <div className="stat">
              <strong>{memories.length}</strong>
              <span>Total memories</span>
            </div>

            <div className="stat">
              <strong>{tasks.length}</strong>
              <span>Tasks</span>
            </div>

            <div className="stat">
              <strong>{people.length}</strong>
              <span>People</span>
            </div>
          </div>
        </section>
        <section className="workspace">
          <div className="workspace-card remember-card">

            <div className="card-heading">
              <div className="heading-icon remember-icon">✦</div>

              <div>
                <span className="section-label">MEMORY CAPTURE</span>
                <h2>Tell MemoMate something</h2>
              </div>
            </div>

            <p className="card-description">
              Share anything you want to remember. MemoMate will organize
              the important parts automatically.
            </p>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="I need to finish this today..."
            />

            <div className="input-footer">
              <span className="hint">
                Your memories stay on this device.
              </span>

              <div className="remember-action">
                {message && (
                  <span className={`save-message ${message.includes("Could") ? "error" : ""}`}>
                    {message.includes("successfully") && "✓ "}
                    {message}
                  </span>
                )}

                <button
                  className="primary-button"
                  onClick={remember}
                  disabled={loading || !text.trim()}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Saving
                    </>
                  ) : (
                    <>
                      Remember
                      <span>→</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
          <div className="workspace-card ask-card">

            <div className="card-heading">
              <div className="heading-icon ask-icon">⌕</div>

              <div>
                <span className="section-label">MEMORY SEARCH</span>
                <h2>Ask MemoMate</h2>
              </div>
            </div>

            <p className="card-description">
              Ask questions naturally. MemoMate searches your stored
              memories and brings back the relevant context.
            </p>

            <div className="ask-input">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") ask()
                }}
                placeholder="What am I supposed to do today?"
              />

              <button
                onClick={ask}
                disabled={asking || !question.trim()}
              >
                {asking ? (
                  <span className="spinner"></span>
                ) : (
                  "Ask →"
                )}
              </button>
            </div>

            {answer && (
              <div className="answer-box">
                <div className="answer-top">
                  <div className="mini-avatar">M</div>
                  <span>MemoMate</span>
                  <div className="answer-line"></div>
                  <span className="ai-label">AI MEMORY</span>
                </div>

                <p>{answer}</p>
              </div>
            )}
          </div>
        </section>

        <section className="memories-section">

          <div className="section-header">
            <div>
              <span className="section-label">YOUR MEMORY</span>
              <h2>Everything MemoMate remembers</h2>
            </div>

            <span className="memory-count">
              {memories.length} total
            </span>
          </div>

          {memories.length === 0 ? (
            <div className="empty-dashboard">
              <div className="empty-symbol">✦</div>
              <h3>Your memory is empty</h3>
              <p>Tell MemoMate something above to get started.</p>
            </div>
          ) : (
            <div className="memory-grid">
              {renderMemoryGroup(
                "Tasks",
                "✓",
                tasks,
                "No tasks captured yet."
              )}

              {renderMemoryGroup(
                "Ideas",
                "✦",
                ideas,
                "No ideas captured yet."
              )}

              {renderMemoryGroup(
                "People",
                "○",
                people,
                "No people captured yet."
              )}

              {renderMemoryGroup(
                "Notes",
                "≡",
                notes,
                "No notes captured yet."
              )}
            </div>
          )}
        </section>

        <section className="feature-strip">

          <div className="feature">
            <div className="feature-number">01</div>
            <div>
              <h3>Understands</h3>
              <p>AI turns natural conversations into useful memories.</p>
            </div>
          </div>

          <div className="feature">
            <div className="feature-number">02</div>
            <div>
              <h3>Remembers</h3>
              <p>Tasks, ideas, people and personal context stay organized.</p>
            </div>
          </div>

          <div className="feature">
            <div className="feature-number">03</div>
            <div>
              <h3>Retrieves</h3>
              <p>Ask naturally and find the information you told it before.</p>
            </div>
          </div>

        </section>

      </main>

      <footer>
        <div className="footer-brand">
          <div className="brand-mark small">M</div>
          <strong>MemoMate</strong>
        </div>

        <span>
          Built with local open-source AI
        </span>
      </footer>

    </div>
  )
}

export default App