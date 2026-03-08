import { useState, useRef, Fragment } from 'react'
import './App.css'

const ALLOWED_FILES = ['W2.pdf', '1098-T.pdf']

const RESULTS_SECTIONS = [
  {
    title: 'Income',
    items: [
      { label: 'W2 Wages', value: '$52,000', line: 'Line 1a' },
      { label: 'Scholarship / Grant Income (1098-T)', value: '$6,000', line: 'Line 1h' },
      { label: 'Total Income', value: '$58,000', line: 'Line 9' },
      { label: 'Adjusted Gross Income (AGI)', value: '$54,500', line: 'Line 11a' },
    ],
  },
  {
    title: 'Deductions & Credits',
    items: [
      { label: 'Standard Deduction', value: '$14,000', line: 'Line 12' },
      { label: 'Itemized Deductions', value: '$0', line: 'Line 12 (Sch. A)' },
      { label: 'Non-Taxable Scholarships', value: '$13,500', line: 'Excluded from Line 1h' },
      { label: 'Education Credits (AOTC)', value: '$2,500', line: 'Sch. 3, Line 3 → Line 20' },
      { label: 'Total Deductions & Credits', value: '$16,500', line: 'Used to calc Line 15', fullWidth: true },
    ],
  },
  {
    title: 'Tax & Refund',
    items: [
      { label: 'Taxable Income', value: '$40,500', line: 'Line 15' },
      { label: 'Tax Bracket', value: '12%', line: 'Used to calc Line 16' },
      { label: 'Effective Tax Rate', value: '9.8%', line: 'Line 16 ÷ Line 15' },
      { label: 'Estimated Tax Liability', value: '$4,000', line: 'Line 16' },
      { label: 'Federal Tax Withheld', value: '$5,200', line: 'Line 25a' },
      { label: 'FICA / Social Security Withheld', value: '$3,224', line: 'W-2 Box 4; not on 1040' },
      { label: 'Medicare Withheld', value: '$754', line: 'W-2 Box 6; not on 1040' },
      { label: 'State Tax (Estimated)', value: '$2,900', line: 'Sch. A, Line 5a (if itemizing)' },
      { label: 'Self-Employment Tax', value: '$0', line: 'Sch. SE → Line 15' },
      { label: 'Child Tax Credit', value: '$0', line: 'Sch. 8812 → Line 19' },
      { label: 'Earned Income Credit (EIC)', value: 'Not Eligible', line: 'Line 27' },
      { label: 'Alternative Minimum Tax (AMT)', value: '$0', line: 'Line 17' },
      { label: 'Potential Refund', value: '$1,200', line: 'Line 35a', fullWidth: true, highlight: true },
    ],
  },
]

const INITIAL_CHAT = [
  { role: 'assistant', text: "Hi! I'm TaxMaxx Assistant. Ask me anything about your tax summary — what a line means, how a value was calculated, or what to do next." },
]

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
          {i < steps.length - 1 && (
            <div className={`step-line ${i < currentIndex ? 'done' : ''}`} />
          )}
        </Fragment>
      ))}
    </div>
  )
}

