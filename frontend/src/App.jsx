import { useState } from 'react'
import axios from 'axios'

function App() {
  const [response, setResponse] = useState('')
  const [question, setQuestion] = useState('')
  const [chatHistory, setChatHistory] = useState([])

  const sendQuery = async () => {
    if (!question.trim()) return
    try {
      const res = await axios.post('http://localhost:8000/query', { question })
      setResponse(res.data.response)
      setChatHistory(res.data.history || [])
      setQuestion('')
    } catch (err) {
      setResponse('Error: ' + err.message)
    }
  }

  const resetChat = async () => {
    const confirmed = window.confirm("Are you sure you want to reset the chat?")
    if (!confirmed) return

    setResponse('')
    setQuestion('')
    setChatHistory([])

    try {
      await axios.post('http://localhost:8000/reset')
      console.log("Chat reset successfully on backend")
    } catch (err) {
      console.error("Failed to reset chat on backend:", err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start px-6 py-8">
      
      {/* Logo / Title */}
      <h1 className="text-4xl font-bold mb-8 text-blue-400">AltoGPT Building Assistant</h1>

      <div className="w-full max-w-2xl space-y-8">

        {/* Chat History Box */}
        <div className="bg-gray-100 text-gray-800 p-6 rounded-md shadow-lg w-full">
          <h2 className="text-lg font-semibold text-center mb-4 text-gray-700">Conversation</h2>

          {chatHistory.length === 0 ? (
            <p className="text-gray-500 text-sm text-center">No conversation yet.</p>
          ) : (
            <ul className="space-y-4 text-sm">
              {chatHistory.map((item, index) => {
                const isLast = index === chatHistory.length - 1
                return (
                  <li key={index} className={`pb-2 ${isLast ? 'text-blue-600 font-semibold' : 'text-gray-800'}`}>
                    <p><strong>You:</strong> {item.question}</p>
                    <p><strong>Assistant:</strong> {item.answer}</p>
                  </li>
                )
              })}
            </ul>
          )}

          {response && (
            <div className="mt-6 pt-4 border-t border-gray-300">
              <h3 className="font-semibold mb-1 text-sm text-gray-600">Latest AI Response:</h3>
              <p className="text-green-700 text-sm">{response}</p>
            </div>
          )}
        </div>

        {/* Input & Buttons */}
        <div className="w-full flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-3 sm:space-y-0">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendQuery()}
            className="w-full sm:flex-grow bg-gray-800 text-white border border-gray-600 px-4 py-3 rounded-md text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ask a question (e.g., CO2 levels in Room101)..."
          />
          <div className="flex space-x-2 w-full sm:w-auto">
            <button
              onClick={resetChat}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded-md text-sm font-medium w-full sm:w-auto"
            >
              Clear 
            </button>
            <button
              onClick={sendQuery}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-md text-sm font-medium w-full sm:w-auto"
            >
              Submit
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
