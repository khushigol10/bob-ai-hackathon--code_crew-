import { useState } from "react";
import "./App.css";
import AssistantPanel from "./AssistantPanel";

function App() {
  const [simulation, setSimulation] = useState(false);

  const shipments = [
    {
      id: "SHIP-001",
      route: "Mumbai → Rotterdam",
      cargo: "Vaccines ❄️",
      value: 520000,
      risk: "High",
    },
    {
      id: "SHIP-002",
      route: "Chennai → Singapore",
      cargo: "Perishable Food ❄️",
      value: 180000,
      risk: "Critical",
    },
    {
      id: "SHIP-003",
      route: "Delhi → Dubai",
      cargo: "Electronics",
      value: 250000,
      risk: "Medium",
    },
  ];

  const fleet = [
    {
      id: "TRUCK-017",
      type: "Refrigerated Truck",
      location: "Rotterdam",
      status: "AVAILABLE",
      utilisation: 35,
    },
    {
      id: "TRUCK-021",
      type: "Standard Truck",
      location: "Mumbai",
      status: "AVAILABLE",
      utilisation: 80,
    },
    {
      id: "TRUCK-034",
      type: "Refrigerated Truck",
      location: "Dubai",
      status: "UNAVAILABLE",
      utilisation: 95,
    },
    {
      id: "TRUCK-042",
      type: "Standard Truck",
      location: "Delhi",
      status: "AVAILABLE",
      utilisation: 25,
    },
  ];

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">L2 SUPPLY CHAIN INTELLIGENCE</p>
          <h1>Supply Chain Control Tower</h1>
          <p className="subtitle">
            Disruption monitoring, cold-chain risk and fleet optimisation
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          SYSTEM OPERATIONAL
        </div>
      </header>

      <main>
        <section className="metrics">
          <div className="metric-card">
            <span>Active Disruptions</span>
            <strong>1</strong>
          </div>

          <div className="metric-card">
            <span>Shipments at Risk</span>
            <strong>2</strong>
          </div>

          <div className="metric-card">
            <span>Cold-Chain Shipments</span>
            <strong>2</strong>
          </div>

          <div className="metric-card">
            <span>Available Fleet</span>
            <strong>3</strong>
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <div className="panel-header">
              <h2>Active Disruptions</h2>
              <span className="badge danger">LIVE</span>
            </div>

            <div className="disruption">
              <div>
                <strong>Port Strike</strong>
                <p>Rotterdam Port</p>
              </div>

              <div className="right">
                <span className="badge danger">CRITICAL</span>
                <small>48h expected</small>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Fleet Availability</h2>
              <span className="badge success">OPTIMIZABLE</span>
            </div>

            {fleet.map((asset) => (
              <div className="fleet-row" key={asset.id}>
                <div>
                  <strong>{asset.id}</strong>
                  <p>
                    {asset.type} · {asset.location}
                  </p>
                </div>

                <div className="right">
                  <span
                    className={`badge ${
                      asset.status === "AVAILABLE"
                        ? "success"
                        : "muted"
                    }`}
                  >
                    {asset.status}
                  </span>

                  <small>{asset.utilisation}% utilised</small>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Shipment Risk Monitor</h2>
            <span className="badge warning">MONITORING</span>
          </div>

          <div className="table">
            <div className="table-row table-head">
              <span>Shipment</span>
              <span>Route</span>
              <span>Cargo</span>
              <span>Value</span>
              <span>Risk</span>
            </div>

            {shipments.map((shipment) => (
              <div className="table-row" key={shipment.id}>
                <strong>{shipment.id}</strong>
                <span>{shipment.route}</span>
                <span>{shipment.cargo}</span>
                <span>${shipment.value.toLocaleString()}</span>
                <span className={`risk ${shipment.risk.toLowerCase()}`}>
                  {shipment.risk}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="action-panel">
          <div>
            <p className="eyebrow">WHAT-IF SIMULATION</p>

            <h2>
              What if the Rotterdam strike lasts another 48 hours?
            </h2>

            <p>
              Simulate the disruption and identify cargo value and
              cold-chain exposure.
            </p>
          </div>

          <button onClick={() => setSimulation(true)}>
            Run Simulation
          </button>
        </section>

        {simulation && (
          <section className="simulation">
            <div>
              <span>Projected Duration</span>
              <strong>96 hours</strong>
            </div>

            <div>
              <span>Shipments Impacted</span>
              <strong>1</strong>
            </div>

            <div>
              <span>Cold-Chain Shipments</span>
              <strong>1</strong>
            </div>

            <div>
              <span>Cargo Value at Risk</span>
              <strong>$520,000</strong>
            </div>

            <div>
              <span>Projected Risk</span>
              <strong className="critical">CRITICAL</strong>
            </div>

            <p className="recommendation">
              Prioritise cold-chain shipments and allocate refrigerated
              fleet capacity immediately.
            </p>
          </section>
        )}
        <AssistantPanel />
      </main>
    </div>
  );
}

export default App;