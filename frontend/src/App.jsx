import { useState, useRef, Fragment, useEffect } from 'react'
import './App.css'

const ALLOWED_FILES = ['W2.pdf', '1098-T.pdf']
const API_BASE = 'http://localhost:8000/api/parser'
const CALC_BASE = 'http://localhost:8000/api/calculations'

const INITIAL_CHAT = [
  { role: 'assistant', text: "Hi! I'm TaxMaxx Assistant. Ask me anything about your tax summary." },
]

const fmtMoney = (n) =>
  '$' + Number(n ?? 0).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
const fmtPct = (n) => `${(Number(n ?? 0) * 100).toFixed(1)}%`

function buildSectionsFromDraft(draft, calculations) {
  if (!draft) return []
  const tax = calculations?.tax_and_refund || {}
  const deductions = calculations?.deductions_credits || {}
  const effectiveRate = draft.line_15 ? (draft.line_16 / draft.line_15) : 0

  return [
    {
      title: 'Income',
      items: [
        { label: 'W2 Wages', value: fmtMoney(draft.line_1a), line: 'Line 1a' },
        { label: 'Total Income', value: fmtMoney(draft.line_9), line: 'Line 9' },
        { label: 'Adjusted Gross Income (AGI)', value: fmtMoney(draft.line_11a), line: 'Line 11a' },
      ],
    },
    {
      title: 'Deductions & Credits',
      items: [
        { label: 'Standard Deduction', value: fmtMoney(deductions.standard_deduction || 14600), line: 'Line 12' },
        { label: 'Education Credits (AOTC)', value: fmtMoney(deductions.education_credits || 0), line: 'Future expansion' },
        { label: 'Taxable Income', value: fmtMoney(draft.line_15), line: 'Line 15', fullWidth: true },
      ],
    },
    {
      title: 'Tax & Refund',
      items: [
        { label: 'Estimated Tax Liability', value: fmtMoney(draft.line_16), line: 'Line 16' },
        { label: 'Federal Tax Withheld', value: fmtMoney(draft.line_25a), line: 'Line 25a' },
        { label: 'Total Payments', value: fmtMoney(draft.line_25d), line: 'Line 25d' },
        { label: 'Potential Refund', value: fmtMoney(draft.line_34), line: 'Line 34', highlight: true },
        { label: 'Tax Bracket', value: fmtPct(tax.tax_bracket_rate || 0), line: 'Derived estimate' },
        { label: 'Effective Tax Rate', value: fmtPct(effectiveRate), line: 'Line 16 ÷ Line 15' },
      ],
    },
  ]
}

function StepIndicator({ step }) {
  const steps = ['upload', 'processing', 'results']
  const labels = ['Upload', 'Processing', 'Results']
  const currentIndex = steps.indexOf(step)
  return (
    <div className="step-indicator">
      {steps.map((s, i) => (
        <Fragment key={s}>
          <div className={`step ${i < currentIndex ? 'done' : ''} ${i === currentIndex ? 'active' : ''} ${i > currentIndex ? 'inactive' : ''}`}>
            <div className="step-circle">{i < currentIndex ? '✓' : i + 1}</div>
            <div className="step-label">{labels[i]}</div>
          </div>
          {i < steps.length - 1 && <div className={`step-line ${i < currentIndex ? 'done' : ''}`} />}
        </Fragment>
      ))}
    </div>
  )
}

