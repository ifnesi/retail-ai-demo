import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './KafkaTab.css';

const TOPIC_ALIASES = {
  'db_public_users': 'View Customers',
  'RETAIL_DEMO_VIEW_PRODUCT': 'View Product',
  'RETAIL_DEMO_ADD_TO_CART': 'Add to Cart',
  'RETAIL_DEMO_ABANDON_CART': 'Abandon Cart',
  'RETAIL_DEMO_STORE_ENTRY': 'Store Entry',
  'RETAIL_DEMO_PARTNER_BROWSE': 'Partner Browse'
};

const TOPICS = Object.keys(TOPIC_ALIASES);

function KafkaTab() {
  const [events, setEvents] = useState({});
  const [selectedTopic, setSelectedTopic] = useState('RETAIL_DEMO_VIEW_PRODUCT');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchEvents();

    if (autoRefresh) {
      const interval = setInterval(fetchEvents, 2000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchEvents = async () => {
    try {
      const response = await axios.get('/api/events/latest');
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await fetchEvents();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const formatEventTimestamp = (ms) => {
    const date = new Date(parseInt(ms));
    return date.toLocaleString();
  };

  const renderEventDetails = (event) => {
    if (!event || !event.data) return null;

    const data = event.data;

    return (
      <div className="event-details">
        {selectedTopic === 'db_public_users' && (
          <>
            <div className="event-row">
              <span className="label">Username:</span>
              <span className="value">{data.username}</span>
            </div>
            <div className="event-row">
              <span className="label">First Name:</span>
              <span className="value">{data.first_name}</span>
            </div>
            <div className="event-row">
              <span className="label">Last Name:</span>
              <span className="value">{data.last_name}</span>
            </div>
            <div className="event-row">
              <span className="label">Date of Birth:</span>
              <span className="value">{data.date_of_birth}</span>
            </div>
            <div className="event-row">
              <span className="label">Customer Tier:</span>
              <span className="value">
                <span className={`customer-tier-badge tier-${data.customer_tier?.toLowerCase()}`}>
                  {data.customer_tier}
                </span>
              </span>
            </div>
          </>
        )}

        {selectedTopic !== 'db_public_users' && (
          <>
            <div className="event-row">
              <span className="label">Event ID:</span>
              <span className="value">{data.event_id}</span>
            </div>
            <div className="event-row">
              <span className="label">Username:</span>
              <span className="value">{data.username}</span>
            </div>
          </>
        )}

        {selectedTopic === 'RETAIL_DEMO_VIEW_PRODUCT' && (
          <>
            <div className="event-row">
              <span className="label">Product:</span>
              <span className="value">{data.product_name} ({data.product_id})</span>
            </div>
            <div className="event-row">
              <span className="label">Category:</span>
              <span className="value">{data.category}</span>
            </div>
            <div className="event-row">
              <span className="label">Price:</span>
              <span className="value">${data.price?.toFixed(2)}</span>
            </div>
          </>
        )}

        {selectedTopic === 'RETAIL_DEMO_ADD_TO_CART' && (
          <>
            <div className="event-row">
              <span className="label">Product:</span>
              <span className="value">{data.product_name} ({data.product_id})</span>
            </div>
            <div className="event-row">
              <span className="label">Quantity:</span>
              <span className="value">{data.quantity}</span>
            </div>
            <div className="event-row">
              <span className="label">Price:</span>
              <span className="value">${data.price?.toFixed(2)}</span>
            </div>
          </>
        )}

        {selectedTopic === 'RETAIL_DEMO_ABANDON_CART' && (
          <>
            <div className="event-row">
              <span className="label">Customer Tier:</span>
              <span className="value">
                <span className={`customer-tier-badge tier-${data.customer_tier?.toLowerCase()}`}>
                  {data.customer_tier}
                </span>
              </span>
            </div>
            <div className="event-row">
              <span className="label">Cart Value:</span>
              <span className="value">${data.cart_value?.toFixed(2)}</span>
            </div>
            <div className="event-row">
              <span className="label">Items Count:</span>
              <span className="value">{data.items_count}</span>
            </div>
          </>
        )}

        {selectedTopic === 'RETAIL_DEMO_STORE_ENTRY' && (
          <>
            <div className="event-row">
              <span className="label">Customer Tier:</span>
              <span className="value">
                <span className={`customer-tier-badge tier-${data.customer_tier?.toLowerCase()}`}>
                  {data.customer_tier}
                </span>
              </span>
            </div>
            <div className="event-row">
              <span className="label">Store:</span>
              <span className="value">{data.store_name} ({data.store_id})</span>
            </div>
            <div className="event-row">
              <span className="label">Location:</span>
              <span className="value">{data.location}</span>
            </div>
            {data.promotions && (
              <div className="event-row event-row-full">
                <span className="label">Promotions:</span>
                <span className="value promotions-list">
                  {data.promotions.split(';').map((promotion, idx) => (
                    <span key={idx} className="promotion-item">• {promotion}</span>
                  ))}
                </span>
              </div>
            )}
          </>
        )}

        {selectedTopic === 'RETAIL_DEMO_PARTNER_BROWSE' && (
          <>
            <div className="event-row">
              <span className="label">Customer Tier:</span>
              <span className="value">
                <span className={`customer-tier-badge tier-${data.customer_tier?.toLowerCase()}`}>
                  {data.customer_tier}
                </span>
              </span>
            </div>
            <div className="event-row">
              <span className="label">Partner:</span>
              <span className="value">{data.partner_name}</span>
            </div>
            <div className="event-row">
              <span className="label">Category:</span>
              <span className="value">{data.category}</span>
            </div>
            {data.promotions && (
              <div className="event-row event-row-full">
                <span className="label">Promotions:</span>
                <span className="value promotions-list">
                  {data.promotions.split(';').map((promotion, idx) => (
                    <span key={idx} className="promotion-item">• {promotion}</span>
                  ))}
                </span>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  const getTopicEventCount = (topic) => {
    return events[topic]?.length || 0;
  };

  const topicEvents = events[selectedTopic] || [];

  return (
    <div className="kafka-container">
      <div className="kafka-header card">
        <div>
          <h2>
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Apache_Kafka_logo.svg/250px-Apache_Kafka_logo.svg.png"
              alt="Kafka"
              style={{ height: '1.2em', verticalAlign: 'middle', marginRight: '0.5rem' }}
            />
            Real-Time Kafka Events
          </h2>
          <p>Streaming events from Confluent Cloud - Live view of customer journey data</p>
        </div>
        <div className="header-controls">
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (2s)
          </label>
          <button
            className={`btn btn-secondary ${isRefreshing ? 'refreshing' : ''}`}
            onClick={handleManualRefresh}
            disabled={isRefreshing}
          >
            🔄 Refresh Now
          </button>
        </div>
      </div>

      <div className="kafka-info card">
        <h3>🎯 Data Streaming Architecture</h3>
        <div className="info-grid">
          <div className="info-item">
            <strong>Platform:</strong> Confluent Cloud
          </div>
          <div className="info-item">
            <strong>Region:</strong> AWS eu-central-1
          </div>
          <div className="info-item">
            <strong>Schema Format:</strong> AVRO
          </div>
          <div className="info-item">
            <strong>Processing:</strong> Flink SQL
          </div>
        </div>
      </div>

      <div className="topics-nav">
        {TOPICS.map(topic => (
          <button
            key={topic}
            className={`topic-btn ${selectedTopic === topic ? 'active' : ''}`}
            onClick={() => setSelectedTopic(topic)}
          >
            <div className="topic-name">{TOPIC_ALIASES[topic]}</div>
            <div className="topic-count">
              {getTopicEventCount(topic)} events
            </div>
          </button>
        ))}
      </div>

      <div className="events-container card">
        <div className="events-header">
          <h3>{selectedTopic}</h3>
          <span className="event-count">
            {topicEvents.length} recent events
          </span>
        </div>

        {topicEvents.length === 0 ? (
          <div className="no-events">
            <p>No events yet for this topic.</p>
            {selectedTopic === 'db_public_users' ? (
              <p className="hint">Users are loaded automatically from Kafka on startup.</p>
            ) : (
              <p className="hint">Go to the Customer tab to generate events!</p>
            )}
          </div>
        ) : (
          <div className="events-list">
            {topicEvents.map((event, idx) => (
              <div key={idx} className="event-card">
                <div className="event-header">
                  <span className="event-time">
                    {selectedTopic === 'db_public_users'
                      ? formatEventTimestamp(event.timestamp)
                      : formatEventTimestamp(event.data.timestamp)}
                  </span>
                </div>
                {renderEventDetails(event)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default KafkaTab;
