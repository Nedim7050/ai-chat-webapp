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
  const sendingRef = useRef(false) // Prevent multiple simultaneous sends
  const messageIdsRef = useRef(new Set()) // Track message IDs to prevent duplicates

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
    // Check every 10 seconds
    const interval = setInterval(checkConnection, 10000)
    return () => clearInterval(interval)
  }, [])

  // Generate unique ID for messages
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const sendMessage = useCallback(async () => {
    // Prevent multiple simultaneous sends
    if (sendingRef.current || !input.trim() || loading) {
      return
    }

    const userMessage = input.trim()
    
    // Check if this exact message was just sent (prevent duplicates)
    const lastUserMessage = messages.filter(m => m.role === 'user').slice(-1)[0]
    if (lastUserMessage && lastUserMessage.content === userMessage) {
      return
    }
    
    // Set sending flag
    sendingRef.current = true
    setInput('')
    setError(null)
    setLoading(true)

    const userMessageId = generateMessageId()
    const userMsg = { id: userMessageId, role: 'user', content: userMessage, timestamp: Date.now() }

    // Add user message with deduplication
    setMessages(prev => {
      // Check for duplicates by content and role
      const isDuplicate = prev.some(
        msg => msg.role === 'user' && 
               msg.content === userMessage && 
               Date.now() - msg.timestamp < 5000 // Within 5 seconds
      )
      if (isDuplicate) {
        sendingRef.current = false
        setLoading(false)
        return prev
      }
      
      // Check if message ID already exists
      if (messageIdsRef.current.has(userMessageId)) {
        sendingRef.current = false
        setLoading(false)
        return prev
      }
      
      messageIdsRef.current.add(userMessageId)
      return [...prev, userMsg]
    })

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: messages.map(m => ({ role: m.role, content: m.content }))
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
      const assistantMsg = { 
        id: assistantMessageId, 
        role: 'assistant', 
        content: data.reply, 
        timestamp: Date.now() 
      }

      // Add assistant reply with strict deduplication
      setMessages(prev => {
        // Check for duplicates by content
        const isDuplicate = prev.some(
          msg => msg.role === 'assistant' && 
                 msg.content === data.reply && 
                 Date.now() - msg.timestamp < 5000 // Within 5 seconds
        )
        if (isDuplicate) {
          return prev
        }
        
        // Check if message ID already exists
        if (messageIdsRef.current.has(assistantMessageId)) {
          return prev
        }
        
        // Check if last message is identical
        const lastMsg = prev[prev.length - 1]
        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === data.reply) {
          return prev
        }
        
        messageIdsRef.current.add(assistantMessageId)
        return [...prev, assistantMsg]
      })
      setConnectionStatus('connected')
    } catch (err) {
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
  }, [input, loading, messages])

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
    messageIdsRef.current.clear()
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
              const lastUserMsg = messages.filter(m => m.role === 'user').slice(-1)[0]
              if (lastUserMsg && lastUserMsg.content === userMessage) {
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
