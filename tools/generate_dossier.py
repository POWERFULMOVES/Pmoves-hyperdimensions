#!/usr/bin/env python3
"""Generate per-submodule integration dossiers for Hyperdimensions.

Fills the PMOVES.AI_INTEGRATION.md template per submodule using data from
the agent registry, services catalog, and NATS subject catalog.

Usage:
    python tools/generate_dossier.py                          # generate all
    python tools/generate_dossier.py --submodule PMOVES-HiRAG # single
"""

import argparse
import os
import sys
import textwrap
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent  # Pmoves-hyperdimensions/
PMOVES_ROOT = REPO_ROOT.parent  # PMOVES.AI/
REGISTRY_PATH = PMOVES_ROOT / "pmoves" / "config" / "agent_registry.yaml"
DOCS_DIR = REPO_ROOT / "docs"

# Import branch suffix map from topology generator
sys.path.insert(0, str(SCRIPT_DIR))
from generate_topology import BRANCH_SUFFIXES, get_all_submodules, agents_for_submodule


# Layer descriptions
LAYER_DESCRIPTIONS = {
    "L0": "Identity Anchors (325 persona anchors)",
    "L1": "Orchestrators (control-plane coordination)",
    "L2": "Bus + Routing (NATS transport, gateway routing)",
    "L2.5": "Hyperdimensions (geometry state visualization + control knobs)",
    "L3": "Swarm Intelligence (EvoSwarm, role-based packs)",
    "L4": "Modal Intelligence (text LLM, audio/TTS/STT, VLM)",
    "L5": "Memory + Safety (persistent storage, CHIT manifests, sandboxes)",
}

