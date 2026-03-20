import React from 'react';
import './CartModal.css';

function CartModal({ cart, onClose, onAbandonCart, onContinueShopping }) {
  const cartTotal = cart.reduce((sum, item) => sum + item.price, 0);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🛒 Your Shopping Cart</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {cart.length === 0 ? (
            <div className="empty-cart">
              <p>Your cart is empty</p>
              <p className="hint">Browse products and add items to your cart</p>
            </div>
          ) : (
            <>
              <div className="cart-items-list">
                {cart.map((item, idx) => (
                  <div key={idx} className="cart-modal-item">
                    <span className="item-icon">{item.image}</span>
                    <div className="item-details">
                      <div className="item-name">{item.name}</div>
                      <div className="item-category">{item.category}</div>
                    </div>
                    <div className="item-price">${item.price.toFixed(2)}</div>
                  </div>
                ))}
              </div>

              <div className="cart-total-section">
                <div className="cart-total-label">Total:</div>
                <div className="cart-total-value">${cartTotal.toFixed(2)}</div>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          {cart.length > 0 && (
            <button className="btn btn-danger" onClick={onAbandonCart}>
              Emulate Abandon Cart<br></br>(Act 2)
            </button>
          )}
          <button className="btn btn-primary" onClick={onContinueShopping}>
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
}

export default CartModal;
