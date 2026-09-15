import { useState, useEffect } from "react";
import "./App.css";
import AssistantPanel from "./AssistantPanel";

// Fallback data shown while loading or if backend is unreachable
const FALLBACK_SHIPMENTS = [
  {
    shipment_id: "SHIP-001",
    origin: "Mumbai",
    destination: "Rotterdam",
    cargo_type: "Vaccines ❄️",
    cold_chain: true,
    cargo_value: 520000,
    status: "In Transit",
    risk_level: "High",
  },
  {
    shipment_id: "SHIP-002",
    origin: "Chennai",
    destination: "Singapore",
    cargo_type: "Perishable Food ❄️",
    cold_chain: true,
    cargo_value: 180000,
    status: "Delayed",
    risk_level: "Critical",
  },
  {
    shipment_id: "SHIP-003",
    origin: "Delhi",
    destination: "Dubai",
    cargo_type: "Electronics",
    cold_chain: false,
    cargo_value: 250000,
    status: "In Transit",
    risk_level: "Medium",
  },
];

const FALLBACK_DISRUPTIONS = [
  {
    disruption_id: "DISR-001",
    type: "Port Strike",
    location: "Rotterdam",
    severity: "High",
    status: "Active",
    expected_duration_hours: 48,
    description: "Labour strike affecting container handling and port operations.",
  },
];

const FALLBACK_FLEET = [
  {
    asset_id: "TRUCK-017",
    asset_type: "Refrigerated Truck",
    location: "Rotterdam",
    available: true,
    utilisation_percent: 35,
  },
  {
    asset_id: "TRUCK-021",
    asset_type: "Standard Truck",
    location: "Mumbai",
    available: false,
    utilisation_percent: 80,
  },
  {
    asset_id: "TRUCK-034",
    asset_type: "Refrigerated Truck",
    location: "Dubai",
    available: false,
    utilisation_percent: 95,
  },
  {
    asset_id: "TRUCK-042",
    asset_type: "Standard Truck",
    location: "Delhi",
    available: true,
    utilisation_percent: 25,
  },
];

function riskClass(level) {
  return (level || "").toLowerCase();
}

function formatCargo(s) {
  const label = s.cargo_type || "";
  return s.cold_chain && !label.includes("❄") ? `${label} ❄️` : label;
}

function SimulationResult({ data }) {
  if (!data) return null;
  return (
    <section className="simulation">
      <div>
        <span>Projected Duration</span>
        <strong>{data.projected_total_duration_hours}h</strong>
      </div>
      <div>
        <span>Shipments Impacted</span>
        <strong>{data.impacted_shipment_count}</strong>
      </div>
      <div>
        <span>Cold-Chain Shipments</span>
        <strong>{data.cold_chain_shipment_count}</strong>
      </div>
      <div>
        <span>Cargo Value at Risk</span>
        <strong>${(data.total_cargo_value_at_risk || 0).toLocaleString()}</strong>
      </div>
      <div>
        <span>Projected Risk</span>
        <strong className={riskClass(data.projected_risk)}>
          {(data.projected_risk || "").toUpperCase()}
        </strong>
      </div>
      <p className="recommendation">{data.recommendation}</p>
    </section>
  );
}

function App() {
  const [shipments, setShipments] = useState(FALLBACK_SHIPMENTS);
  const [disruptions, setDisruptions] = useState(FALLBACK_DISRUPTIONS);
  const [fleet, setFleet] = useState(FALLBACK_FLEET);
  const [simulation, setSimulation] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  // Fetch live data from backend on mount
  useEffect(() => {
    fetch("/shipments")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => { if (data) setShipments(data); })
      .catch(() => {/* keep fallback */});

    fetch("/disruptions")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => { if (data) setDisruptions(data); })
      .catch(() => {/* keep fallback */});

    fetch("/fleet")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => { if (data) setFleet(data); })
      .catch(() => {/* keep fallback */});
  }, []);

  // Derived KPI values from live data
  const activeDisruptions = disruptions.filter((d) => d.status === "Active").length;
  const shipmentsAtRisk = shipments.filter((s) =>
    s.risk_level === "Critical" || s.risk_level === "High"
  ).length;
  const coldChainCount = shipments.filter((s) => s.cold_chain).length;
  const availableFleet = fleet.filter((a) => a.available).length;

  async function runSimulation() {
    setSimLoading(true);
    try {
      const res = await fetch("/simulate-disruption/DISR-001?additional_hours=48");
      if (res.ok) {
        const data = await res.json();
        setSimulation(data);
      }
    } catch {
      // If backend is down, show a static fallback result
      setSimulation({
        projected_total_duration_hours: 96,
        impacted_shipment_count: 2,
        cold_chain_shipment_count: 2,
        total_cargo_value_at_risk: 700000,
        projected_risk: "Critical",
        recommendation:
          "Prioritise cold-chain shipments and allocate refrigerated fleet capacity immediately.",
      });
    } finally {
      setSimLoading(false);
    }
  }

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
            <strong>{activeDisruptions}</strong>
          </div>

          <div className="metric-card">
            <span>Shipments at Risk</span>
            <strong>{shipmentsAtRisk}</strong>
          </div>

          <div className="metric-card">
            <span>Cold-Chain Shipments</span>
            <strong>{coldChainCount}</strong>
          </div>

          <div className="metric-card">
            <span>Available Fleet</span>
            <strong>{availableFleet}</strong>
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <div className="panel-header">
              <h2>Active Disruptions</h2>
              <span className="badge danger">LIVE</span>
            </div>

            {disruptions.map((d) => (
              <div className="disruption" key={d.disruption_id}>
                <div>
                  <strong>{d.type}</strong>
                  <p>{d.location}</p>
                </div>
                <div className="right">
                  <span className={`badge ${d.severity === "High" || d.severity === "Critical" ? "danger" : "warning"}`}>
                    {d.severity.toUpperCase()}
                  </span>
                  <small>{d.expected_duration_hours}h expected</small>
                </div>
              </div>
            ))}
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Fleet Availability</h2>
              <span className="badge success">OPTIMIZABLE</span>
            </div>

            {fleet.map((asset) => (
              <div className="fleet-row" key={asset.asset_id}>
                <div>
                  <strong>{asset.asset_id}</strong>
                  <p>
                    {asset.asset_type} · {asset.location}
                  </p>
                </div>

                <div className="right">
                  <span
                    className={`badge ${
                      asset.available ? "success" : "muted"
                    }`}
                  >
                    {asset.available ? "AVAILABLE" : "BUSY"}
                  </span>
                  <small>{asset.utilisation_percent}% utilised</small>
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

            {shipments.map((s) => (
              <div className="table-row" key={s.shipment_id}>
                <strong>{s.shipment_id}</strong>
                <span>{s.origin} → {s.destination}</span>
                <span>{formatCargo(s)}</span>
                <span>${s.cargo_value.toLocaleString()}</span>
                <span className={`risk ${riskClass(s.risk_level)}`}>
                  {s.risk_level}
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

          <button onClick={runSimulation} disabled={simLoading}>
            {simLoading ? "Running…" : "Run Simulation"}
          </button>
        </section>

        <SimulationResult data={simulation} />

        <AssistantPanel />
      </main>
    </div>
  );
}

export default App;
