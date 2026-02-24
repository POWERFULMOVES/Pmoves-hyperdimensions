# PMOVES.AI Integration Dossier

_Last updated: 2026-02-23_

## Module
- Name: Pmoves-hyperdimensions
- Path: `Pmoves-hyperdimensions/`

## Purpose in PMOVES.AI
- **Role:** UI/data — Geometry visualization surface and control plane (L2.5)
- **Primary Type:** `ui`
- Renders agents and services on a Poincare disk with CHIT geometry state vector driving surface deformation.
- Branch variant: `PMOVES.AI-Edition-Hardened-HD`

## PMOVES Overlay Surface
- pmoves-integrations/ overlay path (if used): N/A (standalone visualization layer)
- Compose/profile wiring: N/A (no Docker service — static topology JSON consumed by UI)
- Env/secret inputs: None required (visualization layer, no external API calls)
- Auth/JWT requirements: None (no HTTP endpoints)

## Contracts and Topics
- NATS subjects: Subscribes to `geometry.visualization.request.v1` (publishes none)
- Supabase schema/tables touched: None
- MCP endpoints/skills: None

## Boot Order and Health
- Bring-up dependency order: None (standalone, no runtime dependencies)
- Health endpoints: N/A (no HTTP service)
- Smoke targets: Verify topology JSON at `saves/Pmoves-hyperdimensions_topology.json`

## Hardening Notes
- Image pinning / provenance: N/A (no container image)
- Secrets source: None required
- Network/security policy constraints: N/A (no network exposure)

## Source Documentation
- Upstream docs entrypoint: README.md
- PMOVES docs index reference: pmoves/docs/SUBMODULE_DOCS_DOSSIER.md
- Detailed dossier: `docs/Pmoves-hyperdimensions/INTEGRATION_DOSSIER.md`

## CHIT Toggle Sensitivity

| Toggle | Active | Description |
|--------|--------|-------------|
| delta | yes | Tree-likeness sensitivity |
| kappa | yes | Hierarchy pressure |
| hz | yes | Spectral entropy |
| swarm | yes | Swarm participation |
| attribution | yes | Attribution gating |

## Layer Coverage

| Layer | Active | Description |
|-------|--------|-------------|
| L0 | yes | Identity Anchors (325 persona anchors) |
| L2.5 | yes | Hyperdimensions (geometry state visualization + control knobs) |

## Owner / Audit
- Owning lane: L2.5 Hyperdimensions
- Last integration audit run: 2026-02-16
- Registry source: `pmoves/config/agent_registry.yaml`