function App() {
  const [step, setStep] = useState('upload')
  const [files, setFiles] = useState({})
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState(INITIAL_CHAT)
  const [chatInput, setChatInput] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)
  const uploadRef = useRef(null)
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
      setError(`File(s) not accepted: ${rejected.join(', ')}. Files must be named exactly: W2.pdf or 1098-T.pdf`)
    }
  }

  const removeFile = (name) => {
    const updated = { ...files }
    delete updated[name]
    setFiles(updated)
    setError('')
  }

  const handleGenerate = () => {
    if (!files['W2.pdf'] || !files['1098-T.pdf']) {
      setError('Please upload both W2.pdf and 1098-T.pdf before generating.')
      return
    }
    setError('')
    setStep('processing')
    // TODO: Connect to backend API here.
    // When the API response is received, call setStep('results') and update result data.
    // Example:
    // fetch('/api/analyze', { method: 'POST', body: formData })
    //   .then(res => res.json())
    //   .then(data => { setResults(data); setStep('results') })
  }

  const handleStartOver = () => {
    setFiles({})
    setError('')
    setChatMessages(INITIAL_CHAT)
    setChatOpen(false)
    setStep('upload')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleGetStarted = () => {
    if (step !== 'upload') {
      setStep('upload')
      setTimeout(() => {
        uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 50)
    } else {
      uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
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
    <div className="app">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-logo">
          <div className="logo-icon">$</div>
          <div>
            <div className="logo-text">TAX<span>MAXX</span></div>
            <div className="logo-subtitle">Intelligence Agent</div>
          </div>
        </div>
        <div className="navbar-right">
          <a href="/1040pdf.pdf" target="_blank" rel="noopener noreferrer" className="nav-btn">
            📄 View 1040
          </a>
          <button className="nav-btn nav-btn-primary" onClick={handleGetStarted}>
            Get Started
          </button>
        </div>
      </nav>

      {/* Step Indicator */}
      <StepIndicator step={step} />

      {/* Page Content */}
      <div className="page-content">

        {/* Step 1: Upload */}
        {step === 'upload' && (
          <div ref={uploadRef}>
            <h1 className="page-title">Upload your documents</h1>
            <p className="page-subtitle">
              Drop your W-2 and 1098-T forms below. We'll extract the information you need to complete your 1040.
            </p>
            <div className="privacy-badge-wrap">
              <div className="privacy-badge">🔒 Your personal information is never stored</div>
            </div>

            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="upload-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                </svg>
              </div>
              <div className="upload-title">Drag &amp; drop your files here</div>
              <div className="upload-desc">or <span className="upload-link">browse</span> to choose files</div>
              <div className="accepted-formats">
                <span className="format-tag">W2.pdf</span>
                <span className="format-tag">1098-T.pdf</span>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleFiles(e.target.files)}
            />

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

            <a href="/1040pdf.pdf" target="_blank" rel="noopener noreferrer" className="view-1040-row">
              <span>📄</span> View blank 1040 form for reference
            </a>

            <div className="btn-row">
              <button className="btn btn-primary" onClick={handleGenerate}>Generate Summary →</button>
            </div>
          </div>
        )}

        {/* Step 2: Processing */}
        {step === 'processing' && (
          <div className="processing-card">
            <div className="spinner" />
            <div className="processing-title">Analyzing your documents…</div>
            <div className="processing-desc">
              This usually takes 10–20 seconds. We never store your personal information.
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" />
            </div>
            <div className="processing-steps">
              <div className="p-step p-step-done"><div className="p-step-dot">✓</div>Extracting data from W2.pdf</div>
              <div className="p-step p-step-done"><div className="p-step-dot">✓</div>Extracting data from 1098-T.pdf</div>
              <div className="p-step p-step-active"><div className="p-step-dot">⟳</div>Calculating tax summary</div>
              <div className="p-step"><div className="p-step-dot">○</div>Generating results</div>
            </div>
            {/* TODO: Remove this dev button before final demo */}
            <button className="btn btn-secondary dev-skip-btn" onClick={() => setStep('results')}>
              [Dev] Skip to Results →
            </button>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 'results' && (
          <div>
            <h1 className="page-title">Your 1040 Summary</h1>
            <p className="page-subtitle">
              Here's what we calculated from your documents. Use these values to fill out your Form 1040.
            </p>

            {RESULTS_SECTIONS.map((section) => (
              <div key={section.title}>
                <p className="section-label">{section.title}</p>
                <div className="results-grid">
                  {section.items.map((item, i) => (
                    <div
                      key={i}
                      className={`result-card ${item.fullWidth ? 'full-width' : ''} ${item.highlight ? 'highlight' : ''}`}
                    >
                      <div className="result-card-label">{item.label}</div>
                      <div className={`result-card-value ${item.highlight ? 'result-card-value--lg' : ''}`}>
                        {item.value}
                      </div>
                      <div className="result-card-line">{item.line}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Chat bot */}
            <div className="chatbot-section">
              <div className="chatbot-header" onClick={() => setChatOpen(!chatOpen)}>
                <div className="chatbot-header-left">
                  <div className="chatbot-dot" />
                  Need help? Ask TaxMaxx Chatbot
                </div>
                <span className="chatbot-arrow">{chatOpen ? '▲' : '▼'}</span>
              </div>
              {chatOpen && (
                <div className="chatbot-body">
                  <div className="chat-messages">
                    {chatMessages.map((msg, i) => (
                      <div key={i} className={`chat-msg chat-msg--${msg.role}`}>
                        {msg.text}
                      </div>
                    ))}
                    <div ref={chatEndRef} />
                  </div>
                  <div className="chat-input-row">
                    <input
                      type="text"
                      className="chat-input"
                      placeholder="Ask a question about your taxes…"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                    />
                    <button className="btn btn-primary chat-send-btn" onClick={handleChatSend}>Send</button>
                  </div>
                </div>
              )}
            </div>

            <div className="btn-row">
              <button className="btn btn-secondary" onClick={handleStartOver}>← Start Over</button>
              <button className="btn btn-primary" onClick={() => window.print()}>Download Summary</button>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default App