# Evolution stage descriptions
EVOLUTION_DESCRIPTIONS = {
    "base": "Base form (1-2 layers, single type)",
    "stage_1": "Stage 1 (3-4 layers, NATS connected, multi-layer awareness)",
    "stage_2": "Stage 2 (5+ layers, CHIT-enabled, publishes/consumes CGP packets)",
    "mega": "Mega Evolution (full-stack, spans all planes)",
}


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_dossier(submodule, agents, registry):
    """Generate an integration dossier markdown for a submodule."""
    today = date.today().isoformat()
    suffix = BRANCH_SUFFIXES.get(submodule, submodule.split("-")[-1])

    # Collect agent info
    agent_lines = []
    all_publishes = []
    all_subscribes = []
    all_layers = set()
    all_ports = []
    all_health = []
    primary_types = set()
    evolution_stages = set()
    chit_summary = {"delta": False, "kappa": False, "hz": False, "swarm": False, "attribution": False}

    for key, ag in agents:
        name = ag.get("name", key)
        cls = ag.get("class", "standard")
        ptype = ag.get("primary_type", "data")
        stype = ag.get("secondary_type", "")
        port = ag.get("port")
        health = ag.get("health")
        layers = ag.get("layers", [])
        stage = ag.get("evolution_stage", "base")
        desc = ag.get("description", "")

        type_str = f"{ptype}/{stype}" if stype else ptype
        agent_lines.append(f"| {name} | {cls} | {type_str} | {port or 'N/A'} | {stage} | {desc} |")

        nats = ag.get("nats", {})
        all_publishes.extend(nats.get("publishes", []))
        all_subscribes.extend(nats.get("subscribes", []))
        all_layers.update(layers)
        if port:
            all_ports.append(f"{port} ({name})")
        if health:
            all_health.append(f"`{health}` on port {port}" if port else f"`{health}`")
        primary_types.add(ptype)
        evolution_stages.add(stage)

        toggles = ag.get("chit_toggles", {})
        if toggles.get("delta_sensitive"):
            chit_summary["delta"] = True
        if toggles.get("kappa_sensitive"):
            chit_summary["kappa"] = True
        if toggles.get("hz_sensitive"):
            chit_summary["hz"] = True
        if toggles.get("swarm_participant"):
            chit_summary["swarm"] = True
        if toggles.get("attribution_gated"):
            chit_summary["attribution"] = True

    # Layer coverage
    layer_order = ["L0", "L1", "L2", "L2.5", "L3", "L4", "L5"]
    layer_lines = []
    for l in layer_order:
        active = "yes" if l in all_layers else "no"
        desc = LAYER_DESCRIPTIONS.get(l, "")
        layer_lines.append(f"| {l} | {active} | {desc} |")

    # CHIT toggles
    chit_lines = []
    for toggle, active in chit_summary.items():
        chit_lines.append(f"| {toggle} | {'yes' if active else 'no'} |")

    # NATS subjects
    pub_lines = "\n".join(f"- `{s}`" for s in all_publishes) if all_publishes else "- None"
    sub_lines = "\n".join(f"- `{s}`" for s in all_subscribes) if all_subscribes else "- None"

    agents_table = "\n".join(agent_lines) if agent_lines else "| (no agents in registry) | | | | | |"
    ports_str = ", ".join(all_ports) if all_ports else "N/A"
    health_str = "\n".join(f"- {h}" for h in all_health) if all_health else "- N/A"
    types_str = ", ".join(sorted(primary_types)) if primary_types else "N/A"

    # Highest evolution stage
    stages_order = ["base", "stage_1", "stage_2", "mega"]
    max_stage = "base"
    for s in evolution_stages:
        if s in stages_order and stages_order.index(s) > stages_order.index(max_stage):
            max_stage = s

    dossier = f"""# {submodule} — Hyperdimensions Integration Dossier

_Last updated: {today}_
_Branch variant: `PMOVES.AI-Edition-Hardened-{suffix}`_
_Topology file: `saves/{submodule.replace('.', '_')}_topology.json`_

---

## 1. Module Identity

| Field | Value |
|-------|-------|
| **Submodule** | `{submodule}` |
| **Branch Suffix** | `-{suffix}` |
| **Primary Type(s)** | {types_str} |
| **Evolution Stage** | {max_stage} — {EVOLUTION_DESCRIPTIONS.get(max_stage, '')} |
| **Ports** | {ports_str} |

## 2. Purpose in PMOVES.AI

This dossier documents the hyperdimensional display configuration for `{submodule}`.
The topology JSON renders this submodule's agents and services on a Poincare disk,
with CHIT geometry state vector driving the surface deformation.

## 3. Agent Roster

| Agent | Class | Type | Port | Stage | Description |
|-------|-------|------|------|-------|-------------|
{agents_table}

## 4. Layer Coverage

| Layer | Active | Description |
|-------|--------|-------------|
{chr(10).join(layer_lines)}

## 5. CHIT Toggle Sensitivity

| Toggle | Active |
|--------|--------|
{chr(10).join(chit_lines)}

These toggles determine whether this submodule's agents respond to geometry
state vector changes from the Hyperdimensions control plane (L2.5).

## 6. NATS Subjects

### Publishes
{pub_lines}

### Subscribes
{sub_lines}

## 7. Health Endpoints

{health_str}

## 8. Topology Configuration

- **Poincare Disk Model**: Agents positioned by class (ring) and type (sector)
- **Surface Height**: Driven by CHIT toggle density x evolution stage multiplier
- **Color Encoding**: Primary type color modulated by readiness
- **Animation**: delta, fitness, hz parameters oscillate to show state dynamics

### Geometry State Vector Defaults

| Parameter | Default | Driven By |
|-----------|---------|-----------|
| delta | {0.7 if chit_summary['delta'] else 0.2} | Tree-likeness sensitivity |
| kappa | {-0.5 if chit_summary['kappa'] else 0.0} | Hierarchy pressure |
| hz | {0.6 if chit_summary['hz'] else 0.1} | Spectral entropy |
| fitness | {0.9 if chit_summary['swarm'] else 0.5} | Swarm participation |
| attribution | {0.95 if chit_summary['attribution'] else 0.4} | Attribution gating |

## 9. Cross-References

- **Service Catalog**: [`.claude/context/services-catalog.md`](../../.claude/context/services-catalog.md)
- **CHIT Integration**: [`pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md`](../../pmoves/docs/PMOVESCHIT/GEOMETRY_BUS_INTEGRATION.md)
- **Agent Taxonomy**: [`pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md`](../../pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md)
- **NATS Subjects**: [`.claude/context/nats-subjects.md`](../../.claude/context/nats-subjects.md)
- **Submodule Docs**: [`{submodule}/README.md`](../../{submodule}/README.md)
- **Global Topology**: [`saves/agent_topology.json`](../saves/agent_topology.json)

## 10. Owner / Audit

| Field | Value |
|-------|-------|
| Owning lane | L2.5 Hyperdimensions |
| Integration audit | {today} |
| Registry source | `pmoves/config/agent_registry.yaml` |
"""
    return dossier


def main():
    parser = argparse.ArgumentParser(description="Generate per-submodule integration dossiers")
    parser.add_argument("--submodule", type=str, help="Generate for a single submodule")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    registry = load_registry()
    all_submodules = get_all_submodules(registry)

    if args.submodule:
        if args.submodule not in all_submodules:
            print(f"Submodule '{args.submodule}' not found in registry.")
            print(f"Available: {', '.join(all_submodules)}")
            sys.exit(1)
        targets = [args.submodule]
    else:
        targets = all_submodules

    generated = 0
    for sub in targets:
        agents = agents_for_submodule(registry, sub)
        dossier = generate_dossier(sub, agents, registry)
        key = sub.replace(".", "_").replace(" ", "_")
        doc_dir = DOCS_DIR / key
        filepath = doc_dir / "INTEGRATION_DOSSIER.md"

        if args.dry_run:
            print(f"[DRY RUN] Would write: {filepath}")
            print(f"  Agents: {[a[0] for a in agents]}")
            continue

        doc_dir.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dossier)

        generated += 1
        print(f"  Generated: {filepath.relative_to(REPO_ROOT)} ({len(agents)} agents)")

    print(f"\nTotal generated: {generated} dossiers")


if __name__ == "__main__":
    main()
