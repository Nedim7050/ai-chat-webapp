import React, { useState, useRef, useEffect } from 'react'
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

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)

    // Add user message
    const newUserMessage = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

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
        // Add timeout
        signal: AbortSignal.timeout(60000) // 60 seconds timeout
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
      
      // Add assistant reply
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
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
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    setError(null)
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
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
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

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Tapez votre message..."
            rows={1}
            className="message-input"
            disabled={loading}
          />
          <button 
            onClick={sendMessage} 
            disabled={loading || !input.trim()}
            className="send-button"
          >
            Envoyer
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

