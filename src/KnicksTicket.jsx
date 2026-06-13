import React, { useState, useEffect, useRef } from 'react';

// Knicks brand palette
const KNICKS_BLUE = '#006BB6';
const KNICKS_ORANGE = '#F58426';

function makeToken() {
  const chars = '0123456789ABCDEF';
  let t = '';
  for (let i = 0; i < 24; i++) t += chars[Math.floor(Math.random() * 16)];
  return t;
}

export default function KnicksTicket() {
  const [isFlipped, setIsFlipped] = useState(false);
  const [showWallet, setShowWallet] = useState(false);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  // SafeTix-style rotating token — refreshes every few seconds so the
  // barcode is never a static screenshot (mirrors the real app's behavior).
  const [token, setToken] = useState(() => makeToken());
  const [secondsLeft, setSecondsLeft] = useState(15);
  const cardRef = useRef(null);

  const event = {
    home: 'New York Knicks',
    away: 'Indiana Pacers',
    homeAbbr: 'NYK',
    awayAbbr: 'IND',
    series: 'Eastern Conference Finals · Game 6',
    venue: 'Madison Square Garden',
    venueCity: 'New York, NY',
    date: 'SAT · JUN 13, 2026',
    time: '8:30 PM ET',
    gates: '7:00 PM',
    section: '107',
    row: '8',
    seat: '14',
    entry: 'Chase Square — Gate 67',
    price: 'Mobile Entry',
    orderId: 'TM-4827-KNX-0613',
  };

  // Rotate the secure token on an interval (SafeTix refresh effect)
  useEffect(() => {
    const tick = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          setToken(makeToken());
          return 15;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(tick);
  }, []);

  // Subtle pointer-driven tilt for the "interactive" feel
  const handleMove = (e) => {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width - 0.5;
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: py * -8, y: px * 8 });
  };
  const resetTilt = () => setTilt({ x: 0, y: 0 });

  return (
    <div className="w-full max-w-md relative z-10">
      <style>{`
        @keyframes safetixSweep {
          0% { transform: translateX(-120%); }
          100% { transform: translateX(120%); }
        }
        @keyframes barPulse {
          0%, 100% { opacity: 0.55; }
          50% { opacity: 1; }
        }
        @keyframes orbDrift {
          0% { transform: translateX(0); }
          50% { transform: translateX(14px); }
          100% { transform: translateX(0); }
        }
      `}</style>

      {/* Apple Wallet sheet */}
      {showWallet && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-end sm:items-center justify-center z-50 p-4"
          onClick={() => setShowWallet(false)}
        >
          <div
            className="relative w-full max-w-sm rounded-3xl p-7 bg-neutral-900 border border-white/10 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center space-x-2 mb-6">
              <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16.5 3c-1.74 0-3.41 1.01-4.5 2.09C10.91 4.01 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3z"/>
              </svg>
              <h3 className="text-white text-lg font-semibold">Add to Apple Wallet</h3>
            </div>
            <p className="text-neutral-400 text-sm leading-relaxed mb-6">
              This event ticket will be saved to Apple Wallet for contactless entry.
              Present the live barcode at <span className="text-white">{event.entry}</span>.
            </p>
            <div className="rounded-2xl bg-black/60 border border-white/10 p-4 mb-6 text-sm">
              <Row label="Event" value={`${event.homeAbbr} vs ${event.awayAbbr}`} />
              <Row label="Date" value={event.date} />
              <Row label="Seat" value={`Sec ${event.section} · Row ${event.row} · Seat ${event.seat}`} />
            </div>
            <button
              onClick={() => setShowWallet(false)}
              className="w-full py-4 rounded-2xl bg-black text-white font-semibold tracking-wide flex items-center justify-center space-x-2 border border-white/15 hover:bg-neutral-800 transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.05 12.04c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.71-3.19-1.73-1.36-.14-2.65.8-3.34.8-.68 0-1.75-.78-2.88-.76-1.48.02-2.85.86-3.61 2.19-1.54 2.67-.39 6.62 1.11 8.78.73 1.06 1.6 2.25 2.74 2.21 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.08 2.65-2.14.84-1.23 1.18-2.42 1.2-2.48-.03-.01-2.29-.88-2.31-3.5zM14.9 5.6c.6-.73 1.01-1.74.9-2.75-.87.04-1.92.58-2.55 1.31-.56.64-1.05 1.67-.92 2.65.97.08 1.96-.49 2.57-1.21z"/>
              </svg>
              <span>Add Pass</span>
            </button>
          </div>
        </div>
      )}

      <div style={{ perspective: '1400px' }}>
        <div
          ref={cardRef}
          className="relative transition-transform duration-500 ease-out cursor-pointer"
          style={{
            transformStyle: 'preserve-3d',
            transform: `rotateX(${tilt.x}deg) rotateY(${isFlipped ? 180 : tilt.y}deg)`,
          }}
          onMouseMove={!isFlipped ? handleMove : undefined}
          onMouseLeave={resetTilt}
          onClick={() => setIsFlipped((f) => !f)}
        >
          {/* ---------- FRONT ---------- */}
          <div
            className="w-full rounded-[28px] overflow-hidden relative"
            style={{ backfaceVisibility: 'hidden', boxShadow: '0 25px 70px rgba(0,0,0,0.7)' }}
          >
            {/* Top hero band */}
            <div className="relative px-6 pt-6 pb-5" style={{ background: `linear-gradient(135deg, ${KNICKS_BLUE} 0%, #00528c 100%)` }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <TicketmasterMark />
                  <span className="text-white/90 text-[11px] tracking-[0.25em] uppercase font-semibold">Ticketmaster</span>
                </div>
                <span
                  className="text-[10px] tracking-[0.2em] uppercase font-bold px-2.5 py-1 rounded-full"
                  style={{ background: KNICKS_ORANGE, color: '#1a1a1a' }}
                >
                  SafeTix
                </span>
              </div>

              {/* Matchup */}
              <div className="mt-6 flex items-center justify-between">
                <TeamBadge abbr={event.homeAbbr} name="Knicks" />
                <div className="text-center px-2">
                  <p className="text-white/60 text-[10px] tracking-[0.3em] uppercase">vs</p>
                </div>
                <TeamBadge abbr={event.awayAbbr} name="Pacers" align="right" />
              </div>

              <p className="text-center text-white/70 text-[10px] tracking-[0.25em] uppercase mt-5">
                {event.series}
              </p>
            </div>

            {/* Event meta */}
            <div className="bg-neutral-950 px-6 pt-5 pb-4 relative">
              <h2 className="text-white text-lg font-light tracking-wide text-center">{event.venue}</h2>
              <p className="text-neutral-500 text-xs text-center tracking-wider mt-0.5">{event.venueCity}</p>

              <div className="flex justify-between mt-5 text-center">
                <Meta label="Date" value={event.date} />
                <Meta label="Time" value={event.time} />
                <Meta label="Gates" value={event.gates} />
              </div>

              <div className="flex justify-between mt-5 pt-4 border-t border-white/5 text-center">
                <Meta label="Sec" value={event.section} accent />
                <Meta label="Row" value={event.row} accent />
                <Meta label="Seat" value={event.seat} accent />
              </div>
            </div>

            {/* Perforation */}
            <div className="relative bg-neutral-950">
              <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-black" />
              <div className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-black" />
              <div className="mx-6 border-t border-dashed border-white/15" />
            </div>

            {/* SafeTix animated barcode */}
            <div className="bg-neutral-950 px-6 pt-5 pb-7">
              <AnimatedBarcode token={token} />
              <div className="flex items-center justify-center mt-3 space-x-2">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: KNICKS_ORANGE, animation: 'barPulse 1.5s ease-in-out infinite' }} />
                  <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: KNICKS_ORANGE }} />
                </span>
                <p className="text-neutral-500 text-[10px] tracking-[0.2em] uppercase">
                  Live · refreshes in {secondsLeft}s
                </p>
              </div>
              <p className="text-center text-neutral-700 text-[9px] tracking-[0.3em] uppercase mt-3">
                Tap card for details
              </p>
            </div>
          </div>

          {/* ---------- BACK ---------- */}
          <div
            className="w-full rounded-[28px] overflow-hidden absolute top-0 left-0 bg-neutral-950"
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)', boxShadow: '0 25px 70px rgba(0,0,0,0.7)' }}
          >
            <div className="px-6 pt-6 pb-4" style={{ background: `linear-gradient(135deg, ${KNICKS_BLUE} 0%, #00528c 100%)` }}>
              <p className="text-white/90 text-sm font-semibold tracking-wide">Ticket Details</p>
              <p className="text-white/60 text-xs mt-0.5">{event.home} vs {event.away}</p>
            </div>

            <div className="px-6 py-5 space-y-3">
              <DetailRow label="Entry" value={event.entry} />
              <DetailRow label="Delivery" value={event.price} />
              <DetailRow label="Section / Row / Seat" value={`${event.section} / ${event.row} / ${event.seat}`} />
              <DetailRow label="Date" value={`${event.date} · ${event.time}`} />
              <DetailRow label="Order" value={event.orderId} />
              <DetailRow label="Token" value={token.replace(/(.{4})/g, '$1 ').trim()} mono />
            </div>

            <div className="px-6 pb-5">
              <p className="text-neutral-600 text-[10px] leading-relaxed tracking-wide">
                This is a screenshot-proof mobile ticket. The barcode is a rotating
                SafeTix token and must be presented live from this device for entry.
                No screenshots or printouts accepted.
              </p>
            </div>

            <div className="px-6 pb-6">
              <div className="border-t border-white/5 pt-4 flex items-center justify-between">
                <span className="text-neutral-600 text-[10px] tracking-[0.3em] uppercase">Tap to flip back</span>
                <TicketmasterMark size={18} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add to Apple Wallet */}
      <button
        onClick={() => setShowWallet(true)}
        className="w-full mt-8 py-4 rounded-2xl bg-black text-white font-semibold tracking-wide flex items-center justify-center space-x-2.5 border border-white/15 hover:bg-neutral-900 transition-colors"
      >
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17.05 12.04c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.71-3.19-1.73-1.36-.14-2.65.8-3.34.8-.68 0-1.75-.78-2.88-.76-1.48.02-2.85.86-3.61 2.19-1.54 2.67-.39 6.62 1.11 8.78.73 1.06 1.6 2.25 2.74 2.21 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.08 2.65-2.14.84-1.23 1.18-2.42 1.2-2.48-.03-.01-2.29-.88-2.31-3.5zM14.9 5.6c.6-.73 1.01-1.74.9-2.75-.87.04-1.92.58-2.55 1.31-.56.64-1.05 1.67-.92 2.65.97.08 1.96-.49 2.57-1.21z"/>
        </svg>
        <span>Add to Apple Wallet</span>
      </button>
    </div>
  );
}

