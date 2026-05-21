# Source Roadmap

## Active v1 Adapters

- FoodLK: hub summary, platform freshness, essentials basket, item/market quote-ready structure.
- Octane: latest fuel pricing, health, and trip-calculator-ready fuel rates.
- PropertyLK: national stats, districts, pipeline, rental-yield-ready structure.
- AutoLens: market stats, trends, listings/estimate-ready summaries, pipeline status.

## Official Expansion

- Food: CBSL Daily Price Report, HARTI daily bulletin, CAA maximum retail prices, World Bank RTP food prices.
- Fuel, utilities, transport: CPC fuel pricing, PUCSL electricity tariffs, NTC bus fares.
- Imports and vehicle context: Sri Lanka Customs tariff, CBSL exchange rates.

## Affordability Index

The Ariva affordability index is a practical Sri Lanka-local planning basket. It combines weighted food, housing, fuel, vehicle, utilities, and transport signals. Numbeo-style basket categories are useful as a methodology reference, but Ariva should use Sri Lanka-local source data and clearly labelled assumptions.

## Limits

- The v1 property and vehicle contributions use conservative planning proxies when rental-yield or ownership-cost feeds are not normalized yet.
- Utility and transport inputs are static v1 assumptions until official tariff snapshots are added.
- Upstream failures should degrade one domain, not fail the full platform.
