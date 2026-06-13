import { useState } from 'react'
import BusinessCard from './OriginalCard'
import KnicksTicket from './KnicksTicket'

function App() {
  const [view, setView] = useState('card')

  if (view === 'ticket') {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4">
        <KnicksTicket />
        <button
          onClick={() => setView('card')}
          className="mt-8 text-neutral-500 hover:text-yellow-500 text-xs tracking-[0.3em] uppercase transition-colors"
        >
          ← Back to Card
        </button>
      </div>
    )
  }

  return (
    <div className="relative">
      <BusinessCard />
      <button
        onClick={() => setView('ticket')}
        className="fixed bottom-6 right-6 z-20 px-5 py-3 rounded-full text-xs tracking-[0.25em] uppercase font-semibold text-white shadow-lg transition-transform hover:scale-105"
        style={{ background: 'linear-gradient(135deg, #006BB6 0%, #F58426 100%)' }}
      >
        🎟 Knicks Ticket
      </button>
    </div>
  )
}

export default App
