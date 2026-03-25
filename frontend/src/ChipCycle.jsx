import React, { useState } from 'react';
import './index.css';

export default function ChipCycle() {

  const [activePage, setActivePage] = useState('home');
  const [isBulk, setIsBulk] = useState(true);

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [qty, setQty] = useState(2);

  const showPage = (name) => {
    if (!isLoggedIn && ["profile", "list-hardware", "cart", "checkout"].includes(name)) {
      setActivePage("login");
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    setActivePage(name);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const login = () => {
    setIsLoggedIn(true);
    setActivePage("home");
  };

  const logout = () => {
    setIsLoggedIn(false);
    setActivePage("home");
  };

  const changeQty = (delta) => {
    setQty(prev => Math.max(1, prev + delta));
  };

  const addToCart = () => {
    alert(`Added ${qty} item(s) to cart! 🛒`);
  };

  return (
    <>
      {/* HTML Ported Body */}
      
    {/*  ═══════════ NAV ═══════════  */}
    <nav id="main-nav">
      <div className="nav-logo" onClick={() => {showPage('home')}}>
        <div className="nav-logo-icon">
          <img src="img/chipcycle logo.png" alt="logo" />
        </div>
        <span className="nav-logo-text">ChipCycle</span>
      </div>
      <ul className="nav-links" id="nav-links">
        <li>
          <a onClick={() => {showPage('marketplace')}} className="nav-link-item"
            >Marketplace</a
          >
        </li>
        {isLoggedIn && (
        <li>
          <a
            onClick={() => {showPage('list-hardware')}}
            className="nav-link-item"
            id="nav-list-hardware"
            >List Your Hardware</a
          >
        </li>
        )}
        <li>
          <a onClick={() => {showPage('how-it-works')}} className="nav-link-item"
            >How It Works</a
          >
        </li>
        <li>
          <a onClick={() => {showPage('about')}} className="nav-link-item">About Us</a>
        </li>
      </ul>
      <div className="nav-right">
        {/*  Logged out state  */}
        <div id="nav-logged-out" style={{ display: isLoggedIn ? "none" : "flex" }}>
          <button className="btn-nav" onClick={() => {showPage('login')}}>
            LOGIN / SIGNUP
          </button>
        </div>
        {/*  Logged in state  */}
        <div id="nav-logged-in" style={{ display: isLoggedIn ? "flex" : "none" }}>
          <span className="cart-icon" onClick={() => {showPage('cart')}}
            >🛒<span className="cart-badge">1</span></span
          >
          <div className="nav-dropdown">
            <div className="nav-user-name">Welcome, Theodore</div>
            <div className="dropdown-menu">
              <a onClick={() => {showPage('profile')}}>Profile</a>
              <a onClick={() => {logout()}}>Log Out</a>
            </div>
          </div>
        </div>
      </div>
    </nav>

    {/*  ════════════════════════════════════════════════
     PAGE: HOME
════════════════════════════════════════════════  */}
    <div id="page-home" className={`page ${activePage === "home" ? "active" : ""}`}>
      {/*  HERO  */}
      <section className="hero">
        <div className="hero-left">
          <h1 className="hero-title">TURN UNUSED HARDWARE INTO VALUE</h1>
          <p className="hero-sub">
            AI-powered marketplace connecting companies with affordable,
            high-quality tech.
          </p>
          <div className="hero-btns">
            <button className="btn-primary" onClick={() => {showPage('marketplace')}}>
              Browse Marketplace
            </button>
            <button className="btn-primary" onClick={() => {showPage('list-hardware')}}>
              Sell Your Hardware
            </button>
          </div>
        </div>
        <div className="hero-right">
          <img
            src="img/Homepage-graphics.png"
            alt="homepage-side-icon"
            className="hero-image"
          />
        </div>
      </section>

      {/*  TRUSTED  */}
      <div className="trusted-banner">
        <h3>
          Trusted by <span className="highlight">resourceful</span> organizations
        </h3>
        <div className="trusted-logos">
          <img src="img/gnois-logo.png" alt="partner-1" />
          <img src="img/Alba_ewaste_logo.png" alt="partner-2" />
          <img src="img/SWM_Logo.png" alt="partner-3" />
        </div>
      </div>

      {/*  WHY CHOOSE US  */}
      <section >
        <h2 className="section-title">Why Choose Us</h2>
        <div className="why-cards">
          <div className="why-card">
            <div className="why-icon">✅</div>
            <h4>Verified Businesses Only</h4>
            <p>Every buyer and seller is vetted for trust and legitimacy.</p>
          </div>
          <div className="why-card">
            <div className="why-icon">🔒</div>
            <h4>Secure Transactions</h4>
            <p>$1M in hardware traded safely through our platform.</p>
          </div>
          <div className="why-card">
            <div className="why-icon">🏅</div>
            <h4>Quality Checked Listings</h4>
            <p>
              5,000+ devices reused — every listing is graded and inspected.
            </p>
          </div>
        </div>
      </section>

      {/*  HOW IT WORKS  */}
      <section >
        <h2 className="section-title">How It Works</h2>
        <div className="how-grid">
          <div className="how-card">
            <h4>For Sellers</h4>
            <div className="how-step">
              <div className="step-num">1</div>
              <span>List your hardware</span>
            </div>
            <div className="how-step">
              <div className="step-num">2</div>
              <span>Set your price</span>
            </div>
            <div className="how-step">
              <div className="step-num">3</div>
              <span>Connect with buyers</span>
            </div>
          </div>
          <div className="how-card">
            <h4>For Buyers</h4>
            <div className="how-step">
              <div className="step-num">1</div>
              <span>Browse listings</span>
            </div>
            <div className="how-step">
              <div className="step-num">2</div>
              <span>Compare options</span>
            </div>
            <div className="how-step">
              <div className="step-num">3</div>
              <span>Purchase or enquire</span>
            </div>
          </div>
        </div>
      </section>

      {/*  FEATURED PRODUCTS  */}
      <section >
        <h2 className="section-title">Featured Products</h2>
        <div className="products-grid featured-products-grid">
          <div className="product-card" onClick={() => {showPage('product-detail')}}>
            <div className="product-img">
              <img src="img/mb-air-13.png" alt="mb-air-13" />
            </div>
            <div className="product-info">
              <h4>Apple MacBook Air 13.3 inch Intel Core i5 1.8GHz 8GB</h4>
              <p className="product-price">SGD 898.94</p>
              <button className="btn-orange">Buy Now</button>
            </div>
          </div>
          <div className="product-card" onClick={() => {showPage('product-detail')}}>
            <div className="product-img">
              <img src="img/keyboard.png" alt="keyboard" />
            </div>
            <div className="product-info">
              <h4>Philips SPT6224 Black Keyboard and Mouse Set USB</h4>
              <p className="product-price">SGD 89.30</p>
              <button className="btn-orange">Buy Now</button>
            </div>
          </div>
          <div className="product-card" onClick={() => {showPage('product-detail')}}>
            <div className="product-img">
              <img src="img/iphone15promax.png" alt="iphone15promax" />
            </div>
            <div className="product-info">
              <h4>SApple iPhone 15 Pro Max, 256 GB</h4>
              <p className="product-price">SGD 6,119.00</p>
              <button className="btn-orange">Buy Now</button>
            </div>
          </div>
        </div>
        <div >
          <button className="btn-primary" onClick={() => {showPage('marketplace')}}>
            Browse Marketplace
          </button>
        </div>
      </section>

      {/*  OUR PROGRESS  */}
      <section className="progress-section">
        <div className="progress-image">
          <img src="img/our-progress.jpg" alt="our-progress" />
        </div>
        <div className="progress-content">
          <h2>Our Progress</h2>
          <p>
            Over the years, our team at ChipCycle have managed to achieve
            remarkable results in the field. And we are looking to do much more.
          </p>
          <div className="stats-grid">
            <div>
              <div className="stat-value">2,400 tons annually</div>
              <div className="stat-label">Of e-waste recycled</div>
            </div>
            <div>
              <div className="stat-value">Up to 95%</div>
              <div className="stat-label">E-waste recovery rates</div>
            </div>
            <div>
              <div className="stat-value">100+ SMEs / Startups</div>
              <div className="stat-label">Trading partners across Singapore</div>
            </div>
          </div>
        </div>
      </section>

      <hr className="divider" />
      {/*  FOOTER  */}
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: LOGIN
════════════════════════════════════════════════  */}
    <div id="page-login" className={`page ${activePage === "login" ? "active" : ""}`}>
      <div className="login-wrap">
        <div className="login-left"><img src="img/login.jpg" alt="login" /></div>
        <div className="login-right">
          <div className="login-box">
            <h2>Log In</h2>
            <p>Enter your details below</p>
            <div className="form-field">
              <label>Email or Phone Number</label>
              <input type="text" placeholder="theodore@example.com" />
            </div>
            <div className="form-field">
              <label>Password</label>
              <input type="password" placeholder="••••••••" />
            </div>
            <div className="login-actions">
              <button
                className="btn-orange"
                onClick={() => {login()}}
                
              >
                Log In
              </button>
              <span className="forgot-link">Forget Password?</span>
            </div>
            <p className="login-signup">
              Don't have an account?
              <span onClick={() => {showPage('home')}}>Sign Up</span>
            </p>
          </div>
        </div>
      </div>
      <footer >
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: PROFILE
════════════════════════════════════════════════  */}
    <div id="page-profile" className={`page ${activePage === "profile" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Account <span>/ My Profile</span></div>
      </div>
      <p className="profile-welcome" >
        Welcome! <strong>Theodore</strong>
      </p>
      <div className="profile-layout">
        <div className="profile-sidebar">
          <div className="profile-nav-section">
            <h4>Manage My Account</h4>
            <a className="profile-nav-link active">My Profile</a>
            <a className="profile-nav-link" >Address Book</a>
            <a className="profile-nav-link" 
              >My Payment Options</a
            >
          </div>
          <div className="profile-nav-section">
            <h4>My Orders</h4>
            <a className="profile-nav-link" >My Returns</a>
            <a className="profile-nav-link" 
              >My Cancellations</a
            >
          </div>
          <div className="profile-nav-section">
            <h4>My Listings</h4>
            <a className="profile-nav-link" >My Reviews</a>
          </div>
        </div>
        <div className="profile-content">
          <h3>Edit Your Profile</h3>
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label
              ><input type="text" placeholder="Theodore" />
            </div>
            <div className="form-group">
              <label>Last Name</label><input type="text" placeholder="Lim" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email</label
              ><input type="email" placeholder="theodore@chipcycle.sg" />
            </div>
            <div className="form-group">
              <label>Address</label
              ><input type="text" placeholder="123 Orchard Road, Singapore" />
            </div>
          </div>
          <div className="form-full">
            <div className="form-group">
              <label>Password Changes</label
              ><input type="password" placeholder="Current Password" />
            </div>
          </div>
          <div className="form-full">
            <div className="form-group">
              <input type="password" placeholder="New Password" />
            </div>
          </div>
          <div className="form-full">
            <div className="form-group">
              <input type="password" placeholder="Confirm New Password" />
            </div>
          </div>
          <div className="form-actions">
            <span className="btn-cancel" onClick={() => {showPage('home')}}>Cancel</span>
            <button
              className="btn-orange"
              
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: HOW IT WORKS
════════════════════════════════════════════════  */}
    <div id="page-how-it-works" className={`page ${activePage === "how-it-works" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Home <span>/ How It Works</span></div>
        <div className="page-title">How It Works</div>
      </div>
      <div className="how-section-box">
        <h2>Buyers</h2>
        <div className="how-steps-list">
          <div className="how-step-item">
            <div className="how-step-num">1</div>
            <div className="how-step-text">
              <h5>Browse the Marketplace</h5>
              <p>
                Explore thousands of verified, quality-checked tech listings
                from trusted businesses across Singapore.
              </p>
            </div>
          </div>
          <div className="how-step-item">
            <div className="how-step-num">2</div>
            <div className="how-step-text">
              <h5>Compare & Select</h5>
              <p>
                Use our AI-powered Fair Market Value engine to compare pricing,
                specs, and condition grades.
              </p>
            </div>
          </div>
          <div className="how-step-item">
            <div className="how-step-num">3</div>
            <div className="how-step-text">
              <h5>Purchase or Enquire</h5>
              <p>
                Add to cart and checkout securely, or send a bulk enquiry
                directly to the seller.
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="how-section-box">
        <h2>Sellers</h2>
        <div className="how-steps-list">
          <div className="how-step-item">
            <div className="how-step-num">1</div>
            <div className="how-step-text">
              <h5>List Your Hardware</h5>
              <p>
                Create a listing with photos, specs, quantity and pricing. Bulk
                and individual lots supported.
              </p>
            </div>
          </div>
          <div className="how-step-item">
            <div className="how-step-num">2</div>
            <div className="how-step-text">
              <h5>Set Your Price</h5>
              <p>
                Use our FMV engine for price recommendations or set your own
                price — you're in control.
              </p>
            </div>
          </div>
          <div className="how-step-item">
            <div className="how-step-num">3</div>
            <div className="how-step-text">
              <h5>Connect with Buyers</h5>
              <p>
                Receive offers, manage enquiries, and close deals with verified
                B2B buyers.
              </p>
            </div>
          </div>
        </div>
      </div>
      <footer >
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: ABOUT US
════════════════════════════════════════════════  */}
    <div id="page-about" className={`page ${activePage === "about" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Home <span>/ About Us</span></div>
        <div className="page-title">About Us</div>
      </div>
      <div className="about-banner banner-orange">
        <div className="about-banner-inner">
          <div className="about-text">
            <h2>Our Mission</h2>
            <p>
              We believe that technological progress shouldn't come at the cost
              of our planet, nor should high-quality tech be out of reach for
              growing businesses. Our mission is to dismantle the linear
              "take-make-dispose" model of corporate hardware by building a
              transparent, AI-driven circular economy. We bridge the gap between
              enterprise e-waste and SME empowerment, turning discarded assets
              into accessible opportunities.
            </p>
          </div>
          <div className="about-img">
            <img src="img/about-us-1.png" alt="about-us-1" />
          </div>
        </div>
      </div>
      <div className="about-cards banner-black">
        <div className="about-card">
          <div className="about-card-icon">🛡️</div>
          <h4>Product Support</h4>
          <p>
            Up to 3 years on-site warranty available for your peace of mind.
          </p>
        </div>
        <div className="about-card">
          <div className="about-card-icon">👤</div>
          <h4>Personal Account</h4>
          <p>
            With big discounts, free delivery and a dedicated support
            specialist.
          </p>
        </div>
        <div className="about-card">
          <div className="about-card-icon">💰</div>
          <h4>Amazing Savings</h4>
          <p>Up to 70% off new products — you can be sure of the best price.</p>
        </div>
      </div>
      <div className="about-banner banner-orange">
        <div className="about-banner-inner">
          <div className="about-img">
            <img src="img/about-us-2.png" alt="about-us-2" />
          </div>
          <div className="about-text">
            <h2>The Problem We're Solving</h2>
            <p>
              Every year, millions of tonnes of perfectly functional corporate
              hardware are sent to landfills simply because they have reached
              the end of their corporate depreciation cycle. Meanwhile, startups
              and SMEs struggle with the prohibitive costs of equipping their
              teams. The secondary market has historically been fragmented,
              intimidating, and lacking in enterprise-grade quality assurance.
              We are here to change that through data, transparency, and
              intelligent matching.
            </p>
          </div>
        </div>
      </div>
      <div >
        <div className="about-banner banner-black" >
          <div className="about-banner-inner">
            <div className="about-text">
              <h2>What Drives Us</h2>
              <p>
                <strong>Environmental Responsibility:</strong> Extending the
                life cycle of a single laptop by just two years reduces its
                carbon footprint by up to 40%.<br /><br /><strong
                  >SME Empowerment:</strong
                >
                We act as a "Virtual CTO," ensuring small business owners get
                exactly the hardware they need.<br /><br /><strong
                  >Market Transparency:</strong
                >
                Through our Fair Market Value (FMV) engine, we replace the
                information asymmetry of the refurbished market with hard data.
              </p>
            </div>
            <div className="about-img">
              <img src="img/about-us-3.png" alt="about-us-3" />
            </div>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: MARKETPLACE
════════════════════════════════════════════════  */}
    <div id="page-marketplace" className={`page ${activePage === "marketplace" ? "active" : ""}`}>
      <div >
        <div className="breadcrumb">Home <span>/ Marketplace</span></div>
      </div>
      {/*  Search  */}
      <div className="search-bar-unified">
        <input type="text" placeholder="Search" />
        <span className="search-icon-unified">🔍</span>
      </div>
      {/*  Hero Banner  */}
      <div className="marketplace-hero">
        <img src="img/marketplace-hero.png" alt="marketplace-hero" />
      </div>

      {/*  Categories  */}
      <div >
        <h2 className="section-title" >Categories</h2>
        {/*  Category circles  */}
        <div
          
        >
          <div
            
            onClick={() => {showPage('marketplace-cat')}}
          >
            <div
              
            >
              💻
            </div>
            <span 
              >Laptops</span
            >
          </div>
          <div
            
            onClick={() => {showPage('marketplace-cat')}}
          >
            <div
              
            >
              📱
            </div>
            <span 
              >Smartphones</span
            >
          </div>
          <div
            
            onClick={() => {showPage('marketplace-cat')}}
          >
            <div
              
            >
              ⌨️
            </div>
            <span 
              >Keyboards</span
            >
          </div>
          <div
            
            onClick={() => {showPage('marketplace-cat')}}
          >
            <div
              
            >
              🖱️
            </div>
            <span 
              >Mouses</span
            >
          </div>
          <div
            
            onClick={() => {showPage('marketplace-cat')}}
          >
            <div
              
            >
              🖥️
            </div>
            <span 
              >Desktops</span
            >
          </div>
        </div>
      </div>
      {/*  New Arrivals  */}
      <div >
        <h2 className="section-title" >New Arrivals</h2>
      </div>
      <div className="products-grid">
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/iphone15promax.png" alt="iphone15promax" /></div>
          <div className="mp-card-info">
            <h4>Apple iPhone 15 Pro Max, 256 GB, Unlocked</h4>
            <p className="mp-card-price">SGD 611.99</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/iphone16promax.png" alt="iphone16promax" /></div>
          <div className="mp-card-info">
            <h4>Apple iPhone 16 PRO MAX 256GB, Refurbished</h4>
            <p className="mp-card-price">SGD 999.99</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/macbookpro16.png" alt="macbookpro16" /></div>
          <div className="mp-card-info">
            <h4>Apple 2021 MacBook Pro M1 Max, 16", 32GB, 1TB</h4>
            <p className="mp-card-price">SGD 1,399.99</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/macbookpro13.png" alt="macbookpro13" /></div>
          <div className="mp-card-info">
            <h4>2022 Apple MacBook Pro 13.3" M2 8-Core 256GB SSD</h4>
            <p className="mp-card-price">SGD 575.00</p>
          </div>
        </div>
      </div>
      {/*  Popular Products  */}
      <div >
        <h2 className="section-title" >Popular Products</h2>
      </div>
      <div className="products-grid">
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img">
            <img src="img/mb-air-13.png" alt="mb-air-13" />
          </div>
          <div className="mp-card-info">
            <h4>Apple MacBook Air 13.3" Intel Core i5 1.8GHz 8GB</h4>
            <p className="mp-card-price">SGD 898.94</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/acer.png" alt="acer" /></div>
          <div className="mp-card-info">
            <h4>Acer Aspire 3 15.6" AMD A9 3GHz 4GB</h4>
            <p className="mp-card-price">SGD 400.00</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img">
            <div className="mp-card-img"><img src="img/hp.png" alt="hp" /></div>
          </div>
          <div className="mp-card-info">
            <h4>HP 250 G6 15.6" Intel Core i5 7200U 2.5GHz 8GB</h4>
            <p className="mp-card-price">SGD 575.00</p>
          </div>
        </div>
        <div className="mp-card" onClick={() => {showPage('product-detail')}}>
          <div className="mp-card-img"><img src="img/acer-desktop.png" alt="acer-desktop" /></div>
          <div className="mp-card-info">
            <h4>Acer Aspire Desktop Intel Core i5-14400 UHD 730</h4>
            <p className="mp-card-price">SGD 549.99</p>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: MARKETPLACE (CATEGORY / FILTER)
════════════════════════════════════════════════  */}
    <div id="page-marketplace-cat" className={`page ${activePage === "marketplace-cat" ? "active" : ""}`}>
      <div>
        <div className="breadcrumb">Home / Marketplace <span>/ Laptops</span></div>
      </div>
      <div className="search-bar-unified">
        <input type="text" placeholder="Search" />
        <span className="search-icon-unified">🔍</span>
      </div>
      {/*  Banner  */}
      <div className="marketplace-hero">
        <img src="img/marketplace-hero.png" alt="marketplace-hero" />
      </div>
      
      {/*  Filters + Grid  */}
      <div >
        <h2 className="section-title header-align">Laptops Products</h2>
      </div>
      <div className="marketplace-layout" >
        {/*  Sidebar Filter  */}
        <div>
          <div className="sidebar-filter" >
            <div className="filter-header">
              <span>Filters</span><span className="filter-clear">Clear Filter</span>
            </div>
            <div className="filter-section">
              <h5>Category</h5>
              <div className="filter-item">
                <span>Apple</span><span className="filter-count">45</span>
              </div>
              <div className="filter-item">
                <span>HP</span><span className="filter-count">30</span>
              </div>
              <div className="filter-item">
                <span>Acer</span><span className="filter-count">1</span>
              </div>
            </div>
            <div className="filter-section">
              <h5>Price</h5>
              <div className="filter-item">
                <span>$0 – $1,000</span><span className="filter-count">19</span>
              </div>
              <div className="filter-item">
                <span>$1,000 – $2,000</span><span className="filter-count">21</span>
              </div>
              <div className="filter-item">
                <span>$2,000 – $3,000</span><span className="filter-count">9</span>
              </div>
              <div className="filter-item">
                <span>$3,000+</span><span className="filter-count">6</span>
              </div>
            </div>
            <div className="filter-section">
              <h5>Colour</h5>
              <div >
                <div
                  
                ></div>
                <div
                  
                ></div>
                <div
                  
                ></div>
              </div>
            </div>
            <button
              className="btn-primary"
              
            >
              Apply Filters
            </button>
          </div>
          {/*  Compare / Wishlist  */}
          <div className="sidebar-filter">
            <div className="filter-header"><span>Compare Products</span></div>
            <p
              
            >
              You have no items to compare.
            </p>
          </div>
          <div className="sidebar-filter" >
            <div className="filter-header"><span>My Wish List</span></div>
            <p
              
            >
              You have no items in your wish list.
            </p>
          </div>
        </div>
        {/*  Products Grid  */}
        <div>
          <div className="products-main-header">
            <span
              
              >Items 10–19 of 61</span
            >
            <div >
              <span className="products-sort">Sort By: Newest | </span>
              <span className="products-sort">Show: 9 per page</span>
            </div>
          </div>
          <div className="marketplace-grid">
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img">
                <img src="img/mb-air-13.png" alt="mb-air-13" />
              </div>
              <div className="mp-card-info">
                <h4>Apple MacBook Air 13.3" Intel Core i5 1.8GHz 8GB</h4>
                <p className="mp-card-price">SGD 898.94</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img">
                <img src="img/acer.png" alt="acer" />
              </div>
              <div className="mp-card-info">
                <h4>Acer Aspire 3 15.6" AMD A9-Series 9420 3GHz 4GB</h4>
                <p className="mp-card-price">SGD 400.00</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img">
                <div className="mp-card-img"><img src="img/hp.png" alt="hp" /></div>
              </div>
              <div className="mp-card-info">
                <h4>HP 250 G6 15.6" Intel Core i5 7200U 2.5GHz 8GB</h4>
                <p className="mp-card-price">SGD 575.00</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/hp-15.png" alt="hp-15" /></div>
              <div className="mp-card-info">
                <h4> HP Pavilion 15.6" FHD Laptop (2022) AMD Ryzen 5 5500U 16GB 512GB</h4>
                <p className="mp-card-price">SGD 300.00</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/macbookpro16.png" alt="macbookpro16" /></div>
              <div className="mp-card-info">
                <h4>Apple 2021 MacBook Pro M1 Max 16" 32GB 1TB</h4>
                <p className="mp-card-price">SGD 1,399.99</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/macbookpro13.png" alt="macbookpro13" /></div>
              <div className="mp-card-info">
                <h4>2022 Apple MacBook Pro 13.3" M2 256GB Space Gray</h4>
                <p className="mp-card-price">SGD 575.00</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/dell-1-plus.png" alt="dell-1-plus" /></div>
              <div className="mp-card-info">
                <h4>Dell 1 Plus AMD Ryzen™ AI 7 350 16GB 1TB</h4>
                <p className="mp-card-price">SGD 723.76</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/msi.png" alt="msi" /></div>
              <div className="mp-card-info">
                <h4>MSI GL63 15.6 Gaming Laptop Intel Core i7 GTX 1050 8GB 1TB</h4>
                <p className="mp-card-price">SGD 929.00</p>
              </div>
            </div>
            <div className="mp-card" onClick={() => {showPage('product-detail')}}>
              <div className="mp-card-img"><img src="img/asus.png" alt="asus" /></div>
              <div className="mp-card-info">
                <h4>ASUS Zenbook S 14</h4>
                <p className="mp-card-price">SGD 699.99</p>
              </div>
            </div>
          </div>
          <div className="pagination">
            <div className="page-btn">‹</div>
            <div className="page-btn">1</div>
            <div className="page-btn active">2</div>
            <div className="page-btn">3</div>
            <div className="page-btn">...</div>
            <div className="page-btn">15</div>
            <div className="page-btn">›</div>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: PRODUCT DETAIL
════════════════════════════════════════════════  */}
    <div id="page-product-detail" className={`page ${activePage === "product-detail" ? "active" : ""}`}>
      <div className="page-header" style={{padding: "40px 8% 20px"}}>
        <div className="breadcrumb">
          Home / Marketplace <span>/ Apple MacBook Air</span>
        </div>
      </div>
      <div className="product-detail-layout">
        {/*  Thumbnails  */}
        <div className="product-thumbs">
          <div className="thumb active">
            <div className="mp-card-img">
              <img src="img/product-detail-2.png" alt="product-detail-2" />
            </div>
          </div>
          <div className="thumb">
            <div className="mp-card-img">
              <img src="img/product-detail-3.png" alt="product-detail-3" />
            </div>
          </div>
          <div className="thumb">
            <div className="mp-card-img">
              <img src="img/product-detail-4.png" alt="product-detail-4" />
            </div>
          </div>
        </div>
        {/*  Main Image  */}
        <div className="product-main-img">
          <img src="img/mb-air-13.png" alt="mb-air-13" />
        </div>
        {/*  Product Meta  */}
        <div className="product-meta">
          <h2>Apple MacBook Air 13.3 inch Intel Core i5 1.8GHz 8GB</h2>
          <div className="in-stock">In Stock</div>
          <div className="product-price-detail">SGD 898.94</div>
          <div className="divider-line"></div>
          <p className="product-specs">
            Intel Core i5 1.8GHz CPU, 8GB Ram, 128GB Flash Storage Memory, Intel
            HD Graphics 6000 GPU
          </p>
          <div className="divider-line"></div>
          <p className="color-label">Colours: <strong>Midnight</strong></p>
          <div className="color-swatches">
            <div className="swatch active" style={{backgroundColor: '#1e222b'}}></div>
            <div className="swatch" style={{backgroundColor: '#e2e3e5'}}></div>
            <div className="swatch" style={{backgroundColor: '#f0e4d3'}}></div>
          </div>
          <div className="qty-ctrl">
            <button className="qty-btn" onClick={() => {changeQty(-1)}}>−</button>
            <div className="qty-num" id="qty-num">{qty}</div>
            <button className="qty-btn" onClick={() => {changeQty(1)}}>+</button>
          </div>
          <div className="product-actions-row">
            <button
              className="btn-orange"
              onClick={() => {addToCart()}}
              
            >
              Add To Cart
            </button>
          </div>
          <div className="delivery-box">
            <div className="delivery-row">
              <div className="delivery-icon">🚚</div>
              <div className="delivery-text">
                <h5>Free Delivery</h5>
                <p>Enter your postal code for Delivery Availability</p>
              </div>
            </div>
            <div className="delivery-row">
              <div className="delivery-icon">ℹ️</div>
              <div className="delivery-text">
                <h5>Bulk Purchase</h5>
                <p>For bulk purchase, do enquire us!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/*  Related Items  */}
      <div className="related-section">
        <h3>Related Items</h3>
        <div className="related-grid">
          <div className="related-card" onClick={() => {showPage('product-detail')}}>
            <div className="related-card-img">
              <img src="img/keyboard.png" alt="keyboard" />
            </div>
            <div className="related-card-info">
              <h4>Philips SPT6224 Black Keyboard and Mouse Set USB</h4>
              <p className="price">SGD 89.30</p>
            </div>
          </div>
          <div className="related-card" onClick={() => {showPage('product-detail')}}>
            <div className="related-card-img">
              <img src="img/iphone15promax.png" alt="iphone15promax" />
            </div>
            <div className="related-card-info">
              <h4>Apple iPhone 15 Pro Max, 256 GB</h4>
              <p className="price">SGD 6,119.00</p>
            </div>
          </div>
          <div className="related-card" onClick={() => {showPage('product-detail')}}>
            <div className="related-card-img">
              <img src="img/acer.png" alt="acer" />
            </div>
            <div className="related-card-info">
              <h4>Acer Aspire 3 15.6" AMD A9-Series 9420 3GHz 4GB</h4>
              <p className="price">SGD 400.00</p>
            </div>
          </div>
          <div className="related-card" onClick={() => {showPage('product-detail')}}>
            <div className="related-card-img">
              <div className="mp-card-img"><img src="img/hp.png" alt="hp" /></div>
            </div>
            <div className="related-card-info">
              <h4>HP 250 G6 15.6" Intel Core i5 7200U 2.5GHz 8GB</h4>
              <p className="price">SGD 575.00</p>
            </div>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: CART
════════════════════════════════════════════════  */}
    <div id="page-cart" className={`page ${activePage === "cart" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Home <span>/ Cart</span></div>
      </div>
      <div className="cart-section">
        <div className="cart-table-header">
          <span>Product</span><span>Price</span><span>Quantity</span
          ><span>Subtotal</span>
        </div>
        <div className="cart-item">
          <div className="cart-item-product">
            <div className="cart-item-img">
              <img src="img/mb-air-13.png" alt="mb-air-13" />
            </div>
            <span>Apple MacBook Air 13.3"</span>
          </div>
          <span>SGD 898.94</span>
          <div className="cart-qty">
            <button className="cart-qty-btn">−</button
            ><span className="cart-qty-num">2</span
            ><button className="cart-qty-btn">+</button>
          </div>
          <span>SGD 1,797.88</span>
        </div>
        <div className="cart-bottom">
          <div className="cart-summary">
            <h3>Cart Total</h3>
            <div className="cart-row">
              <span>Subtotal:</span><span>SGD 1,797.88</span>
            </div>
            <div className="cart-row">
              <span>Shipping:</span><span >Free</span>
            </div>
            <div className="cart-row">
              <span>Total:</span><span>SGD 1,797.88</span>
            </div>
            <button
              className="btn-orange"
              
              onClick={() => {showPage('checkout')}}
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>
      <footer>
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: CHECKOUT
════════════════════════════════════════════════  */}
    <div id="page-checkout" className={`page ${activePage === "checkout" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Account / Cart / <span>CheckOut</span></div>
      </div>
      <div className="checkout-layout">
        <div className="checkout-left">
          <h2>Billing Details</h2>
          <div className="checkout-form-grid">
            <input
              className="checkout-input"
              type="text"
              placeholder="First Name*"
            />
            <input
              className="checkout-input"
              type="text"
              placeholder="Company Name"
            />
            <input
              className="checkout-input"
              type="text"
              placeholder="Street Address*"
            />
            <input
              className="checkout-input"
              type="text"
              placeholder="Apartment, floor, etc. (optional)"
            />
            <input
              className="checkout-input"
              type="text"
              placeholder="Town / City*"
            />
            <input
              className="checkout-input"
              type="tel"
              placeholder="Phone Number*"
            />
            <input
              className="checkout-input"
              type="email"
              placeholder="Email Address*"
            />
          </div>
          <div className="checkout-checkbox">
            <div className="checkbox-box">✓</div>
            <p>Save this information for faster check-out next time</p>
          </div>
        </div>
        <div className="checkout-right">
          <div className="order-product-row">
            <div className="order-product-img">
              <img src="img/mb-air-13.png" alt="mb-air-13" />
            </div>
            <div className="order-product-info">
              <h4>Apple MacBook Air 13" × 2</h4>
            </div>
            <div className="order-product-price">SGD 898.94</div>
          </div>
          <div className="order-summary-rows">
            <div className="order-row">
              <span>Subtotal:</span><span>SGD SGD 1,797.88</span>
            </div>
            <div className="order-row">
              <span>Shipping:</span><span >Free</span>
            </div>
            <div className="order-row">
              <span>Total:</span><span>SGD SGD 1,797.88</span>
            </div>
          </div>
          <div className="payment-options">
            <h4>Payment Method</h4>
            <div className="payment-row">
              <div className="radio-circle"></div>
              <span 
                >Bank</span
              >
              <div className="payment-icons">
                <span className="pay-icon">Visa</span
                ><span className="pay-icon">MC</span>
              </div>
            </div>
            <div className="payment-row">
              <div className="radio-circle selected"></div>
              <span 
                >Cash on delivery</span
              >
            </div>
          </div>
          <button
            className="btn-orange"
            
          >
            Place Order
          </button>
        </div>
      </div>
      <footer >
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     PAGE: LIST YOUR HARDWARE
════════════════════════════════════════════════  */}
    <div id="page-list-hardware" className={`page ${activePage === "list-hardware" ? "active" : ""}`}>
      <div className="page-header">
        <div className="breadcrumb">Home <span>/ List Your Hardware</span></div>
        <div className="page-title">List Your Hardware</div>
      </div>
      {/*  Company Info  */}
      <div className="list-section">
        <h3>Company Information</h3>
        <div className="list-form-row">
          <div>
            <label className="list-input-label">Company Name</label
            ><input className="list-input" type="text" placeholder="Company Name" />
          </div>
          <div>
            <label className="list-input-label">Business Registration Number</label
            ><input
              className="list-input"
              type="text"
              placeholder="Business Registration Number"
            />
          </div>
        </div>
        <div className="list-form-row">
          <div>
            <label className="list-input-label">Contact Details</label
            ><input
              className="list-input"
              type="text"
              placeholder="Contact Details"
            />
          </div>
          <div>
            <label className="list-input-label">Location</label
            ><input className="list-input" type="text" placeholder="Location" />
          </div>
        </div>
      </div>
      {/*  Listing Overview  */}
      <div className="list-section">
        <h3>Listing Overview</h3>
        <div >
          <div className="pill-switch-container">
  <span className="pill-switch-label">Lot Type:</span>
  <div className="pill-switch">
    <div className={`pill-option ${isBulk ? "active" : ""}`} onClick={() => setIsBulk(true)}>Bulk</div>
    <div className={`pill-option ${!isBulk ? "active" : ""}`} onClick={() => setIsBulk(false)}>Individual</div>
  </div>
  {isBulk && (
    <input type="number" className="list-input" style={{ width: "100px", padding: "8px 12px" }} min="1" defaultValue="1" placeholder="Qty" />
  )}
</div>
        </div>
        <div >
          <label className="list-input-label"
            >Listing Title (e.g. Bulk Used Laptops – Dell & HP – 500
            Units)</label
          ><input className="list-input" type="text" placeholder="Listing Title" />
        </div>
        <div className="list-form-row">
          <div>
            <label className="list-input-label">Category</label
            ><select className="list-input">
              <option>Select Category</option>
              <option>Laptops</option>
              <option>Desktops</option>
              <option>Smartphones</option>
              <option>Peripherals</option>
            </select>
          </div>
          <div>
            <label className="list-input-label">Condition</label
            ><select className="list-input">
              <option>Select Condition</option>
              <option>Grade A – Like New</option>
              <option>Grade B – Good</option>
              <option>Grade C – Fair</option>
            </select>
          </div>
        </div>
        <div className="list-form-row">
          <div>
            <label className="list-input-label">$ Price</label
            ><input
              className="list-input"
              type="number"
              placeholder="Price (SGD)"
            />
          </div>
          <div>
            <label className="list-input-label">Brand</label
            ><input className="list-input" type="text" placeholder="Brand" />
          </div>
        </div>
        <div >
          <label className="list-input-label">Age / Year</label
          ><input
            className="list-input"
            type="text"
            placeholder="Year of purchase"
          />
        </div>
        <div >
          <label className="list-input-label">Add Images</label>

          <div className="upload-box">
            <div className="upload-content">
              <span className="plus">+</span>
              <span className="text">Upload</span>
            </div>
          </div>
        </div>

        <div >
          <label className="list-input-label">Description</label>
          <textarea
            className="list-input"
            rows="4"
            placeholder="Describe your hardware listing..."
          ></textarea>
        </div>
      </div>
      {/*  Pickup/Shipping  */}
      <div className="list-section">
        <h3>Pickup / Shipping</h3>
        <div >
          <label className="list-input-label">Pickup Location (Full Address)</label
          ><input
            className="list-input"
            type="text"
            placeholder="Full pickup address"
          />
        </div>
        <div >
          <label className="list-input-label">Shipping Options</label
          ><select className="list-input">
            <option>Buyer arranges</option>
            <option>Seller arranges</option>
            <option>Both available</option>
          </select>
        </div>
      </div>
      <div >
        <button className="btn-primary" >
          Submit Listing
        </button>
      </div>
      <footer >
        <div className="footer-grid">
          <div className="footer-col footer-support">
            <h5>Support</h5>
            <p>Singapore, SG</p>
            <p>hello@chipcycle.sg</p>
            <p>+65 8888-9999</p>
            <div className="footer-socials">
              <span className="social-icon">f</span>
              <span className="social-icon">𝕏</span>
              <span className="social-icon">in</span>
              <span className="social-icon">📷</span>
            </div>
          </div>

          <div className="footer-col">
            <h5>Account</h5>
            <ul>
              <li><a onClick={() => {showPage('profile')}}>My Account</a></li>
              <li><a onClick={() => {showPage('cart')}}>Cart</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <h5>Quick Link</h5>
            <ul>
              <li><a onClick={() => {showPage('marketplace')}}>Marketplace</a></li>
              {isLoggedIn && ( <li><a onClick={() => {showPage('list-hardware')}}>Sell Hardware</a></li> )}
              <li><a onClick={() => {showPage('how-it-works')}}>How It Works</a></li>
              <li><a onClick={() => {showPage('about')}}>About Us</a></li>
            </ul>
          </div>

          <div className="footer-col">
            <ul>
              <li><a>Privacy Policy</a></li>
              <li><a>Terms of Use</a></li>
              <li><a>FAQ</a></li>
              <li><a>Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <span>©</span>
          <p>ChipCycle 2024. All rights reserved.</p>
        </div>
      </footer>
    </div>

    {/*  ════════════════════════════════════════════════
     JAVASCRIPT
════════════════════════════════════════════════  */}
    
  
    </>
  );
}
