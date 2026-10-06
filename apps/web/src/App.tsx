import React, { useState } from 'react';

// A mock UI for the core flow to demonstrate the frontend requirements

const App = () => {
  const [sessionState, setSessionState] = useState<'idle' | 'recording' | 'processing' | 'review'>('idle');
  const [language, setLanguage] = useState('ta');
  
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold text-xl shadow-md">
              A
            </div>
            <h1 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600">
              AcoustiStruct
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-slate-100 border-none rounded-lg px-3 py-1.5 text-sm font-medium focus:ring-2 focus:ring-primary-500 outline-none"
            >
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="en">English</option>
            </select>
            <div className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white shadow-sm flex items-center justify-center text-slate-600 font-medium">
              FW
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-6 lg:p-8 flex flex-col gap-6">
        
        {/* Welcome / Dashboard State */}
        {sessionState === 'idle' && (
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div className="w-20 h-20 bg-primary-100 text-primary-600 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-4 tracking-tight">Agriculture Field Assessment</h2>
            <p className="text-slate-500 max-w-md mb-10 text-lg">
              Speak naturally in your local dialect. The AI will extract and structure the information automatically.
            </p>
            <button 
              onClick={() => setSessionState('recording')}
              className="btn-primary text-lg px-8 py-4 w-full md:w-auto"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
              Start New Session
            </button>
          </div>
        )}

        {/* Recording State */}
        {sessionState === 'recording' && (
          <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
            <div className="relative mb-12">
              <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-20"></div>
              <div className="w-24 h-24 bg-red-50 text-red-500 rounded-full flex items-center justify-center border-4 border-white shadow-xl relative z-10">
                <svg className="w-10 h-10 animate-pulse-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
              </div>
            </div>
            
            <div className="text-center mb-12 max-w-2xl">
              <p className="text-sm font-medium text-red-500 uppercase tracking-wider mb-3">Recording Live</p>
              <p className="text-2xl md:text-3xl font-medium text-slate-800 leading-relaxed text-left opacity-80 border-l-4 border-primary-200 pl-6 py-2">
                "என் பெயர் ராமசாமி. நான் மதுரை மாவட்டம் திருமங்கலம் கிராமத்தில் இருக்கிறேன். என்கிட்ட இரண்டரை ஏக்கர்..."
              </p>
            </div>

            <div className="flex gap-4">
              <button className="btn-secondary">Pause</button>
              <button 
                onClick={() => setSessionState('processing')}
                className="btn-primary bg-gradient-to-r from-slate-800 to-slate-900 shadow-slate-900/20"
              >
                Stop & Process
              </button>
            </div>
          </div>
        )}

        {/* Processing State */}
        {sessionState === 'processing' && (
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div className="w-16 h-16 border-4 border-slate-200 border-t-primary-500 rounded-full animate-spin mb-8"></div>
            <h3 className="text-xl font-semibold mb-2">Analyzing Speech</h3>
            <p className="text-slate-500">Transcribing, normalizing dialect, and extracting fields...</p>
            
            {/* Auto advance for demo purposes */}
            {setTimeout(() => setSessionState('review'), 3000) && null}
          </div>
        )}

        {/* Review State */}
        {sessionState === 'review' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in pb-20">
            {/* Left Col: Transcript & Evidence */}
            <div className="lg:col-span-1 space-y-6">
              <div className="glass-card p-5">
                <h3 className="font-semibold text-slate-800 mb-4 flex items-center justify-between">
                  <span>Transcript</span>
                  <span className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-600">southern_tamil (0.85)</span>
                </h3>
                <div className="space-y-3 text-sm text-slate-700 leading-relaxed max-h-[400px] overflow-y-auto pr-2">
                  <p><span className="text-primary-600 bg-primary-50 font-medium px-1 rounded cursor-pointer">என் பெயர் ராமசாமி.</span> நான் மதுரை மாவட்டம் திருமங்கலம் கிராமத்தில் இருக்கிறேன்.</p>
                  <p>என்கிட்ட <span className="bg-amber-100 px-1 rounded cursor-pointer">இரண்டரை ஏக்கர்</span> நிலம் இருக்கு. நெல் பயிர் போட்டிருக்கேன்.</p>
                  <p>கிணத்து நீர்ப்பாசனம் பயன்படுத்துறேன். இந்த வருஷம் மழை குறைவா இருக்கு. மண் வளம் நடுத்தரமா இருக்கு.</p>
                  <p>யூரியா உரம் போட்டிருக்கேன். காய்ப்புழு பாதிப்பு இருக்கு.</p>
                  <p>சுமார் முப்பது சதவிகிதம் பயிர் சேதம் ஆயிருக்கு. <span className="bg-red-100 px-1 rounded cursor-pointer border border-red-200">ஏறக்குறைய ஐம்பதாயிரம் ரூபாய் நஷ்டம் இருக்கும்னு நினைக்கிறேன்.</span></p>
                </div>
              </div>
            </div>

            {/* Right Col: Extracted Fields */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-800">Verification</h2>
                <div className="flex gap-3">
                  <button onClick={() => setSessionState('idle')} className="btn-secondary py-2 text-sm">Discard</button>
                  <button onClick={() => setSessionState('idle')} className="btn-primary py-2 text-sm">Generate Report</button>
                </div>
              </div>

              {/* Clarification Alert */}
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-4 items-start shadow-sm">
                <div className="w-8 h-8 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                </div>
                <div>
                  <h4 className="font-semibold text-amber-900">Clarification Needed</h4>
                  <p className="text-amber-800 text-sm mt-1 mb-3">I detected 'ஏறக்குறைய ஐம்பதாயிரம் ரூபாய்' for Estimated Loss, but the speaker sounded uncertain. Can you confirm?</p>
                  <div className="flex gap-2">
                    <button className="bg-white text-sm border border-amber-300 text-amber-700 px-3 py-1.5 rounded-lg hover:bg-amber-100 font-medium">Confirm 50000</button>
                    <button className="bg-white text-sm border border-amber-300 text-amber-700 px-3 py-1.5 rounded-lg hover:bg-amber-100 font-medium">Edit Value</button>
                  </div>
                </div>
              </div>

              {/* Data Grid */}
              <div className="glass-card overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-sm uppercase tracking-wider">
                      <th className="p-4 font-medium">Field</th>
                      <th className="p-4 font-medium">Value</th>
                      <th className="p-4 font-medium w-32">Status</th>
                      <th className="p-4 font-medium w-16"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr className="hover:bg-slate-50 transition-colors group">
                      <td className="p-4 font-medium text-slate-700">Farmer Name</td>
                      <td className="p-4 text-slate-900 font-semibold">Ramasamy</td>
                      <td className="p-4"><span className="status-badge status-extracted">AI Extracted</span></td>
                      <td className="p-4 text-slate-400">
                        <button className="hover:text-primary-600">✎</button>
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50 transition-colors group">
                      <td className="p-4 font-medium text-slate-700">Village</td>
                      <td className="p-4 text-slate-900 font-semibold">Thirumangalam</td>
                      <td className="p-4"><span className="status-badge status-extracted">AI Extracted</span></td>
                      <td className="p-4 text-slate-400">
                        <button className="hover:text-primary-600">✎</button>
                      </td>
                    </tr>
                    <tr className="bg-primary-50/50 hover:bg-primary-50 transition-colors group">
                      <td className="p-4 font-medium text-slate-700">Land Area</td>
                      <td className="p-4 text-slate-900 font-semibold flex items-baseline gap-2">
                        2.5 <span className="text-sm font-normal text-slate-500">acre</span>
                      </td>
                      <td className="p-4"><span className="status-badge status-verified">Verified</span></td>
                      <td className="p-4 text-slate-400">
                        <button className="hover:text-primary-600">✎</button>
                      </td>
                    </tr>
                    <tr className="bg-amber-50/30 hover:bg-amber-50/50 transition-colors group border-l-2 border-l-amber-400">
                      <td className="p-4 font-medium text-slate-700">Estimated Loss</td>
                      <td className="p-4 text-slate-900 font-semibold flex items-baseline gap-2">
                        50000 <span className="text-sm font-normal text-slate-500">Rs</span>
                      </td>
                      <td className="p-4"><span className="status-badge status-review">Needs Review</span></td>
                      <td className="p-4 text-slate-400">
                        <button className="hover:text-primary-600">✎</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
