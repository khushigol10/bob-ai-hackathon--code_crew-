# Problem Statement

## Background

Global freight logistics depends on dozens of ports, carriers, and haulage operators working in tight coordination.
When something goes wrong — a port strike, a severe weather event, a vessel delay — the ripple effects move faster than any operations team can manually track.
Supply chain control towers exist precisely to give operations teams a single pane of glass, but most are passive dashboards that display what has already happened rather than helping teams understand what is about to happen and what to do about it.

## The Problem

When a disruptive event occurs (a port strike, severe weather, political instability), supply chain operations teams must manually:

1. Identify which shipments pass through the affected location.
2. Determine which of those shipments carry time-sensitive or temperature-sensitive cargo (cold chain).
3. Calculate the cargo value at risk.
4. Identify which fleet assets are available and suitable for reallocation.
5. Decide on a course of action — all within a narrow window before SLA breaches or cold-chain spoilage occurs.

This process is currently fragmented across shipment management systems, fleet management tools, cold-chain monitoring dashboards, and email threads.
A single disruption incident can consume 30–60 minutes of an operations manager's time before any remedial action is taken.

## Who is Affected

**Supply chain operations managers and logistics coordinators** at freight forwarders, pharmaceutical distributors, and food logistics companies — specifically those responsible for time-critical and cold-chain shipments.

Cold-chain cargo (vaccines, perishable food) is the highest-stakes category: temperature excursions caused by delayed decisions can result in cargo spoilage, patient safety incidents, and losses running into hundreds of thousands of dollars per shipment.

## Why It Matters

- **Financial risk:** A single delayed pharmaceutical cold-chain shipment can represent $500,000+ in cargo value, plus SLA penalties and re-supply costs.
- **Safety risk:** Vaccine shipments outside the 2–8 °C safe range become unusable; spoiled perishable food reaches end consumers.
- **Time pressure:** Port strikes and severe weather events evolve by the hour — a 24-hour delay in decision-making can escalate a "High" risk situation to "Critical".
- **Operational burden:** Operations teams currently have no way to instantly answer "what happens if this disruption lasts another 48 hours?" — they have to calculate it manually.

## Why Existing Solutions Fall Short

Existing control tower products display current shipment status and disruption alerts, but they do not:

- **Simulate forward scenarios** — they show what is happening, not what will happen if the disruption extends.
- **Cross-reference cold-chain constraints with fleet availability** automatically.
- **Provide natural-language querying** — an operations manager cannot ask "which fleet asset should we send to Rotterdam right now?" and get a grounded, actionable answer in seconds.
- **Degrade gracefully** — if the AI layer is unavailable, the operational data should still be accessible and useful.

Our solution addresses all four gaps.