function App() {
  const [step, setStep] = useState('upload')
  const [files, setFiles] = useState({})
  const [error, setError] = useState('')
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState(INITIAL_CHAT)
  const [chatInput, setChatInput] = useState('')
  const [resultsSections, setResultsSections] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('theme') === 'dark')
  const [chatLoading, setChatLoading] = useState(false)

  const fileInputRef = useRef(null)
  const uploadRef = useRef(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  const handleFiles = (newFiles) => {
    setError('')
    const updated = { ...files }
    const rejected = []
    Array.from(newFiles).forEach((file) => {
      if (!ALLOWED_FILES.includes(file.name)) rejected.push(file.name)
      else updated[file.name] = file
    })
    setFiles(updated)
    if (rejected.length) setError(`File(s) not accepted: ${rejected.join(', ')}. Files must be named exactly: W2.pdf or 1098-T.pdf`)
  }

  const removeFile = (name) => {
    const updated = { ...files }
    delete updated[name]
    setFiles(updated)
    setError('')
  }

  const uploadedNames = Object.keys(files)

  const handleGenerate = async () => {
    if (!files['W2.pdf'] || !files['1098-T.pdf']) {
      setError('Please upload both W2.pdf and 1098-T.pdf before generating.')
      return
    }
    setError('')
    setStep('processing')

    const formData = new FormData()
    formData.append('files', files['W2.pdf'])
    formData.append('files', files['1098-T.pdf'])
    formData.append('mock_mode', 'false')

    try {
      const response = await fetch(`${API_BASE}/box-data`, { method: 'POST', body: formData })
      const payload = await response.json()
      if (!response.ok) {
        const detail = payload?.detail ? (typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)) : 'Failed to analyze documents.'
        throw new Error(detail)
      }

      const nextSessionId = payload.session_id
      setSessionId(nextSessionId || null)

      let draft = payload?.draft_1040
      if (nextSessionId) {
        const draftResp = await fetch(`${CALC_BASE}/draft/${nextSessionId}`)
        if (draftResp.ok) {
          const draftPayload = await draftResp.json()
          draft = draftPayload?.draft_1040 || draft
        }
      }
      if (!draft) throw new Error('No draft 1040 values were returned by backend.')

      setResultsSections(buildSectionsFromDraft(draft, payload.calculations))
      setStep('results')
    } catch (e) {
      setStep('upload')
      setError(`Could not process documents: ${e.message}`)
    }
  }

  const handleChatSend = async () => {
    const message = chatInput.trim()
    if (!message) return

    setChatMessages((prev) => [...prev, { role: 'user', text: message }])
    setChatInput('')

    if (!sessionId) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: 'Generate your report first so I can explain your actual stored 1040 draft values.',
        },
      ])
      return
    }

    setChatLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/chatbot/ask/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
      const payload = await response.json()
      if (!response.ok) {
        const detail = payload?.detail
          ? (typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail))
          : 'Could not get chatbot response.'
        throw new Error(detail)
      }
      setChatMessages((prev) => [...prev, { role: 'assistant', text: payload.answer }])
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `I hit an error while answering: ${err.message}`,
        },
      ])
    } finally {
      setChatLoading(false)
      setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-logo">
          <div className="logo-icon">$</div>
          <div>
            <div className="logo-text">TAX<span>MAXX</span></div>
            <div className="logo-subtitle">Intelligence Agent</div>
          </div>
        </div>
        <div className="navbar-right">
          <button className="nav-btn" onClick={() => setDarkMode((v) => !v)}>{darkMode ? '☀️' : '🌙'}</button>
          <a href="/1040pdf.pdf" target="_blank" rel="noopener noreferrer" className="nav-btn">📄 View 1040</a>
          <button className="nav-btn nav-btn-primary" onClick={() => uploadRef.current?.scrollIntoView({ behavior: 'smooth' })}>Get Started</button>
        </div>
      </nav>

      <StepIndicator step={step} />
      <div className="page-content" ref={uploadRef}>
        {step === 'upload' && (
          <>
            <h1 className="page-title">Upload your documents</h1>
            <p className="page-subtitle">Drop your W-2 and 1098-T forms below. We will extract and calculate your draft 1040 values.</p>
            <div className={`upload-zone ${dragOver ? 'drag-over' : ''}`} onDragOver={(e) => { e.preventDefault(); setDragOver(true) }} onDragLeave={() => setDragOver(false)} onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files) }} onClick={() => fileInputRef.current.click()}>
              <div className="upload-title">Drag & drop your files here</div>
              <div className="upload-desc">or <span className="upload-link">browse</span> to choose files</div>
              <div className="accepted-formats"><span className="format-tag">W2.pdf</span><span className="format-tag">1098-T.pdf</span></div>
            </div>
            <input ref={fileInputRef} type="file" accept=".pdf" multiple style={{ display: 'none' }} onChange={(e) => handleFiles(e.target.files)} />
            {error && <p className="error-msg">{error}</p>}
            {uploadedNames.length > 0 && (
              <div className="file-list">
                {uploadedNames.map((name) => (
                  <div key={name} className="file-item">
                    <div className="file-item-left">
                      <div className="file-icon-badge">PDF</div>
                      <div>
                        <div className="file-name">{name}</div>
                        <div className="file-size">{(files[name].size / 1024).toFixed(0)} KB</div>
                      </div>
                    </div>
                    <div className="file-item-right">
                      <div className="file-status">
                        <div className="check-icon">✓</div>
                        Ready
                      </div>
                      <button className="remove-btn" onClick={(e) => { e.stopPropagation(); removeFile(name) }}>×</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="btn-row"><button className="btn btn-primary" onClick={handleGenerate}>Generate Summary →</button></div>
          </>
        )}

        {step === 'processing' && (
          <div className="processing-card">
            <div className="spinner" />
            <div className="processing-title">Analyzing your documents...</div>
            <div className="processing-desc">Please wait while TaxMaxx parses your W-2 and 1098-T.</div>
          </div>
        )}

        {step === 'results' && (
          <>
            <h1 className="page-title">Your 1040 Summary</h1>
            {sessionId && <p className="page-subtitle">Session ID: {sessionId}</p>}
            {resultsSections.map((section) => (
              <div key={section.title}>
                <p className="section-label">{section.title}</p>
                <div className="results-grid">
                  {section.items.map((item, i) => (
                    <div key={`${section.title}-${i}`} className={`result-card ${item.fullWidth ? 'full-width' : ''} ${item.highlight ? 'highlight' : ''}`}>
                      <div className="result-card-label">{item.label}</div>
                      <div className={`result-card-value ${item.highlight ? 'result-card-value--lg' : ''}`}>{item.value}</div>
                      <div className="result-card-line">{item.line}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <div className="chatbot-section">
              <div className="chatbot-header" onClick={() => setChatOpen(!chatOpen)}>
                <div className="chatbot-header-left"><div className="chatbot-dot" />Need help? Ask TaxMaxx Chatbot</div>
                <span className="chatbot-arrow">{chatOpen ? '▲' : '▼'}</span>
              </div>
              {chatOpen && (
                <div className="chatbot-body">
                  <div className="chat-messages">
                    {chatMessages.map((m, i) => <div key={i} className={`chat-msg chat-msg--${m.role}`}>{m.text}</div>)}
                    {chatLoading && <div className="chat-msg chat-msg--assistant">Thinking...</div>}
                    <div ref={chatEndRef} />
                  </div>
                  <div className="chat-input-row">
                    <input
                      className="chat-input"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                      placeholder="Ask a question about your taxes..."
                      disabled={chatLoading}
                    />
                    <button className="btn btn-blue" onClick={handleChatSend} disabled={chatLoading}>
                      Send
                    </button>
                  </div>
                </div>
              )}
            </div>
            <div className="btn-row">
              <button className="btn btn-secondary" onClick={() => { setStep('upload'); setResultsSections([]); setFiles({}); setError('') }}>← Start Over</button>
              <button className="btn btn-primary" onClick={() => window.print()}>Download Summary</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
