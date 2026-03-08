import { useState, useRef } from 'react'
import './App.css'

const ALLOWED_FILES = ['W2.pdf', '1098-T.pdf']

const HARDCODED_RESULTS = [
  { label: 'Total Income', value: '$58,000' },
  { label: 'W2 Wages', value: '$52,000' },
  { label: 'Scholarship / Grant Income (1098-T)', value: '$6,000' },
  { label: 'Adjusted Gross Income (AGI)', value: '$54,500' },
  { label: 'Taxable Income', value: '$40,500' },
  { label: 'Standard Deduction', value: '$14,000' },
  { label: 'Itemized Deductions', value: '$0' },
  { label: 'Non-Taxable Scholarships', value: '$13,500' },
  { label: 'Education Credits (AOTC)', value: '$2,500' },
  { label: 'Total Deductions & Credits', value: '$16,500' },
  { label: 'Federal Tax Withheld', value: '$5,200' },
  { label: 'Estimated Tax Liability', value: '$4,000' },
  { label: 'Potential Refund', value: '$1,200' },
  { label: 'Tax Bracket', value: '12%' },
  { label: 'Effective Tax Rate', value: '9.8%' },
  { label: 'FICA / Social Security Withheld', value: '$3,224' },
  { label: 'Medicare Withheld', value: '$754' },
  { label: 'State Tax (Estimated)', value: '$2,900' },
  { label: 'Self-Employment Tax', value: '$0' },
  { label: 'Child Tax Credit', value: '$0' },
  { label: 'Earned Income Credit (EIC)', value: 'Not Eligible' },
  { label: 'Alternative Minimum Tax (AMT)', value: '$0' },
]

const INITIAL_CHAT = [
  { role: 'assistant', text: "Hi! I'm TaxMaxx Assistant. Ask me anything about your tax summary." },
]

function App() {
  const [files, setFiles] = useState({})
  const [generated, setGenerated] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState(INITIAL_CHAT)
  const [chatInput, setChatInput] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)
  const chatEndRef = useRef(null)

  const handleFiles = (newFiles) => {
    setError('')
    const updated = { ...files }
    const rejected = []
    Array.from(newFiles).forEach((file) => {
      if (!ALLOWED_FILES.includes(file.name)) {
        rejected.push(file.name)
      } else {
        updated[file.name] = file
      }
    })
    setFiles(updated)
    if (rejected.length > 0) {
      setError(
        `File(s) not accepted: ${rejected.join(', ')}. Files must be named exactly: W2.pdf or 1098-T.pdf`
      )
    }
  }

  const removeFile = (name) => {
    const updated = { ...files }
    delete updated[name]
    setFiles(updated)
    setGenerated(false)
    setError('')
  }

  const handleGenerate = () => {
    if (!files['W2.pdf'] || !files['1098-T.pdf']) {
      setError('Please upload both W2.pdf and 1098-T.pdf before generating.')
      return
    }
    setError('')
    setGenerated(true)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleChatSend = () => {
    if (!chatInput.trim()) return
    setChatMessages((prev) => [
      ...prev,
      { role: 'user', text: chatInput },
      { role: 'assistant', text: 'This is a placeholder response. The AI chatbot will be integrated soon!' },
    ])
    setChatInput('')
    setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
  }

  const uploadedNames = Object.keys(files)

  return (
    <div className="page">
      <div className="card">
        {/* Header */}
        <h1 className="title">TaxMaxx</h1>
        <p className="subtitle">
          Upload your tax documents, and we'll generate the info you need to fill out your 1040 form.
        </p>

        {/* Action Bar */}
        <div className="action-bar">
          <a
            href="/1040pdf.pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline"
          >
            <span className="btn-icon">📄</span> View 1040.pdf
          </a>
          <button className="btn btn-blue" onClick={() => fileInputRef.current.click()}>
            Upload
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            multiple
            style={{ display: 'none' }}
            onChange={(e) => handleFiles(e.target.files)}
          />
          <button className="btn btn-green" onClick={handleGenerate}>
            Generate →
          </button>
        </div>

        {/* Drop Zone */}
        <div
          className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <p className="drop-text">Drag &amp; drop your files here or <span className="browse-link">Browse files</span></p>
          <p className="file-hint">
            Files must be named exactly: <strong>W2.pdf</strong> and <strong>1098-T.pdf</strong>
          </p>
        </div>

        {/* Error Message */}
        {error && <p className="error-msg">{error}</p>}

        {/* Uploaded Files */}
        {uploadedNames.map((name) => (
          <div key={name} className="file-row">
            <span className="file-row-icon">📄</span>
            <span className="file-row-name">{name}</span>
            <button className="remove-btn" onClick={() => removeFile(name)}>✕</button>
          </div>
        ))}

        {/* Results Box */}
        {generated && (
          <div className="results-box">
            <h3 className="results-title">Summary of Personal Form 1040</h3>
            <div className="results-scroll">
              <div className="results-grid">
                {HARDCODED_RESULTS.map((item, i) => (
                  <div key={i} className="result-item">
                    <span className="result-label">• {item.label}:</span>
                    <span className="result-value">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chatbot */}
        {generated && (
          <div className="chatbot-section">
            <button className="chatbot-toggle" onClick={() => setChatOpen(!chatOpen)}>
              <span>💬</span>
              <span>Need more help? Ask TaxMaxx Chatbot</span>
              <span className="toggle-arrow">{chatOpen ? '▲' : '▼'}</span>
            </button>

            {chatOpen && (
              <div className="chat-window">
                <div className="chat-messages">
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`chat-msg chat-msg--${msg.role}`}>
                      <span>{msg.text}</span>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
                <div className="chat-input-row">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask a question about your taxes..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                  />
                  <button className="btn btn-blue" onClick={handleChatSend}>
                    Send
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
