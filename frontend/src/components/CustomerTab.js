import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CustomerTab.css';

function CustomerTab({ user, onLogin, cart, onAddToCart, showToast }) {
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');
  const [activeAct, setActiveAct] = useState('act1');
  const [products, setProducts] = useState([]);
  const [stores, setStores] = useState([]);
  const [partners, setPartners] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedStore, setSelectedStore] = useState(null);
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [selectedPartnerCategory, setSelectedPartnerCategory] = useState(null);

  useEffect(() => {
    // Fetch reference data from backend
    const fetchData = async () => {
      try {
        const [productsRes, storesRes, partnersRes, usersRes] = await Promise.all([
          axios.get('/api/products'),
          axios.get('/api/stores'),
          axios.get('/api/partners'),
          axios.get('/api/users'),
        ]);
        setProducts(productsRes.data);
        setStores(storesRes.data);
        setPartners(partnersRes.data);
        setUsers(usersRes.data);
      } catch (error) {
        console.error('Error fetching reference data:', error);
      }
    };

    fetchData();
  }, []);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError('');

    try {
      const response = await axios.post('/api/login', loginForm);
      onLogin(response.data);
    } catch (error) {
      setLoginError(error.response?.data?.error || 'Login failed');
    }
  };

  const handleViewProduct = async (product) => {
    // Open modal
    setSelectedProduct(product);

    // Send VIEW_PRODUCT event to Kafka
    await axios.post('/api/events/view-product', {
      product_id: product.product_id,
      product_name: product.name,
      category: product.category,
      price: product.price,
      description: product.description
    });
  };

  const handleCloseModal = () => {
    setSelectedProduct(null);
  };

  const handleAddToCart = async (product) => {
    await axios.post('/api/events/add-to-cart', {
      product_id: product.product_id,
      product_name: product.name,
      price: product.price,
      quantity: 1
    });

    onAddToCart(product);
    showToast(`${product.name} added to cart!`, 'success');

    // Close modal after adding to cart
    setSelectedProduct(null);
  };

  const handleStoreEntry = async (store) => {
    await axios.post('/api/events/store-entry', {
      store_id: store.store_id,
      store_name: store.name,
      location: store.location
    });

    showToast(`Entered ${store.name}! Check the Dashboard for personalized experience.`, 'success');
  };

  const handlePartnerCategoryClick = (partner, category) => {
    // Open modal first
    setSelectedPartner(partner);
    setSelectedPartnerCategory(category);
  };

  const handlePartnerBrowse = async (partner, category) => {
    await axios.post('/api/events/partner-browse', {
      partner_name: partner.name,
      category: category
    });

    showToast(`Browsing ${category} on ${partner.name}! Check the Dashboard for retail media ads.`, 'info');

    // Close modal after browsing
    setSelectedPartner(null);
    setSelectedPartnerCategory(null);
  };

  const handleActChange = (act) => {
    setActiveAct(act);
    // Reset category filter when switching acts
    if (act === 'act1') {
      setSelectedCategory('All');
    }
  };

  if (!user) {
    return (
      <div className="login-container">
        <div className="login-card card">
          <h2>Welcome to UrbanStreet</h2>
          <p>Please login to continue your shopping journey</p>

          <form onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                placeholder="Enter your username"
                autoComplete="off"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                placeholder="Enter your password"
                autoComplete="new-password"
                required
              />
            </div>

            {loginError && <div className="error">{loginError}</div>}

            <button type="submit" className="btn btn-primary btn-block">
              Login
            </button>
          </form>

          <div className="demo-credentials">
            <p><strong>Demo credentials:</strong></p>
            {users.length > 0 && (
              <>
                <p>Username: <code>{users[0].username}</code> | Password: <code>secret</code></p>
                <p className="hint">
                  Other users: {users.slice(1).map(u => u.username).join(', ')}
                </p>
              </>
            )}
            {users.length === 0 && (
              <p className="hint">Loading users...</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="customer-container">
      <div className="act-tabs">
        <button
          className={`act-tab ${activeAct === 'act1' ? 'active' : ''}`}
          onClick={() => handleActChange('act1')}
        >
          🎬 Acts 1 & 2: Online Discovery
        </button>
        <button
          className={`act-tab ${activeAct === 'act3' ? 'active' : ''}`}
          onClick={() => handleActChange('act3')}
        >
          🏪 Act 3: In-Store Experience
        </button>
        <button
          className={`act-tab ${activeAct === 'act4' ? 'active' : ''}`}
          onClick={() => handleActChange('act4')}
        >
          🤝 Act 4: Partner Experience
        </button>
      </div>

      {activeAct === 'act1' && (
        <div className="demo-section">
          <p className="act-description">
            Browse products and experience localized, AI-powered recommendations
          </p>

          <div className="products-layout">
            <div className="categories-sidebar card">
              <h3>Categories</h3>
              <div className="category-list">
                <button
                  className={`category-item ${selectedCategory === 'All' ? 'active' : ''}`}
                  onClick={() => setSelectedCategory('All')}
                >
                  All Products
                </button>
                {[...new Set(products.map(p => p.category))]
                  .sort()
                  .map(category => (
                    <button
                      key={category}
                      className={`category-item ${selectedCategory === category ? 'active' : ''}`}
                      onClick={() => setSelectedCategory(category)}
                    >
                      {category}
                    </button>
                  ))}
              </div>
            </div>

            <div className="products-grid">
              {products
                .filter(product => selectedCategory === 'All' || product.category === selectedCategory)
                .sort((a, b) => a.category.localeCompare(b.category))
                .map(product => (
                  <div
                    key={product.product_id}
                    className="product-card card clickable"
                    onClick={() => handleViewProduct(product)}
                  >
                    <div className="product-image">{product.icon}</div>
                    <h3>{product.name}</h3>
                    <p className="category">{product.category}</p>
                    <p className="price">${product.price.toFixed(2)}</p>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {activeAct === 'act3' && (
        <div className="demo-section">
          <p className="act-description">
            Visit a physical store and get personalized service based on your online activity
          </p>

          <div className="stores-grid">
            {stores.map(store => (
              <div
                key={store.store_id}
                className="store-card card clickable"
                onClick={() => setSelectedStore(store)}
              >
                <h3>{store.icon} {store.name}</h3>
                <p>{store.location}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeAct === 'act4' && (
        <div className="demo-section">
          <p className="act-description">
            Browse on partner marketplaces and see real-time retail media placements
          </p>

          <div className="partners-grid">
            {partners.map(partner => (
              <div key={partner.partner_id} className="partner-card card">
                <h3>{partner.icon} {partner.name}</h3>
                <p>Browse categories:</p>
                <div className="partner-categories">
                  {Object.keys(partner.categories || {}).map(category => (
                    <button
                      key={category}
                      className="btn btn-secondary category-btn"
                      onClick={() => handlePartnerCategoryClick(partner, category)}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedProduct.name}</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="modal-product-icon">{selectedProduct.icon}</div>
              <p className="modal-category">{selectedProduct.category}</p>
              <p className="modal-price">${selectedProduct.price.toFixed(2)}</p>
              <p className="modal-description">{selectedProduct.description}</p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={handleCloseModal}>
                Close
              </button>
              <button className="btn btn-primary" onClick={() => handleAddToCart(selectedProduct)}>
                Add to Cart
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Store Detail Modal */}
      {selectedStore && (
        <div className="modal-overlay" onClick={() => setSelectedStore(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedStore.icon} {selectedStore.name}</h2>
              <button className="modal-close" onClick={() => setSelectedStore(null)}>×</button>
            </div>
            <div className="modal-body">
              <p className="modal-location"><strong>Location:</strong> {selectedStore.location}</p>
              {selectedStore.promotions && selectedStore.promotions.length > 0 && (
                <>
                  <h3>Store Promotions:</h3>
                  <ul className="store-promotions-list">
                    {selectedStore.promotions.map((feature, index) => (
                      <li key={index}>{feature}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectedStore(null)}>
                Close
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  handleStoreEntry(selectedStore);
                  setSelectedStore(null);
                }}
              >
                Enter Store
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Partner Category Modal */}
      {selectedPartner && selectedPartnerCategory && (
        <div className="modal-overlay" onClick={() => { setSelectedPartner(null); setSelectedPartnerCategory(null); }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedPartner.icon} {selectedPartner.name}</h2>
              <button className="modal-close" onClick={() => { setSelectedPartner(null); setSelectedPartnerCategory(null); }}>×</button>
            </div>
            <div className="modal-body">
              <p className="modal-category"><strong>Category:</strong> {selectedPartnerCategory}</p>
              {selectedPartner.categories[selectedPartnerCategory] && selectedPartner.categories[selectedPartnerCategory].length > 0 && (
                <>
                  <h3>Available Promotions:</h3>
                  <ul className="store-promotions-list">
                    {selectedPartner.categories[selectedPartnerCategory].map((promotion, index) => (
                      <li key={index}>{promotion}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => { setSelectedPartner(null); setSelectedPartnerCategory(null); }}>
                Close
              </button>
              <button
                className="btn btn-primary"
                onClick={() => handlePartnerBrowse(selectedPartner, selectedPartnerCategory)}
              >
                Browse Category
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomerTab;
