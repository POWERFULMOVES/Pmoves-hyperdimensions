# PMOVES.AI Integration Dossier

_Last updated: 2026-04-28_

## Module
- Name: Pmoves-hyperdimensions
- Path: Pmoves-hyperdimensions

## Purpose in PMOVES.AI
- 3D/WebGL visualization for CHIT consciousness data and holographic rendering.

## PMOVES Overlay Surface
- pmoves-integrations/ overlay path (if used): _TBD_
- Compose/profile wiring: served by `pmoves/services/hi-rag-gateway-v2` at `/hyperdimensions/app`
- Env/secret inputs: _TBD_
- Auth/JWT requirements: _TBD_

## Contracts and Topics
- NATS subjects (if any): `geometry.cgp.v1`, `content.hirag.accepted.v1`
- Supabase schema/tables touched (if any): _TBD_
- MCP endpoints/skills (if any): gateway surfaces `/hyperdimensions/provenance/latest.json` and `/hyperdimensions/provenance/view`
- Live refresh path: viewer joins `/ws/signaling/geometry` and listens for `hyperdimensions.save.v1`

## Boot Order and Health
- Bring-up dependency order: `hi-rag-gateway-v2` first, then any `content.hirag.accepted.v1` producers
- Health endpoints: inherit `hi-rag-gateway-v2` health plus live provenance view at `/hyperdimensions/provenance/view`
- Smoke targets: _TBD_

## Hardening Notes
- Image pinning / provenance: _TBD_
- Secrets source (*_FILE / vault / GH env): _TBD_
- Network/security policy constraints: _TBD_

## Source Documentation
- Upstream docs entrypoint: README.md
- PMOVES docs index reference: pmoves/docs/SUBMODULE_DOCS_DOSSIER.md

## Owner / Audit
- Owning lane: _TBD_
- Last integration audit run: 2026-04-04