/* ---------- Sub-components ---------- */

function TeamBadge({ abbr, name, align = 'left' }) {
  return (
    <div className={`flex-1 ${align === 'right' ? 'text-right' : 'text-left'}`}>
      <p className="text-white text-2xl font-bold tracking-tight">{abbr}</p>
      <p className="text-white/70 text-[11px] tracking-[0.2em] uppercase mt-0.5">{name}</p>
    </div>
  );
}

function Meta({ label, value, accent }) {
  return (
    <div className="flex-1">
      <p className="text-neutral-600 text-[9px] tracking-[0.25em] uppercase">{label}</p>
      <p className={`mt-1 text-sm font-semibold ${accent ? '' : 'text-white'}`} style={accent ? { color: KNICKS_ORANGE } : undefined}>
        {value}
      </p>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between py-1">
      <span className="text-neutral-500">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}

function DetailRow({ label, value, mono }) {
  return (
    <div className="flex justify-between items-baseline gap-4">
      <span className="text-neutral-600 text-xs tracking-wide flex-shrink-0">{label}</span>
      <span className={`text-white text-sm text-right ${mono ? 'font-mono text-xs tracking-tight' : 'font-medium'}`}>{value}</span>
    </div>
  );
}

function TicketmasterMark({ size = 22 }) {
  return (
    <div
      className="rounded-md flex items-center justify-center font-black text-white"
      style={{ width: size, height: size, background: KNICKS_ORANGE, fontSize: size * 0.6 }}
    >
      t
    </div>
  );
}

// SafeTix-style barcode: dense bars with a moving sweep + drifting orbs,
// so it reads as a live, animated credential rather than a static image.
function AnimatedBarcode({ token }) {
  // Derive deterministic bar widths from the live token so it visibly
  // changes whenever the token rotates.
  const bars = [];
  for (let i = 0; i < 60; i++) {
    const seed = token.charCodeAt(i % token.length) + i * 7;
    bars.push((seed % 3) + 1); // width 1–3
  }

  return (
    <div className="rounded-xl bg-white p-3 relative overflow-hidden">
      <div className="flex items-end justify-center h-20 gap-[2px]">
        {bars.map((w, i) => (
          <div
            key={i}
            className="bg-black h-full"
            style={{ width: `${w}px` }}
          />
        ))}
      </div>
      {/* moving sweep highlight */}
      <div
        className="absolute inset-y-0 w-16 pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent, rgba(245,132,38,0.35), transparent)',
          animation: 'safetixSweep 2.4s ease-in-out infinite',
        }}
      />
      {/* drifting brand orbs (signature SafeTix motion) */}
      <div className="absolute bottom-1.5 left-1/2 -translate-x-1/2 flex gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: KNICKS_BLUE, animation: 'orbDrift 2s ease-in-out infinite' }} />
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: KNICKS_ORANGE, animation: 'orbDrift 2s ease-in-out infinite reverse' }} />
      </div>
    </div>
  );
}
