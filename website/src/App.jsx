import './App.css'

function App() {
  return (
    <div className="app">
      <header className="hero">
        <nav className="nav">
          <div className="logo">Splice3D</div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#hardware">Hardware</a>
            <a href="#docs">Docs</a>
            <a href="https://github.com/dmhernandez2525/splice3d" target="_blank" rel="noopener noreferrer" className="github-link">GitHub</a>
          </div>
        </nav>
        <div className="hero-content">
          <h1>Multi-Color 3D Printing for Any Printer</h1>
          <p className="tagline">Pre-splice multi-color filament for any FDM printer. No tool changes. No modifications.</p>
          <div className="hero-buttons">
            <a href="https://github.com/dmhernandez2525/splice3d" className="btn btn-primary">Get Started</a>
            <a href="#how-it-works" className="btn btn-secondary">Learn More</a>
          </div>
        </div>
      </header>

      <section id="features" className="features">
        <h2>Why Splice3D?</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🎨</div>
            <h3>4000+ Color Changes</h3>
            <p>Handle complex multi-color prints like the Starry Night Vase with thousands of precise color transitions.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🖨️</div>
            <h3>Any Single-Extruder Printer</h3>
            <p>Works with any FDM printer. No modifications required. Just load the pre-spliced spool and print.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>No Real-Time Tool Changes</h3>
            <p>All splicing happens before the print. Zero interruptions during printing means faster, cleaner results.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💰</div>
            <h3>Affordable Build</h3>
            <p>Build your own Splice3D machine for $170-250 using common parts and donor Ender 3 components.</p>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="how-it-works">
        <h2>How It Works</h2>
        <div className="workflow">
          <div className="workflow-step">
            <div className="step-number">1</div>
            <h3>Slice with OrcaSlicer</h3>
            <p>Use virtual multi-extruder settings in OrcaSlicer to assign colors to your model.</p>
          </div>
          <div className="workflow-arrow">→</div>
          <div className="workflow-step">
            <div className="step-number">2</div>
            <h3>Post-Process G-code</h3>
            <p>Our post-processor extracts exact segment lengths and generates a splice recipe.</p>
          </div>
          <div className="workflow-arrow">→</div>
          <div className="workflow-step">
            <div className="step-number">3</div>
            <h3>Splice Filament</h3>
            <p>The Splice3D machine welds filament segments together in the precise order.</p>
          </div>
          <div className="workflow-arrow">→</div>
          <div className="workflow-step">
            <div className="step-number">4</div>
            <h3>Print!</h3>
            <p>Load the pre-spliced spool and print on any single-extruder printer.</p>
          </div>
        </div>
        <div className="code-block">
          <code>
            [OrcaSlicer] → [Post-Processor] → [Splice3D Machine] → [Pre-spliced Spool] → [Any Printer]
          </code>
        </div>
      </section>

      <section id="hardware" className="hardware">
        <h2>Hardware Requirements</h2>
        <div className="hardware-grid">
          <div className="hardware-item">
            <h3>Controller</h3>
            <p>BTT SKR Mini E3 v2.0 (STM32F103)</p>
          </div>
          <div className="hardware-item">
            <h3>Motors</h3>
            <p>3x NEMA17 (from Ender 3)</p>
          </div>
          <div className="hardware-item">
            <h3>Heater</h3>
            <p>Hotend assembly (weld chamber)</p>
          </div>
          <div className="hardware-item">
            <h3>Cutter</h3>
            <p>SG90 servo + blade</p>
          </div>
        </div>
        <p className="hardware-cost">Estimated build cost: <strong>$170-250</strong> (using donor Ender 3 parts)</p>
      </section>

      <section id="docs" className="docs">
        <h2>Documentation</h2>
        <div className="docs-grid">
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/WIRING.md" className="doc-card">
            <h3>Wiring Guide</h3>
            <p>SKR Mini E3 v2 connection guide</p>
          </a>
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/BOM.md" className="doc-card">
            <h3>Bill of Materials</h3>
            <p>Complete parts list with prices</p>
          </a>
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/MECHANICAL.md" className="doc-card">
            <h3>Build Guide</h3>
            <p>Step-by-step mechanical assembly</p>
          </a>
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/CALIBRATION.md" className="doc-card">
            <h3>Calibration</h3>
            <p>Tuning steps/mm and weld quality</p>
          </a>
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/ORCASLICER_SETUP.md" className="doc-card">
            <h3>OrcaSlicer Setup</h3>
            <p>Multi-extruder profile configuration</p>
          </a>
          <a href="https://github.com/dmhernandez2525/splice3d/blob/main/docs/ROADMAP.md" className="doc-card">
            <h3>Roadmap</h3>
            <p>Future development phases</p>
          </a>
        </div>
      </section>

      <section className="quick-start">
        <h2>Quick Start</h2>
        <div className="code-examples">
          <div className="code-example">
            <h3>Install Post-Processor</h3>
            <pre><code>pip install -e .</code></pre>
          </div>
          <div className="code-example">
            <h3>Process Multi-Color G-code</h3>
            <pre><code>python3 splice3d_postprocessor.py input.gcode --colors white black</code></pre>
          </div>
          <div className="code-example">
            <h3>Simulate Splice Cycle</h3>
            <pre><code>cd cli{'\n'}python3 simulator.py ../samples/test_multicolor_splice_recipe.json</code></pre>
          </div>
        </div>
      </section>

      <section className="status">
        <h2>Project Status</h2>
        <div className="status-grid">
          <div className="status-item complete">
            <span className="status-icon">✅</span>
            <span>Post-processor complete (30 tests passing)</span>
          </div>
          <div className="status-item complete">
            <span className="status-icon">✅</span>
            <span>Firmware architecture complete</span>
          </div>
          <div className="status-item complete">
            <span className="status-icon">✅</span>
            <span>CI/CD pipeline configured (Python 3.9-3.12)</span>
          </div>
          <div className="status-item complete">
            <span className="status-icon">✅</span>
            <span>Documentation complete (25+ guides)</span>
          </div>
          <div className="status-item pending">
            <span className="status-icon">🔧</span>
            <span>Hardware build pending</span>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Splice3D</h3>
            <p>Open source multi-color filament splicing for any FDM printer.</p>
          </div>
          <div className="footer-section">
            <h3>Links</h3>
            <a href="https://github.com/dmhernandez2525/splice3d">GitHub Repository</a>
            <a href="https://github.com/dmhernandez2525/splice3d/blob/main/LICENSE">MIT License</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>MIT License - Open Source</p>
        </div>
      </footer>
    </div>
  )
}

export default App
