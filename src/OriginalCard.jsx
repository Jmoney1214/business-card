import React, { useState } from 'react';

export default function BusinessCard() {
  const [isFlipped, setIsFlipped] = useState(false);
  const [showShareSuccess, setShowShareSuccess] = useState(false);
  const [showNFCInfo, setShowNFCInfo] = useState(false);
  
  const contact = {
    name: "Justin Etwaru",
    firstName: "Justin",
    lastName: "Etwaru",
    title: "CEO",
    company: "Legacy Wine & Spirits",
    tagline: "The Art of Fine Spirits",
    phone: "+19144201823",
    phoneDisplay: "(914) 420-1823",
    email: "justin@legacywineandliquor.com",
    website: "https://legacywineandliquor.com",
    websiteDisplay: "legacywineandliquor.com",
    address: "",
    city: "Sanford",
    state: "FL",
    zip: "",
    country: "USA",
  };

  const generateVCard = () => {
    return `BEGIN:VCARD
VERSION:3.0
N:${contact.lastName};${contact.firstName};;;
FN:${contact.name}
ORG:${contact.company}
TITLE:${contact.title}
TEL;TYPE=WORK,VOICE:${contact.phone}
EMAIL;TYPE=WORK:${contact.email}
URL:${contact.website}
ADR;TYPE=WORK:;;${contact.address};${contact.city};${contact.state};${contact.zip};${contact.country}
NOTE:${contact.tagline}
END:VCARD`;
  };

  const downloadVCard = () => {
    const vcard = generateVCard();
    const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${contact.name.replace(' ', '_')}.vcf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setShowShareSuccess(true);
    setTimeout(() => setShowShareSuccess(false), 3000);
  };

  const shareContact = async () => {
    const vcard = generateVCard();
    const blob = new Blob([vcard], { type: 'text/vcard' });
    const file = new File([blob], `${contact.name.replace(' ', '_')}.vcf`, { type: 'text/vcard' });

    if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({
          files: [file],
          title: `${contact.name} - Contact Card`,
          text: `Contact info for ${contact.name} at ${contact.company}`,
        });
        setShowShareSuccess(true);
        setTimeout(() => setShowShareSuccess(false), 3000);
      } catch (err) {
        if (err.name !== 'AbortError') {
          try {
            await navigator.share({
              title: `${contact.name} - ${contact.company}`,
              text: `${contact.name}\n${contact.title}\n${contact.company}\n📞 ${contact.phoneDisplay}\n✉️ ${contact.email}\n🌐 ${contact.websiteDisplay}`,
              url: contact.website,
            });
          } catch (e) {
            downloadVCard();
          }
        }
      }
    } else if (navigator.share) {
      try {
        await navigator.share({
          title: `${contact.name} - ${contact.company}`,
          text: `${contact.name}\n${contact.title}\n${contact.company}\n📞 ${contact.phoneDisplay}\n✉️ ${contact.email}\n🌐 ${contact.websiteDisplay}`,
          url: contact.website,
        });
      } catch (e) {
        if (e.name !== 'AbortError') {
          downloadVCard();
        }
      }
    } else {
      downloadVCard();
    }
  };

  // Luxury QR Code with gold styling
  const QRCode = () => (
    <svg viewBox="0 0 100 100" className="w-full h-full">
      <defs>
        <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#d4a855"/>
          <stop offset="50%" stopColor="#f5d998"/>
          <stop offset="100%" stopColor="#c9a227"/>
        </linearGradient>
      </defs>
      <rect fill="#080808" width="100" height="100"/>
      <g fill="url(#goldGradient)">
        <rect x="5" y="5" width="25" height="25"/>
        <rect x="8" y="8" width="19" height="19" fill="#080808"/>
        <rect x="11" y="11" width="13" height="13" fill="url(#goldGradient)"/>
        
        <rect x="70" y="5" width="25" height="25"/>
        <rect x="73" y="8" width="19" height="19" fill="#080808"/>
        <rect x="76" y="11" width="13" height="13" fill="url(#goldGradient)"/>
        
        <rect x="5" y="70" width="25" height="25"/>
        <rect x="8" y="73" width="19" height="19" fill="#080808"/>
        <rect x="11" y="76" width="13" height="13" fill="url(#goldGradient)"/>
        
        {[35,40,45,50,55,60].map(x => <rect key={`t${x}`} x={x} y="5" width="4" height="4"/>)}
        {[35,45,55].map(x => <rect key={`t2${x}`} x={x} y="10" width="4" height="4"/>)}
        {[5,10,15,20,25].map(y => <rect key={`l${y}`} x="35" y={35+y} width="4" height="4"/>)}
        {[0,10,20].map(i => <rect key={`c${i}`} x={40+i} y="40" width="4" height="4"/>)}
        {[0,5,15,20,25].map(i => <rect key={`r${i}`} x="70" y={35+i} width="4" height="4"/>)}
        {[40,50,60].map(x => <rect key={`b${x}`} x={x} y="70" width="4" height="4"/>)}
        {[75,80,85].map(y => <rect key={`br${y}`} x="70" y={y} width="4" height="4"/>)}
        <rect x="45" y="45" width="10" height="10"/>
      </g>
    </svg>
  );

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4 relative overflow-hidden">
      {/* Luxury background effects */}
      <div className="fixed inset-0">
        {/* Subtle radial glow */}
        <div className="absolute inset-0 bg-gradient-radial from-yellow-900/5 via-transparent to-transparent" 
          style={{background: 'radial-gradient(ellipse at center, rgba(212,175,55,0.03) 0%, transparent 70%)'}}/>
        {/* Diagonal luxury pattern */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `repeating-linear-gradient(45deg, #d4af37 0px, #d4af37 1px, transparent 1px, transparent 60px)`
        }}/>
        {/* Vignette effect */}
        <div className="absolute inset-0" style={{
          background: 'radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.4) 100%)'
        }}/>
      </div>

      {/* Animated gold particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div 
            key={i}
            className="absolute w-1 h-1 rounded-full bg-yellow-500/20"
            style={{
              left: `${15 + i * 15}%`,
              top: `${20 + (i % 3) * 25}%`,
              animation: `float ${4 + i}s ease-in-out infinite`,
              animationDelay: `${i * 0.5}s`
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) scale(1); opacity: 0.2; }
          50% { transform: translateY(-20px) scale(1.5); opacity: 0.5; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes borderGlow {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.6; }
        }
      `}</style>

      {/* Success Toast */}
      {showShareSuccess && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
          <div className="relative px-8 py-4 rounded-full shadow-2xl flex items-center space-x-3 border border-yellow-500/30"
            style={{
              background: 'linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%)',
              boxShadow: '0 0 40px rgba(212,175,55,0.2)'
            }}>
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-700 flex items-center justify-center">
              <svg className="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span className="text-yellow-500 font-light tracking-[0.2em] uppercase text-sm">Contact Ready</span>
          </div>
        </div>
      )}

      {/* NFC Info Modal */}
      {showNFCInfo && (
        <div className="fixed inset-0 bg-black/95 backdrop-blur-xl flex items-center justify-center z-50 p-4" onClick={() => setShowNFCInfo(false)}>
          <div 
            className="relative max-w-sm w-full rounded-3xl p-8 border border-yellow-600/20"
            style={{
              background: 'linear-gradient(180deg, #111 0%, #080808 100%)',
              boxShadow: '0 0 60px rgba(212,175,55,0.1), inset 0 1px 0 rgba(212,175,55,0.1)'
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Corner accents */}
            <div className="absolute top-0 left-0 w-16 h-16">
              <div className="absolute top-4 left-4 w-8 h-px bg-gradient-to-r from-yellow-600 to-transparent"/>
              <div className="absolute top-4 left-4 w-px h-8 bg-gradient-to-b from-yellow-600 to-transparent"/>
            </div>
            <div className="absolute bottom-0 right-0 w-16 h-16">
              <div className="absolute bottom-4 right-4 w-8 h-px bg-gradient-to-l from-yellow-600 to-transparent"/>
              <div className="absolute bottom-4 right-4 w-px h-8 bg-gradient-to-t from-yellow-600 to-transparent"/>
            </div>

            <div className="flex justify-between items-center mb-8">
              <h3 className="text-lg font-extralight text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-yellow-500 to-yellow-200 tracking-[0.3em] uppercase">NFC Setup</h3>
              <button onClick={() => setShowNFCInfo(false)} className="text-neutral-600 hover:text-yellow-500 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              {[
                { num: "01", title: "Acquire NFC Tag", desc: "NTAG215 or NTAG216 recommended" },
                { num: "02", title: "Download vCard", desc: "Export your digital contact file" },
                { num: "03", title: "Program Tag", desc: "Use NFC Tools app to encode" },
                { num: "04", title: "Tap to Share", desc: "Instant contact transfer" },
              ].map((step, i) => (
                <div key={i} className="flex items-start space-x-5 group">
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full border border-yellow-600/30 flex items-center justify-center group-hover:border-yellow-600/60 transition-colors">
                      <span className="text-transparent bg-clip-text bg-gradient-to-b from-yellow-400 to-yellow-700 font-light text-sm">{step.num}</span>
                    </div>
                  </div>
                  <div className="pt-1">
                    <p className="text-white font-light tracking-wider">{step.title}</p>
                    <p className="text-neutral-600 text-sm mt-0.5">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <button 
              onClick={downloadVCard}
              className="w-full mt-10 px-6 py-4 rounded-2xl font-medium tracking-[0.2em] uppercase text-sm transition-all relative overflow-hidden group"
              style={{
                background: 'linear-gradient(135deg, #b8860b 0%, #d4af37 25%, #f5d998 50%, #d4af37 75%, #b8860b 100%)',
                backgroundSize: '200% auto',
              }}
            >
              <span className="relative z-10 text-black">Export vCard</span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"/>
            </button>
          </div>
        </div>
      )}

      <div className="w-full max-w-md relative z-10">
        {/* Card */}
        <div 
          className="relative cursor-pointer group"
          style={{ perspective: '1200px' }}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          <div 
            className="relative transition-all duration-1000 ease-out"
            style={{ 
              transformStyle: 'preserve-3d',
              transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
            }}
          >
            {/* Front of Card */}
            <div 
              className="w-full rounded-3xl overflow-hidden relative"
              style={{ 
                backfaceVisibility: 'hidden',
                boxShadow: '0 25px 80px rgba(0,0,0,0.8), 0 0 40px rgba(212,175,55,0.1)'
              }}
            >
              {/* Card background with texture */}
              <div className="absolute inset-0 bg-gradient-to-br from-neutral-900 via-black to-neutral-900"/>
              <div className="absolute inset-0 opacity-30" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              }}/>
              
              {/* Animated border glow */}
              <div className="absolute inset-0 rounded-3xl border border-yellow-600/20 group-hover:border-yellow-600/40 transition-colors duration-500"
                style={{ animation: 'borderGlow 3s ease-in-out infinite' }}/>
              
              {/* Inner gold line border */}
              <div className="absolute inset-2 rounded-2xl border border-yellow-600/10"/>

              <div className="relative p-12 min-h-72">
                {/* Corner accents - more elaborate */}
                <div className="absolute top-6 left-6">
                  <div className="w-12 h-px bg-gradient-to-r from-yellow-500 to-transparent"/>
                  <div className="w-px h-12 bg-gradient-to-b from-yellow-500 to-transparent"/>
                  <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-yellow-500"/>
                </div>
                <div className="absolute top-6 right-6">
                  <div className="w-12 h-px bg-gradient-to-l from-yellow-500 to-transparent ml-auto"/>
                  <div className="w-px h-12 bg-gradient-to-b from-yellow-500 to-transparent ml-auto"/>
                  <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-yellow-500"/>
                </div>
                <div className="absolute bottom-6 left-6">
                  <div className="w-px h-12 bg-gradient-to-t from-yellow-500 to-transparent"/>
                  <div className="w-12 h-px bg-gradient-to-r from-yellow-500 to-transparent"/>
                  <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-yellow-500"/>
                </div>
                <div className="absolute bottom-6 right-6">
                  <div className="w-px h-12 bg-gradient-to-t from-yellow-500 to-transparent ml-auto"/>
                  <div className="w-12 h-px bg-gradient-to-l from-yellow-500 to-transparent"/>
                  <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-yellow-500"/>
                </div>
                
                {/* Luxury Monogram */}
                <div className="flex justify-center mb-10">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full flex items-center justify-center relative"
                      style={{
                        background: 'linear-gradient(135deg, rgba(212,175,55,0.1) 0%, transparent 50%, rgba(212,175,55,0.05) 100%)',
                        boxShadow: 'inset 0 0 20px rgba(212,175,55,0.1)'
                      }}>
                      <div className="absolute inset-0 rounded-full border border-yellow-600/40"/>
                      <div className="absolute inset-1.5 rounded-full border border-yellow-600/20"/>
                      <div className="absolute inset-3 rounded-full border border-yellow-600/10"/>
                      <span 
                        className="text-2xl tracking-[0.3em] font-extralight"
                        style={{
                          background: 'linear-gradient(180deg, #f5d998 0%, #d4af37 50%, #b8860b 100%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                          textShadow: '0 0 30px rgba(212,175,55,0.3)'
                        }}
                      >LS</span>
                    </div>
                  </div>
                </div>
                
                {/* Company Name */}
                <div className="text-center mb-10">
                  <h2 
                    className="text-xl font-extralight tracking-[0.4em] uppercase"
                    style={{
                      background: 'linear-gradient(90deg, #b8860b 0%, #d4af37 20%, #f5d998 50%, #d4af37 80%, #b8860b 100%)',
                      backgroundSize: '200% auto',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      animation: 'shimmer 4s linear infinite',
                    }}
                  >
                    {contact.company}
                  </h2>
                  <div className="flex items-center justify-center mt-4 space-x-4">
                    <div className="w-16 h-px bg-gradient-to-r from-transparent via-yellow-600/50 to-transparent"/>
                    <div className="w-1.5 h-1.5 rounded-full bg-yellow-600/50"/>
                    <div className="w-16 h-px bg-gradient-to-r from-transparent via-yellow-600/50 to-transparent"/>
                  </div>
                  <p className="text-neutral-500 text-xs tracking-[0.35em] uppercase mt-4 font-light italic">
                    {contact.tagline}
                  </p>
                </div>
                
                {/* Name & Title */}
                <div className="text-center">
                  <h1 
                    className="text-3xl font-extralight tracking-[0.25em] uppercase text-white"
                    style={{ textShadow: '0 0 40px rgba(255,255,255,0.1)' }}
                  >
                    {contact.name}
                  </h1>
                  <p 
                    className="mt-4 tracking-[0.3em] uppercase text-xs font-light"
                    style={{
                      background: 'linear-gradient(90deg, #8b7355, #d4af37, #8b7355)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    {contact.title}
                  </p>
                </div>
                
                {/* Flip indicator */}
                <div className="absolute bottom-5 left-1/2 -translate-x-1/2">
                  <div className="flex items-center space-x-3 text-neutral-700">
                    <div className="w-6 h-px bg-gradient-to-r from-transparent to-neutral-700"/>
                    <svg className="w-3 h-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <div className="w-6 h-px bg-gradient-to-l from-transparent to-neutral-700"/>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Back of Card */}
            <div 
              className="w-full rounded-3xl overflow-hidden absolute top-0 left-0"
              style={{ 
                backfaceVisibility: 'hidden',
                transform: 'rotateY(180deg)',
                boxShadow: '0 25px 80px rgba(0,0,0,0.8), 0 0 40px rgba(212,175,55,0.1)'
              }}
            >
              {/* Card background */}
              <div className="absolute inset-0 bg-gradient-to-br from-neutral-900 via-black to-neutral-900"/>
              <div className="absolute inset-0 opacity-30" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              }}/>
              
              <div className="absolute inset-0 rounded-3xl border border-yellow-600/20"/>
              <div className="absolute inset-2 rounded-2xl border border-yellow-600/10"/>

              <div className="relative p-8">
                {/* Mini corner accents */}
                <div className="absolute top-5 left-5 w-6 h-6">
                  <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-yellow-600/60 to-transparent"/>
                  <div className="absolute top-0 left-0 w-px h-full bg-gradient-to-b from-yellow-600/60 to-transparent"/>
                </div>
                <div className="absolute top-5 right-5 w-6 h-6">
                  <div className="absolute top-0 right-0 w-full h-px bg-gradient-to-l from-yellow-600/60 to-transparent"/>
                  <div className="absolute top-0 right-0 w-px h-full bg-gradient-to-b from-yellow-600/60 to-transparent"/>
                </div>
                <div className="absolute bottom-5 left-5 w-6 h-6">
                  <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-yellow-600/60 to-transparent"/>
                  <div className="absolute bottom-0 left-0 w-px h-full bg-gradient-to-t from-yellow-600/60 to-transparent"/>
                </div>
                <div className="absolute bottom-5 right-5 w-6 h-6">
                  <div className="absolute bottom-0 right-0 w-full h-px bg-gradient-to-l from-yellow-600/60 to-transparent"/>
                  <div className="absolute bottom-0 right-0 w-px h-full bg-gradient-to-t from-yellow-600/60 to-transparent"/>
                </div>

                <div className="flex gap-6">
                  {/* Contact Details */}
                  <div className="flex-1 space-y-5">
                    {/* Phone */}
                    <a href={`tel:${contact.phone}`} className="flex items-center space-x-4 group/item" onClick={e => e.stopPropagation()}>
                      <div className="w-11 h-11 rounded-full flex items-center justify-center transition-all duration-300 relative"
                        style={{
                          background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, transparent 100%)',
                          border: '1px solid rgba(212,175,55,0.25)'
                        }}>
                        <div className="absolute inset-0 rounded-full bg-yellow-600/10 opacity-0 group-hover/item:opacity-100 transition-opacity"/>
                        <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-neutral-600 text-xs tracking-[0.2em] uppercase">Phone</p>
                        <p className="text-white font-light tracking-wider mt-0.5">{contact.phoneDisplay}</p>
                      </div>
                    </a>
                    
                    {/* Email */}
                    <a href={`mailto:${contact.email}`} className="flex items-center space-x-4 group/item" onClick={e => e.stopPropagation()}>
                      <div className="w-11 h-11 rounded-full flex items-center justify-center transition-all duration-300 relative"
                        style={{
                          background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, transparent 100%)',
                          border: '1px solid rgba(212,175,55,0.25)'
                        }}>
                        <div className="absolute inset-0 rounded-full bg-yellow-600/10 opacity-0 group-hover/item:opacity-100 transition-opacity"/>
                        <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-neutral-600 text-xs tracking-[0.2em] uppercase">Email</p>
                        <p className="text-white font-light text-sm tracking-wide mt-0.5 break-all">{contact.email}</p>
                      </div>
                    </a>
                    
                    {/* Website */}
                    <a href={contact.website} target="_blank" rel="noopener noreferrer" className="flex items-center space-x-4 group/item" onClick={e => e.stopPropagation()}>
                      <div className="w-11 h-11 rounded-full flex items-center justify-center transition-all duration-300 relative"
                        style={{
                          background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, transparent 100%)',
                          border: '1px solid rgba(212,175,55,0.25)'
                        }}>
                        <div className="absolute inset-0 rounded-full bg-yellow-600/10 opacity-0 group-hover/item:opacity-100 transition-opacity"/>
                        <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-neutral-600 text-xs tracking-[0.2em] uppercase">Web</p>
                        <p className="text-white font-light text-sm tracking-wide mt-0.5">{contact.websiteDisplay}</p>
                      </div>
                    </a>
                    
                    {/* Location */}
                    <div className="flex items-center space-x-4">
                      <div className="w-11 h-11 rounded-full flex items-center justify-center"
                        style={{
                          background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, transparent 100%)',
                          border: '1px solid rgba(212,175,55,0.25)'
                        }}>
                        <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-neutral-600 text-xs tracking-[0.2em] uppercase">Location</p>
                        <p className="text-white font-light tracking-wide mt-0.5">{contact.city}, {contact.state}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* QR Code */}
                  <div className="w-28 flex-shrink-0 flex flex-col items-center justify-center">
                    <div className="p-3 rounded-xl relative"
                      style={{
                        background: 'linear-gradient(135deg, rgba(212,175,55,0.1) 0%, rgba(0,0,0,0.5) 100%)',
                        border: '1px solid rgba(212,175,55,0.2)'
                      }}>
                      <div className="w-20 h-20">
                        <QRCode />
                      </div>
                    </div>
                    <p className="text-neutral-600 text-xs tracking-[0.3em] uppercase mt-3">Scan</p>
                  </div>
                </div>
                
                {/* Flip indicator */}
                <div className="mt-6 flex justify-center">
                  <div className="flex items-center space-x-3 text-neutral-700">
                    <div className="w-6 h-px bg-gradient-to-r from-transparent to-neutral-700"/>
                    <svg className="w-3 h-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <div className="w-6 h-px bg-gradient-to-l from-transparent to-neutral-700"/>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="mt-10 space-y-4">
          {/* AirDrop Button - Luxury Gold */}
          <button 
            onClick={shareContact}
            className="w-full px-8 py-5 rounded-2xl font-medium tracking-[0.25em] uppercase text-sm transition-all flex items-center justify-center space-x-4 relative overflow-hidden group"
            style={{
              background: 'linear-gradient(135deg, #8b6914 0%, #b8860b 20%, #d4af37 35%, #f5d998 50%, #d4af37 65%, #b8860b 80%, #8b6914 100%)',
              backgroundSize: '200% auto',
              boxShadow: '0 10px 40px rgba(212,175,55,0.3), inset 0 1px 0 rgba(255,255,255,0.2)'
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"/>
            <svg className="w-5 h-5 text-black relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            <span className="text-black relative z-10 font-semibold">Share via AirDrop</span>
          </button>
          
          {/* Secondary Row */}
          <div className="flex gap-4">
            <button 
              onClick={() => setShowNFCInfo(true)}
              className="flex-1 px-6 py-4 rounded-2xl font-medium tracking-[0.2em] uppercase text-xs transition-all flex items-center justify-center space-x-3 group relative overflow-hidden"
              style={{
                background: 'transparent',
                border: '1px solid rgba(212,175,55,0.3)',
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/0 via-yellow-600/10 to-yellow-600/0 opacity-0 group-hover:opacity-100 transition-opacity"/>
              <svg className="w-5 h-5 text-yellow-600 relative z-10" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 18H4V4h16v16zM8.93 8.93c-1.46 1.46-1.77 3.64-.93 5.4l-1.5 1.5c-1.56-2.48-1.23-5.78.93-7.94s5.46-2.49 7.94-.93l-1.5 1.5c-1.76-.84-3.94-.53-5.4.93zm1.41 1.41c-.78.78-.98 1.92-.59 2.88l-1.5 1.5c-1-1.67-.69-3.84.73-5.26s3.59-1.73 5.26-.73l-1.5 1.5c-.96-.39-2.1-.19-2.88.59z"/>
              </svg>
              <span className="text-yellow-600 relative z-10">NFC Tap</span>
            </button>
            
            <button 
              onClick={downloadVCard}
              className="flex-1 px-6 py-4 rounded-2xl font-medium tracking-[0.2em] uppercase text-xs transition-all flex items-center justify-center space-x-3 group relative overflow-hidden"
              style={{
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/5 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity"/>
              <svg className="w-5 h-5 text-neutral-400 group-hover:text-white transition-colors relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span className="text-neutral-400 group-hover:text-white transition-colors relative z-10">Save</span>
            </button>
          </div>
        </div>
        
        {/* Footer */}
        <div className="mt-10 text-center">
          <div className="flex items-center justify-center space-x-4">
            <div className="w-12 h-px bg-gradient-to-r from-transparent to-yellow-900/50"/>
            <p className="text-neutral-700 text-xs tracking-[0.4em] uppercase font-light">
              Tap · Share · Connect
            </p>
            <div className="w-12 h-px bg-gradient-to-l from-transparent to-yellow-900/50"/>
          </div>
        </div>
      </div>
    </div>
  );
}
