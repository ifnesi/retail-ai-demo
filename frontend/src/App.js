import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import CustomerTab from './components/CustomerTab';
import KafkaTab from './components/KafkaTab';
import DashboardTab from './components/DashboardTab';
import CartModal from './components/CartModal';
import Toast from './components/Toast';

axios.defaults.withCredentials = true;

function App() {
  const [activeTab, setActiveTab] = useState('customer');
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]);
  const [showCartModal, setShowCartModal] = useState(false);
  const [toast, setToast] = useState(null);
  const [aiPredictions, setAiPredictions] = useState({
    cart_recovery: [],
    store_context: [],
    partner_ads: []
  });
  const shownPredictionsRef = React.useRef(new Set());

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  useEffect(() => {
    // Check for existing session
    axios.get('/api/session')
      .then(response => {
        setUser(response.data);
      })
      .catch(() => {
        // No active session
      });
  }, []);

  useEffect(() => {
    // Fetch AI predictions continuously in background
    const fetchAIPredictions = async () => {
      try {
        const aiResponse = await axios.get('/api/ai/predictions');
        setAiPredictions(aiResponse.data);
      } catch (error) {
        console.error('Error fetching AI predictions:', error);
      }
    };

    // Only fetch if user is logged in
    if (user) {
      fetchAIPredictions();
      const interval = setInterval(fetchAIPredictions, 3000);
      return () => clearInterval(interval);
    }
  }, [user]);

  useEffect(() => {
    // Show toast notifications for new AI predictions

    // Cart Recovery
    aiPredictions.cart_recovery.forEach(pred => {
      const key = `cart_recovery_${pred.timestamp}`;
      if (!shownPredictionsRef.current.has(key)) {
        shownPredictionsRef.current.add(key);
        const data = pred.data;
        let nudgeMessage = 'AI cart recovery message generated';
        const possibleFields = [data.llm_output, data.ai_llm_output, data.ai_recovery_message];
        for (let field of possibleFields) {
          if (field) {
            if (typeof field === 'string') {
              nudgeMessage = field;
              break;
            } else if (field.string) {
              nudgeMessage = field.string;
              break;
            }
          }
        }
        showToast(`💰 AI Cart Recovery: ${nudgeMessage}`, 'success');
      }
    });

    // Store Context
    aiPredictions.store_context.forEach(pred => {
      const key = `store_context_${pred.timestamp}`;
      if (!shownPredictionsRef.current.has(key)) {
        shownPredictionsRef.current.add(key);
        const data = pred.data;
        let welcomeMessage = 'AI welcome message generated';
        if (data.llm_output) {
          if (typeof data.llm_output === 'string') {
            welcomeMessage = data.llm_output;
          } else if (data.llm_output.string) {
            welcomeMessage = data.llm_output.string;
          }
        }
        showToast(`🏪 AI In-Store Context: ${welcomeMessage}`, 'success');
      }
    });

    // Partner Ads
    aiPredictions.partner_ads.forEach(pred => {
      const key = `partner_ads_${pred.timestamp}`;
      if (!shownPredictionsRef.current.has(key)) {
        shownPredictionsRef.current.add(key);
        const data = pred.data;
        let adCopy = 'AI ad copy generated';
        if (data.llm_output) {
          if (typeof data.llm_output === 'string') {
            adCopy = data.llm_output;
          } else if (data.llm_output.string) {
            adCopy = data.llm_output.string;
          }
        }
        showToast(`📢 AI Partner Retail Media: ${adCopy}`, 'success');
      }
    });
  }, [aiPredictions]);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    axios.post('/api/logout')
      .then(() => {
        setUser(null);
        setCart([]);
        setActiveTab('customer'); // Reset to customer tab to show login page
      });
  };

  const handleAddToCart = (product) => {
    setCart([...cart, product]);
  };

  const handleAbandonCart = async () => {
    if (cart.length === 0) {
      showToast('Cart is empty!', 'warning');
      return;
    }

    const cartValue = cart.reduce((sum, item) => sum + item.price, 0);
    await axios.post('/api/events/abandon-cart', {
      cart_value: cartValue,
      items_count: cart.length
    });

    showToast('Cart abandoned! Check the Dashboard for AI nudge response.', 'info');
    setCart([]);
    setShowCartModal(false);
  };

  const handleContinueShopping = () => {
    setShowCartModal(false);
  };

  return (
    <div className={`App ${user ? `app-${activeTab}` : ''}`}>
      <header className="App-header">
        <div className="header-content">
          <h1>
            <img src="/logo.svg" alt="UrbanStreet" className="header-logo" />
            UrbanStreet
          </h1>
          <p className="subtitle">
            Retail AI Demo - Powered by Confluent Cloud
            <img src="/cflt-logo.png" alt="Confluent" className="confluent-logo"/>
          </p>
        </div>
        {user && (
          <div className="user-info">
            <div className="user-greeting">
              <span>Welcome, {user.first_name}!</span>
              {user.customer_tier && (
                <span className={`customer-tier-badge tier-${user.customer_tier.toLowerCase()}`}>
                  {user.customer_tier}
                </span>
              )}
            </div>
            <button onClick={() => setShowCartModal(true)} className="cart-btn">
              🛒 Cart ({cart.length})
            </button>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        )}
      </header>

      {user && (
        <nav className="tabs">
          <button
            className={`tab tab-customer ${activeTab === 'customer' ? 'active' : ''}`}
            onClick={() => setActiveTab('customer')}
          >
            👤 Customer
          </button>
          <button
            className={`tab tab-kafka ${activeTab === 'kafka' ? 'active' : ''}`}
            onClick={() => setActiveTab('kafka')}
          >
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Apache_Kafka_logo.svg/250px-Apache_Kafka_logo.svg.png"
              alt="Kafka"
              style={{ height: '1em', verticalAlign: 'middle', marginRight: '0.5rem' }}
            />
            Kafka Events
          </button>
          <button
            className={`tab tab-dashboard ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📈 Dashboard
          </button>
        </nav>
      )}

      <main className={`content ${user ? `content-${activeTab}` : ''}`}>
        {activeTab === 'customer' && (
          <CustomerTab
            user={user}
            onLogin={handleLogin}
            cart={cart}
            onAddToCart={handleAddToCart}
            showToast={showToast}
          />
        )}
        {activeTab === 'kafka' && <KafkaTab />}
        {activeTab === 'dashboard' && <DashboardTab user={user} aiPredictions={aiPredictions} />}
      </main>

      <footer className="footer">
        <p>Demo Flow: Act 1 (Discovery) → Act 2 (Cart Abandonment) → Act 3 (In-Store) → Act 4 (Partner) → Act 5 (Analytics)</p>
      </footer>

      {showCartModal && (
        <CartModal
          cart={cart}
          onClose={handleContinueShopping}
          onAbandonCart={handleAbandonCart}
          onContinueShopping={handleContinueShopping}
        />
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

export default App;
