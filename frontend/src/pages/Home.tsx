import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import OASCalculatorModal from '../components/OASCalculatorModal';

const Home: React.FC = () => {
  const [isOASModalOpen, setIsOASModalOpen] = useState(false);

  const openOASModal = () => setIsOASModalOpen(true);
  const closeOASModal = () => setIsOASModalOpen(false);

  return (
    <>
      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        paddingTop: '80px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '4rem',
            alignItems: 'center'
          }}>
            <div>
              <h1 style={{
                fontSize: '3.2rem',
                fontWeight: 800,
                marginBottom: '1.5rem',
                lineHeight: 1.2,
                color: '#1a202c'
              }}>
                <span style={{ color: '#e53e3e' }}>Stop Overpaying</span> on Retirement Taxes
              </h1>
              <p style={{
                fontSize: '1.3rem',
                marginBottom: '2.5rem',
                color: '#4a5568',
                lineHeight: 1.6
              }}>
                Discover How Much You Could Save with Ontario's Most Powerful RRSP Withdrawal Analyzer. Our app analyzes over 8 tax-saving strategies, including spousal equalization and RRIF meltdowns, to find the optimal plan for your specific financial situation. Stop guessing and start planning with confidence.
              </p>
              <Link
                to="/calculator"
                style={{
                  display: 'inline-block',
                  background: 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)',
                  color: 'white',
                  padding: '1.2rem 2.5rem',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  textDecoration: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 10px 25px rgba(229, 62, 62, 0.3)',
                  transition: 'all 0.3s ease'
                }}
              >
                Generate My Personalized Tax Analysis
              </Link>
              <p style={{
                marginTop: '1.5rem',
                fontSize: '1rem',
                color: '#4a5568'
              }}>
                Not ready for a full analysis? <Link to="/free-rrif-guide" style={{ color: '#2c5aa0', textDecoration: 'none', fontWeight: 600 }}>Download our free RRIF Guide first.</Link>
              </p>
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              position: 'relative'
            }}>
              <div style={{
                background: 'white',
                borderRadius: '12px',
                padding: '2rem',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
                transform: 'rotate(-2deg)',
                position: 'relative'
              }}>
                <h3 style={{ color: '#2c5aa0', marginBottom: '1rem' }}>📊 Professional Tax Report</h3>
                <div style={{
                  height: '200px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#4a5568'
                }}>
                  Comprehensive Analysis<br />
                  8+ Strategies Compared<br />
                  Ontario-Specific Calculations
                </div>
              </div>
              <div style={{
                position: 'absolute',
                right: '-50px',
                top: '50px',
                background: 'white',
                padding: '1.5rem',
                borderRadius: '8px',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
                transform: 'rotate(3deg)'
              }}>
                <h4 style={{ color: '#2c5aa0', marginBottom: '0.5rem' }}>Tax Savings</h4>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'end' }}>
                  <div style={{ background: '#e53e3e', height: '60px', width: '30px', borderRadius: '4px' }}></div>
                  <div style={{ background: '#38a169', height: '100px', width: '30px', borderRadius: '4px' }}></div>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#4a5568', marginTop: '0.5rem' }}>Unoptimized vs Optimized</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section id="problem" style={{ padding: '6rem 0', background: '#f7fafc' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h2 style={{
            fontSize: '2.8rem',
            fontWeight: 700,
            textAlign: 'center',
            marginBottom: '3rem',
            color: '#1a202c'
          }}>
            Retirement in Ontario is More Complicated Than Ever
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem',
            marginTop: '2rem'
          }}>
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              borderLeft: '4px solid #e53e3e'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>💰</div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '1rem', color: '#2d3748' }}>High Advisor Fees</h3>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Comprehensive retirement plans can cost over $1,500, locking valuable advice away from those who need it most.</p>
            </div>
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              borderLeft: '4px solid #e53e3e'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚠️</div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '1rem', color: '#2d3748' }}>The OAS Clawback</h3>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Are you unknowingly on track to lose thousands in government benefits? The clawback threshold is $93,454 for 2025, and many retirees cross it without a plan.</p>
            </div>
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              borderLeft: '4px solid #e53e3e'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>👫</div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '1rem', color: '#2d3748' }}>Complex Spousal Rules</h3>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Are you and your spouse truly minimizing your combined tax bill? Misunderstanding spousal RRSP and pension splitting rules can be a costly mistake.</p>
            </div>
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              borderLeft: '4px solid #e53e3e'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📊</div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '1rem', color: '#2d3748' }}>Generic Advice</h3>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Most online calculators ignore Ontario-specific surtaxes and health premiums, giving you an incomplete and dangerously inaccurate picture.</p>
            </div>
          </div>
          
          {/* OAS Clawback Calculator Callout */}
          <div style={{
            background: '#F0F7FF',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '2rem',
            marginTop: '3rem',
            textAlign: 'center'
          }}>
            <h2 style={{
              fontSize: '2rem',
              fontWeight: 700,
              color: '#1a202c',
              marginBottom: '1rem'
            }}>
              Find Your Personal Clawback Risk Zone
            </h2>
            <p style={{
              fontSize: '1.1rem',
              color: '#4a5568',
              marginBottom: '2rem',
              lineHeight: 1.6
            }}>
              Are your planned withdrawals putting your OAS at risk? Don't guess. Use our free, interactive calculator to see your estimated net income and find out if you're in the danger zone.
            </p>
            <button
              onClick={openOASModal}
              style={{
                background: 'linear-gradient(135deg, #2c5aa0 0%, #1a365d 100%)',
                color: 'white',
                padding: '1rem 2rem',
                fontSize: '1.1rem',
                fontWeight: 600,
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(44, 90, 160, 0.3)'
              }}
            >
              Launch Free OAS Calculator
            </button>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="solution" style={{ padding: '6rem 0', background: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h2 style={{
            fontSize: '2.8rem',
            fontWeight: 700,
            textAlign: 'center',
            marginBottom: '1.5rem',
            color: '#1a202c'
          }}>
            The Ontario Tax App: Your Financial Advisor in Your Pocket
          </h2>
          <p style={{
            textAlign: 'center',
            fontSize: '1.2rem',
            color: '#4a5568',
            marginBottom: '4rem',
            maxWidth: '600px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            Frame each feature as a direct benefit to you
          </p>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '3rem',
            marginTop: '3rem'
          }}>
            <div style={{
              background: '#f8fafc',
              padding: '2.5rem',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              transition: 'transform 0.3s ease'
            }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#2c5aa0', marginBottom: '0.5rem' }}>8+ Withdrawal Strategies Analyzed</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#2d3748', marginBottom: '1rem' }}>Complete Scenario Comparison</div>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>We compare every viable scenario—from Bracket Filling to a Gradual Meltdown—so you can see the exact tax and estate value implications of each choice. No more what-ifs.</p>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '2.5rem',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              transition: 'transform 0.3s ease'
            }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#2c5aa0', marginBottom: '0.5rem' }}>Spousal Equalization</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#2d3748', marginBottom: '1rem' }}>Household Tax Optimization</div>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Our proprietary algorithm finds the optimal withdrawal split between you and your spouse to minimize your household tax bill and protect your government benefits.</p>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '2.5rem',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              transition: 'transform 0.3s ease'
            }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#2c5aa0', marginBottom: '0.5rem' }}>Ontario-Specific Tax Engine</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#2d3748', marginBottom: '1rem' }}>True All-In Cost Analysis</div>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Our calculations include the Ontario Surtax and Health Premium, providing a true, all-in cost analysis that generic national tools miss.</p>
            </div>
            <div style={{
              background: '#f8fafc',
              padding: '2.5rem',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              transition: 'transform 0.3s ease'
            }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#2c5aa0', marginBottom: '0.5rem' }}>Professional PDF Report</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#2d3748', marginBottom: '1rem' }}>Confident Decision Making</div>
              <p style={{ color: '#4a5568', lineHeight: 1.6 }}>Receive a comprehensive, easy-to-understand report that you can save, print, and use to make confident decisions about your future.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Section */}
      <section style={{ 
        padding: '6rem 0', 
        background: 'linear-gradient(135deg, #2c5aa0 0%, #1a365d 100%)', 
        color: 'white' 
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h2 style={{
            fontSize: '2.8rem',
            fontWeight: 700,
            textAlign: 'center',
            marginBottom: '3rem'
          }}>
            An Investment in Your Financial Future
          </h2>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            overflow: 'hidden',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
            margin: '0 auto',
            maxWidth: '900px'
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{
                    background: '#2d3748',
                    color: 'white',
                    padding: '1.5rem 1rem',
                    fontWeight: 600,
                    textAlign: 'left'
                  }}>Feature</th>
                  <th style={{
                    background: '#f0fff4',
                    color: '#2d3748',
                    padding: '1.5rem 1rem',
                    fontWeight: 600,
                    textAlign: 'left'
                  }}>Ontario Tax App</th>
                  <th style={{
                    background: '#2d3748',
                    color: 'white',
                    padding: '1.5rem 1rem',
                    fontWeight: 600,
                    textAlign: 'left'
                  }}>Traditional Financial Advisor</th>
                  <th style={{
                    background: '#2d3748',
                    color: 'white',
                    padding: '1.5rem 1rem',
                    fontWeight: 600,
                    textAlign: 'left'
                  }}>Free Bank Calculators</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    fontWeight: 600
                  }}>Cost</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    background: '#f0fff4',
                    fontWeight: 600
                  }}>$149 One-Time</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748'
                  }}>$1,500+ Ongoing</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748'
                  }}>Free</td>
                </tr>
                <tr>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    fontWeight: 600
                  }}>Strategy Analysis</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    background: '#f0fff4',
                    fontWeight: 600
                  }}>8+ Scenarios Compared</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748'
                  }}>1-2 Scenarios</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748'
                  }}>1 Basic Projection</td>
                </tr>
                <tr>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    fontWeight: 600
                  }}>Spousal Optimization</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#38a169',
                    background: '#f0fff4',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✓ Yes</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#38a169',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✓ Yes</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#e53e3e',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✗ No</td>
                </tr>
                <tr>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#2d3748',
                    fontWeight: 600
                  }}>Ontario-Specific Taxes</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#38a169',
                    background: '#f0fff4',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✓ Yes</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#38a169',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✓ Yes</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    borderBottom: '1px solid #e2e8f0',
                    color: '#e53e3e',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>✗ No</td>
                </tr>
                <tr>
                  <td style={{
                    padding: '1.2rem 1rem',
                    color: '#2d3748',
                    fontWeight: 600
                  }}>Outcome</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    color: '#2d3748',
                    background: '#f0fff4',
                    fontWeight: 600
                  }}>Actionable, Optimized Plan</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    color: '#2d3748'
                  }}>Actionable Plan</td>
                  <td style={{
                    padding: '1.2rem 1rem',
                    color: '#2d3748'
                  }}>Vague Estimate</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" style={{ padding: '6rem 0', background: '#f7fafc' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h2 style={{
            fontSize: '2.8rem',
            fontWeight: 700,
            textAlign: 'center',
            marginBottom: '1rem',
            color: '#1a202c'
          }}>
            Clear Pricing & Final CTA
          </h2>
          <p style={{
            textAlign: 'center',
            fontSize: '1.2rem',
            color: '#4a5568',
            marginBottom: '4rem'
          }}>
            One-time payment. No recurring fees.
          </p>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '3rem',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
            textAlign: 'center',
            maxWidth: '500px',
            margin: '0 auto',
            border: '2px solid #2c5aa0'
          }}>
            <div style={{
              fontSize: '3rem',
              fontWeight: 800,
              color: '#2c5aa0',
              marginBottom: '0.5rem'
            }}>
              $149
            </div>
            <div style={{
              color: '#4a5568',
              marginBottom: '2rem',
              fontSize: '1.1rem'
            }}>
              Complete Tax Optimization Analysis
            </div>
            <ul style={{
              listStyle: 'none',
              marginBottom: '2.5rem',
              textAlign: 'left'
            }}>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                8+ Withdrawal Strategies Analyzed
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                Spousal Equalization Optimization
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                Ontario-Specific Tax Calculations
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                Professional PDF Report
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                OAS Clawback Protection Analysis
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                Estate Value Projections
              </li>
              <li style={{
                padding: '0.8rem 0',
                display: 'flex',
                alignItems: 'center',
                color: '#2d3748'
              }}>
                <span style={{
                  color: '#38a169',
                  fontWeight: 'bold',
                  marginRight: '1rem',
                  fontSize: '1.2rem'
                }}>✓</span>
                Lifetime Access to Your Report
              </li>
            </ul>
            <Link
              to="/calculator"
              style={{
                display: 'inline-block',
                background: 'linear-gradient(135deg, #38a169 0%, #2f855a 100%)',
                color: 'white',
                padding: '1.5rem 3rem',
                fontSize: '1.2rem',
                fontWeight: 600,
                textDecoration: 'none',
                borderRadius: '8px',
                boxShadow: '0 10px 25px rgba(56, 161, 105, 0.3)',
                transition: 'all 0.3s ease',
                width: '100%',
                textAlign: 'center'
              }}
            >
              Get Your Comprehensive Retirement Tax Report Now
            </Link>
          </div>
        </div>
      </section>

      {/* Pre-Footer Final Offer */}
      <section style={{ padding: '4rem 0', background: 'white', textAlign: 'center' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h2 style={{
            fontSize: '2.2rem',
            fontWeight: 700,
            color: '#1a202c',
            marginBottom: '1.5rem'
          }}>
            Still Exploring Your Options?
          </h2>
          <p style={{
            fontSize: '1.1rem',
            color: '#4a5568',
            marginBottom: '2rem',
            maxWidth: '700px',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: 1.6
          }}>
            We've condensed everything an Ontario retiree needs to know about the RRIF conversion process into one simple, easy-to-read guide. Download it for free and get the foundational knowledge you need to make a smart decision.
          </p>
          <Link
            to="/free-rrif-guide"
            style={{
              background: 'transparent',
              color: '#2c5aa0',
              padding: '1rem 2rem',
              fontSize: '1.1rem',
              fontWeight: 600,
              border: '2px solid #2c5aa0',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              textDecoration: 'none',
              display: 'inline-block'
            }}
          >
            Download The Free Guide
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ background: '#1a202c', color: 'white', padding: '3rem 0 1rem' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              borderTop: '1px solid #2d3748',
              paddingTop: '1rem',
              marginTop: '2rem',
              textAlign: 'center',
              color: '#a0aec0',
              fontSize: '0.9rem'
            }}>
              <p>&copy; 2025 Ontario Tax App. All rights reserved. Not affiliated with the Government of Ontario or Canada Revenue Agency.</p>
              <p style={{ marginTop: '0.5rem' }}>Secure calculations performed locally. Your financial data never leaves your device.</p>
            </div>
          </div>
        </div>
      </footer>

      {/* OAS Calculator Modal */}
      {isOASModalOpen && (
        <OASCalculatorModal open={isOASModalOpen} onClose={closeOASModal} />
      )}
    </>
  );
};

export default Home;
