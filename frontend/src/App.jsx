import React, { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'

// Use proxy in development, direct URL in production
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '/api' : 'http://localhost:8000')

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('checking')
  const messagesEndRef = useRef(null)
  const sendingRef = useRef(false)
  const pendingMessagesRef = useRef(new Set()) // Track pending message IDs
  const lastMessageRef = useRef({ role: null, content: null, timestamp: 0 }) // Track last message

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_URL}/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        if (response.ok) {
          const data = await response.json()
          setConnectionStatus(data.model_loaded ? 'connected' : 'loading')
        } else {
          setConnectionStatus('disconnected')
        }
      } catch (err) {
        setConnectionStatus('disconnected')
        console.warn('Backend not available:', err.message)
      }
    }
    
    checkConnection()
    const interval = setInterval(checkConnection, 10000)
    return () => clearInterval(interval)
  }, [])

  // Generate unique ID for messages
  const generateMessageId = useCallback(() => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

  // Strict deduplication check
  const isDuplicateMessage = useCallback((role, content) => {
    const now = Date.now()
    // Check if same as last message within 2 seconds
    if (lastMessageRef.current.role === role && 
        lastMessageRef.current.content === content &&
        now - lastMessageRef.current.timestamp < 2000) {
      return true
    }
    return false
  }, [])

  const sendMessage = useCallback(async () => {
    // Multiple guards against duplicate sends
    if (sendingRef.current || loading || !input.trim()) {
      return
    }

    const userMessage = input.trim()
    const now = Date.now()
    
    // Check if this is a duplicate of the last user message
    if (isDuplicateMessage('user', userMessage)) {
      console.log('Duplicate user message blocked')
      return
    }
    
    // Check against last message in state
    setMessages(currentMessages => {
      const lastMsg = currentMessages[currentMessages.length - 1]
      if (lastMsg && lastMsg.role === 'user' && lastMsg.content === userMessage) {
        console.log('Duplicate user message in state blocked')
        return currentMessages
      }
      return currentMessages
    })

    // Set sending flag IMMEDIATELY
    sendingRef.current = true
    const userMessageId = generateMessageId()
    
    // Check if this ID is already pending
    if (pendingMessagesRef.current.has(userMessageId)) {
      sendingRef.current = false
      return
    }
    pendingMessagesRef.current.add(userMessageId)

    setInput('')
    setError(null)
    setLoading(true)

    // Update last message ref
    lastMessageRef.current = { role: 'user', content: userMessage, timestamp: now }

    // Add user message with strict deduplication
    setMessages(prev => {
      // Final check: ensure no duplicate
      const lastMsg = prev[prev.length - 1]
      if (lastMsg && lastMsg.role === 'user' && lastMsg.content === userMessage) {
        pendingMessagesRef.current.delete(userMessageId)
        sendingRef.current = false
        setLoading(false)
        return prev
      }
      
      return [...prev, { 
        id: userMessageId, 
        role: 'user', 
        content: userMessage, 
        timestamp: now 
      }]
    })

    try {
      // Get current messages for history (use functional update to get latest)
      const currentMessages = messages
      const history = currentMessages.map(m => ({ role: m.role, content: m.content }))

      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: history
        }),
        signal: AbortSignal.timeout(60000)
      })

      if (!response.ok) {
        const errorText = await response.text()
        let errorMessage = `Erreur ${response.status}`
        
        if (response.status === 403) {
          errorMessage = 'Accès refusé. Vérifiez que le backend est démarré et que CORS est configuré correctement.'
        } else if (response.status === 404) {
          errorMessage = 'Endpoint non trouvé. Vérifiez l\'URL de l\'API.'
        } else if (response.status === 500) {
          errorMessage = 'Erreur serveur. Le modèle n\'est peut-être pas chargé.'
        } else if (response.status === 503) {
          errorMessage = 'Service indisponible. Le modèle est en cours de chargement...'
        }
        
        throw new Error(`${errorMessage} (${response.status})`)
      }

      const data = await response.json()
      
      if (!data.reply) {
        throw new Error('Réponse invalide du serveur')
      }
      
      const assistantMessageId = generateMessageId()
      const replyTimestamp = Date.now()

      // Check if this reply is a duplicate
      if (isDuplicateMessage('assistant', data.reply)) {
        console.log('Duplicate assistant message blocked')
        pendingMessagesRef.current.delete(userMessageId)
        sendingRef.current = false
        setLoading(false)
        return
      }

      // Update last message ref
      lastMessageRef.current = { role: 'assistant', content: data.reply, timestamp: replyTimestamp }

      // Add assistant reply with STRICT deduplication
      setMessages(prev => {
        // Check if last message is identical
        const lastMsg = prev[prev.length - 1]
        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === data.reply) {
          console.log('Duplicate assistant message in state blocked')
          pendingMessagesRef.current.delete(userMessageId)
          return prev
        }
        
        // Check if any recent message is identical (within last 3 messages)
        const recentMessages = prev.slice(-3)
        const hasDuplicate = recentMessages.some(
          msg => msg.role === 'assistant' && msg.content === data.reply
        )
        if (hasDuplicate) {
          console.log('Duplicate assistant message in recent messages blocked')
          pendingMessagesRef.current.delete(userMessageId)
          return prev
        }
        
        pendingMessagesRef.current.delete(userMessageId)
        return [...prev, { 
          id: assistantMessageId, 
          role: 'assistant', 
          content: data.reply, 
          timestamp: replyTimestamp 
        }]
      })
      setConnectionStatus('connected')
    } catch (err) {
      pendingMessagesRef.current.delete(userMessageId)
      if (err.name === 'AbortError') {
        setError('Timeout: La requête a pris trop de temps. Le modèle est peut-être en train de se charger.')
      } else if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Impossible de se connecter au backend. Vérifiez que le serveur est démarré sur ' + API_URL)
        setConnectionStatus('disconnected')
      } else {
        setError(err.message)
      }
      console.error('Error sending message:', err)
    } finally {
      setLoading(false)
      sendingRef.current = false
    }
  }, [input, loading, messages, generateMessageId, isDuplicateMessage])

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!loading && input.trim() && !sendingRef.current) {
        sendMessage()
      }
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!loading && input.trim() && !sendingRef.current) {
        sendMessage()
      }
    }
  }

  const clearChat = () => {
    setMessages([])
    setError(null)
    pendingMessagesRef.current.clear()
    lastMessageRef.current = { role: null, content: null, timestamp: 0 }
  }

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-left">
            <h1>Assistant Pharma/MedTech</h1>
            <p className="domain-subtitle">Spécialisé en Pharmaceutique & Santé</p>
            <div className="connection-status">
              <span className={`status-dot ${connectionStatus}`}></span>
              {connectionStatus === 'connected' && 'En ligne'}
              {connectionStatus === 'loading' && 'Chargement...'}
              {connectionStatus === 'disconnected' && 'Hors ligne'}
              {connectionStatus === 'checking' && 'Vérification...'}
            </div>
          </div>
          <button onClick={clearChat} className="clear-btn">Effacer</button>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <p>👋 Bonjour! Je suis un assistant spécialisé dans le domaine <strong>pharmaceutique et de la santé (Pharma/MedTech)</strong>.</p>
              <p>Je peux vous aider avec des questions sur :</p>
              <ul>
                <li>💊 Médicaments et principes actifs</li>
                <li>🏥 Dispositifs médicaux (MedTech)</li>
                <li>🔬 Essais cliniques et recherche pharmaceutique</li>
                <li>📋 Réglementation (FDA, EMA, ANSM)</li>
                <li>⚠️ Pharmacovigilance et sécurité</li>
                <li>🧬 Biotechnologie pharmaceutique</li>
              </ul>
              <p><strong>Note :</strong> Je ne peux répondre qu'aux questions liées au domaine pharmaceutique et de la santé.</p>
            </div>
          )}
          
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message assistant">
              <div className="message-content">
                <span className="typing-indicator">...</span>
              </div>
            </div>
          )}
          
          {error && (
            <div className="error-message">
              Erreur: {error}
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form 
          className="input-container"
          onSubmit={(e) => {
            e.preventDefault()
            if (!loading && input.trim() && !sendingRef.current) {
              const userMessage = input.trim()
              // Final check before sending
              if (isDuplicateMessage('user', userMessage)) {
                return
              }
              sendMessage()
            }
          }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            onKeyDown={handleKeyDown}
            placeholder="Tapez votre message..."
            rows={1}
            className="message-input"
            disabled={loading || sendingRef.current}
          />
          <button 
            type="submit"
            disabled={loading || !input.trim() || sendingRef.current}
            className="send-button"
          >
            {loading ? 'Envoi...' : 'Envoyer'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
