import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DashboardTab.css';

function DashboardTab({ user, aiPredictions }) {
  const [events, setEvents] = useState({});
  const [metrics, setMetrics] = useState({
    viewsCount: 0,
    cartAdds: 0,
    cartAbandonments: 0,
    storeVisits: 0,
    partnerBrowses: 0,
    totalCartValue: 0,
    conversionRate: 0
  });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch events only (AI predictions are fetched in App.js)
      const eventsResponse = await axios.get('/api/events/latest');
      setEvents(eventsResponse.data);
      calculateMetrics(eventsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const calculateMetrics = (eventData) => {
    const viewsCount = eventData.RETAIL_DEMO_VIEW_PRODUCT?.length || 0;
    const cartAdds = eventData.RETAIL_DEMO_ADD_TO_CART?.length || 0;
    const cartAbandonments = eventData.RETAIL_DEMO_ABANDON_CART?.length || 0;
    const storeVisits = eventData.RETAIL_DEMO_STORE_ENTRY?.length || 0;
    const partnerBrowses = eventData.RETAIL_DEMO_PARTNER_BROWSE?.length || 0;

    const totalCartValue = eventData.RETAIL_DEMO_ABANDON_CART?.reduce((sum, event) => {
      return sum + (event.data?.cart_value || 0);
    }, 0) || 0;

    const conversionRate = viewsCount > 0 ? ((cartAdds / viewsCount) * 100).toFixed(1) : 0;

    setMetrics({
      viewsCount,
      cartAdds,
      cartAbandonments,
      storeVisits,
      partnerBrowses,
      totalCartValue,
      conversionRate
    });
  };

  const getAIRecommendations = () => {
    const recommendations = [];

    // AI-Generated Cart Recovery Messages (from Flink SQL)
    if (aiPredictions.cart_recovery && aiPredictions.cart_recovery.length > 0) {
      aiPredictions.cart_recovery.slice(0, 3).forEach(pred => {
        const data = pred.data;

        // Extract nudge_message - handle AVRO union format {"string": "..."}
        let nudgeMessage = 'Processing AI response...';
        const possibleFields = [data.nudge_message, data.ai_nudge_message, data.ai_recovery_message];
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

        recommendations.push({
          type: '💰 AI Cart Recovery',
          severity: 'high',
          message: <>AI-Generated for <strong>{data.username}</strong>: Cart value <strong>${data.cart_value?.toFixed(2) || 'N/A'}</strong></>,
          action: nudgeMessage,
          uplift: '32% conversion increase expected (AI-powered)',
          isAiGenerated: true,
          timestamp: pred.timestamp
        });
      });
    } else if (metrics.cartAbandonments > 0) {
      // Fallback to static message if no AI predictions yet
      recommendations.push({
        type: 'Cart Abandonment (Awaiting AI)',
        severity: 'high',
        message: `${metrics.cartAbandonments} cart(s) abandoned with total value $${metrics.totalCartValue.toFixed(2)}`,
        action: '⏳ Waiting for Flink SQL AI model to generate personalized nudge... (Create RETAIL_DEMO_CART_RECOVERY_MESSAGES table in Flink)',
        uplift: '32% conversion increase expected',
        isAiGenerated: false
      });
    }

    // AI-Generated Store Context (from Flink SQL)
    if (aiPredictions.store_context && aiPredictions.store_context.length > 0) {
      aiPredictions.store_context.slice(0, 2).forEach(pred => {
        const data = pred.data;

        // Extract welcome_message - handle AVRO union format {"string": "..."}
        let welcomeMessage = 'AI-generated welcome message';
        if (data.welcome_message) {
          if (typeof data.welcome_message === 'string') {
            welcomeMessage = data.welcome_message;
          } else if (data.welcome_message.string) {
            welcomeMessage = data.welcome_message.string;
          }
        }

        recommendations.push({
          type: '🏪 AI In-Store Context',
          severity: 'medium',
          message: <><strong>{data.username}</strong> entered <strong>{data.store_name || 'store'}</strong></>,
          action: welcomeMessage,
          uplift: 'Enhanced in-store experience with online context',
          isAiGenerated: true,
          timestamp: pred.timestamp
        });
      });
    } else if (metrics.storeVisits > 0) {
      recommendations.push({
        type: 'In-Store Personalization (Awaiting AI)',
        severity: 'medium',
        message: `${metrics.storeVisits} store visit(s) detected`,
        action: '⏳ Create RETAIL_DEMO_STORE_VISIT_CONTEXT table in Flink for enriched insights',
        uplift: 'Enhanced customer experience and assisted selling',
        isAiGenerated: false
      });
    }

    // AI-Generated Partner Retail Media (Act 4)
    if (aiPredictions.partner_ads && aiPredictions.partner_ads.length > 0) {
      aiPredictions.partner_ads.slice(0, 2).forEach(pred => {
        const data = pred.data;

        // Extract ad_copy - handle AVRO union format {"string": "..."}
        let adCopy = 'AI-generated ad copy available';
        if (data.ad_copy) {
          if (typeof data.ad_copy === 'string') {
            adCopy = data.ad_copy;
          } else if (data.ad_copy.string) {
            adCopy = data.ad_copy.string;
          }
        }

        recommendations.push({
          type: '📢 AI Partner Retail Media',
          severity: 'medium',
          message: <><strong>{data.username}</strong> browsing <strong>{data.category}</strong> on <strong>{data.partner_name}</strong></>,
          action: adCopy,
          uplift: '2x sales uplift from AI-powered personalized ads',
          isAiGenerated: true,
          timestamp: pred.timestamp
        });
      });
    } else if (metrics.partnerBrowses > 0) {
      recommendations.push({
        type: 'Retail Media (Awaiting AI)',
        severity: 'medium',
        message: `${metrics.partnerBrowses} partner browse(s) detected`,
        action: '⏳ Create RETAIL_DEMO_PARTNER_BROWSE_ADS table in Flink for AI-generated ad copy',
        uplift: '2x sales uplift from localized ads',
        isAiGenerated: false
      });
    }

    // Browse Intent
    if (metrics.viewsCount > 5 && metrics.cartAdds === 0) {
      recommendations.push({
        type: 'Browse Intent',
        severity: 'low',
        message: 'High browse activity but no cart adds',
        action: 'Offer limited-time discount or free shipping incentive',
        uplift: 'Increase purchase intent',
        isAiGenerated: false
      });
    }

    // Sort by timestamp (newest first) - AI-generated recommendations have timestamps
    recommendations.sort((a, b) => {
      const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
      const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
      return timeB - timeA; // Descending order (newest first)
    });

    return recommendations;
  };

  const recommendations = getAIRecommendations();

  return (
    <div className="dashboard-container">
      <div className="dashboard-header card">
        <h2>📈 Act 5: Real-Time AI Decisions & Analytics</h2>
        <p>Live insights powered by Confluent Cloud data streaming and AI</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card card">
          <div className="metric-icon">👁️</div>
          <div className="metric-value">{metrics.viewsCount}</div>
          <div className="metric-label">Product Views</div>
        </div>

        <div className="metric-card card">
          <div className="metric-icon">🛒</div>
          <div className="metric-value">{metrics.cartAdds}</div>
          <div className="metric-label">Cart Additions</div>
        </div>

        <div className="metric-card card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-value">{metrics.cartAbandonments}</div>
          <div className="metric-label">Cart Abandonments</div>
        </div>

        <div className="metric-card card">
          <div className="metric-icon">🏪</div>
          <div className="metric-value">{metrics.storeVisits}</div>
          <div className="metric-label">Store Visits</div>
        </div>

        <div className="metric-card card">
          <div className="metric-icon">🤝</div>
          <div className="metric-value">{metrics.partnerBrowses}</div>
          <div className="metric-label">Partner Browses</div>
        </div>

        <div className="metric-card card highlight tooltip-container">
          <div className="metric-icon">📊</div>
          <div className="metric-value">{metrics.conversionRate}%</div>
          <div className="metric-label">Conversion Rate</div>
          <div className="tooltip">
            Calculated as:<br/>(Cart Additions / Product Views) * 100%
          </div>
        </div>
      </div>

      <div className="ai-recommendations card">
        <h3>🤖 Real-Time AI Decisions</h3>
        <p className="section-description">
          AI-powered actions triggered by streaming events
        </p>

        {recommendations.length === 0 ? (
          <div className="no-recommendations">
            <p>No AI recommendations yet.</p>
            <p className="hint">Generate events in the Customer tab to see AI decisions!</p>
          </div>
        ) : (
          <div className="recommendations-list">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`recommendation-card severity-${rec.severity} ${rec.isAiGenerated ? 'ai-generated' : ''}`}
              >
                <div className="rec-header">
                  <span className="rec-type">{rec.type}</span>
                  <div className="rec-badges">
                    {rec.isAiGenerated && (
                      <span className="rec-badge ai-badge">
                        🤖 LIVE AI
                      </span>
                    )}
                    <span className={`rec-badge ${rec.severity}`}>
                      {rec.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="rec-message">{rec.message}</div>
                <div className="rec-action">
                  <strong>{rec.isAiGenerated ? 'AI Response:' : 'Action:'}</strong> {rec.action}
                </div>
                <div className="rec-uplift">
                  <strong>Expected Impact:</strong> {rec.uplift}
                </div>
                {rec.timestamp && (
                  <div className="rec-timestamp">
                    Generated: {new Date(rec.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="journey-insights card">
        <h3>🎯 Customer Journey Insights</h3>
        <div className="insights-grid">
          <div className="insight-box">
            <h4>Localized Ads (Act 1)</h4>
            <p>Real-time geo + inventory + customer context</p>
            <div className="insight-metric">2x sales uplift</div>
          </div>

          <div className="insight-box">
            <h4>Mid-Journey Nudges (Act 2)</h4>
            <p>Event-driven promotional triggers</p>
            <div className="insight-metric">32% conversion increase</div>
          </div>

          <div className="insight-box">
            <h4>In-Store Experience (Act 3)</h4>
            <p>Online + offline unified customer view</p>
            <div className="insight-metric">Seamless experience</div>
          </div>

          <div className="insight-box">
            <h4>Retail Media (Act 4)</h4>
            <p>Personalized partner placements</p>
            <div className="insight-metric">33% YoY basket growth</div>
          </div>
        </div>
      </div>

      <div className="platform-value card">
        <h3>💡 Platform Value Proposition</h3>
        <div className="value-points">
          <div className="value-point">
            <div className="value-icon">⚡</div>
            <div className="value-content">
              <strong>Real-Time Decision Making</strong>
              <p>React to customer behavior in milliseconds, not hours</p>
            </div>
          </div>
          <div className="value-point">
            <div className="value-icon">🔄</div>
            <div className="value-content">
              <strong>Unified Data Backbone</strong>
              <p>One platform for AI in the moment and insights afterwards</p>
            </div>
          </div>
          <div className="value-point">
            <div className="value-icon">🎯</div>
            <div className="value-content">
              <strong>Reusable Data Products</strong>
              <p>Build once, reuse for fraud, pricing, new journeys</p>
            </div>
          </div>
          <div className="value-point">
            <div className="value-icon">🌐</div>
            <div className="value-content">
              <strong>Omnichannel Intelligence</strong>
              <p>Seamless experience across web, app, store, and partners</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardTab;
