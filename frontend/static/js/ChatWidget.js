// AI Chatbot Component for AI Smart Food OS
// Standalone React component to be loaded via Babel CDN

const { useState, useEffect, useRef } = React;

function ChatWidget() {
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState([
        { id: 1, role: 'ai', content: "👋 Hello! I'm your AI Food Concierge. Tell me your budget, mood, or health goal and I'll find the perfect meal for you!" }
    ]);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (open) scrollToBottom();
    }, [messages, open]);

    async function send() {
        const msg = input.trim();
        if (!msg) return;
        
        setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: msg }]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', content: data.reply }]);
        } catch(e) {
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', content: '⚠️ Neural link interrupted. Please try again.' }]);
        }
        setLoading(false);
    }

    function quickSend(text) {
        setInput(text);
        // We can't immediately call send() because state update is async, 
        // so we handle it manually or just set input and let user click send.
        // For better UX, let's trigger it:
        setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: text }]);
        setLoading(true);
        fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        }).then(res => res.json())
          .then(data => {
              setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', content: data.reply }]);
              setLoading(false);
          })
          .catch(() => {
              setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', content: '⚠️ Error.' }]);
              setLoading(false);
          });
    }

    return (
        <div id="chat-widget-root">
            <button className={`chat-fab ${open ? 'active' : ''}`} 
                    onClick={() => setOpen(!open)}
                    style={{fontSize: '1.4rem', transform: open ? 'scale(1.05) rotate(-10deg)' : 'none'}}>
                {!open ? '🤖' : '✕'}
            </button>

            {open && (
                <div className="chat-panel" style={{display: 'flex', flexDirection: 'column'}}>
                    <div className="chat-header">
                        <div className="chat-header-dot"></div>
                        <div>
                            <div className="chat-title">AI Food Concierge</div>
                            <div className="chat-subtitle">Powered by Synthetix Intelligence</div>
                        </div>
                    </div>

                    <div className="chat-messages" style={{flex: 1, overflowY: 'auto'}}>
                        {messages.map(msg => (
                            <div key={msg.id} className={`chat-bubble ${msg.role}`}>
                                {msg.content}
                            </div>
                        ))}
                        {loading && (
                            <div className="chat-bubble ai" style={{display: 'flex', gap: '4px', alignItems: 'center'}}>
                                <span className="dot-pulse">●</span>
                                <span className="dot-pulse" style={{animationDelay: '0.2s'}}>●</span>
                                <span className="dot-pulse" style={{animationDelay: '0.4s'}}>●</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chat-suggestions">
                        <button className="chat-suggestion-btn" onClick={() => quickSend('I have ₹150 for dinner')}>₹150 dinner</button>
                        <button className="chat-suggestion-btn" onClick={() => quickSend('Healthy high-protein meal')}>High protein</button>
                        <button className="chat-suggestion-btn" onClick={() => quickSend('Emergency budget mode')}>🆘 Emergency</button>
                    </div>

                    <div className="chat-input-row">
                        <input className="chat-input" 
                               value={input} 
                               onChange={e => setInput(e.target.value)}
                               onKeyUp={e => e.key === 'Enter' && send()}
                               placeholder="Tell me your mood, budget, goal..." 
                               autoComplete="off" />
                        <button className="chat-send" onClick={send}>▶</button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Render into footer container if exists
const chatContainer = document.createElement('div');
chatContainer.id = 'chat-widget-mounting-point';
document.body.appendChild(chatContainer);
const chatRoot = ReactDOM.createRoot(chatContainer);
chatRoot.render(<ChatWidget />);
