#!/usr/bin/env python3
"""Generate per-submodule topology JSONs for Hyperdimensions Poincare disk.

Reads pmoves/config/agent_registry.yaml and generates one topology JSON per
submodule, plus updates saves/_list.json with new entries.

Usage:
    python tools/generate_topology.py                    # generate all
    python tools/generate_topology.py --verify           # validate existing JSONs
    python tools/generate_topology.py --submodule PMOVES-HiRAG  # single submodule
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)

# Paths relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent  # Pmoves-hyperdimensions/
PMOVES_ROOT = REPO_ROOT.parent  # PMOVES.AI/
REGISTRY_PATH = PMOVES_ROOT / "pmoves" / "config" / "agent_registry.yaml"
SAVES_DIR = REPO_ROOT / "saves"
LIST_PATH = SAVES_DIR / "_list.json"

# Class ring radii on Poincare disk (inner=legendary, outer=utility)
CLASS_RINGS = {
    "legendary":   (0.00, 0.05),
    "standard":    (0.05, 0.40),
    "specialized": (0.40, 0.70),
    "utility":     (0.70, 0.95),
}

# Type sector angles (radians)
TYPE_SECTORS = {
    "data":   (0.00, 0.90),
    "api":    (0.90, 1.80),
    "llm":    (1.80, 2.70),
    "worker": (2.70, 3.60),
    "media":  (3.60, 4.50),
    "agent":  (4.50, 5.40),
    "ui":     (5.40, 6.28),
}

# Type colors from agent_registry.yaml
TYPE_COLORS = {
    "data":   {"r": 0.55, "g": 0.27, "b": 0.07},  # Brown
    "api":    {"r": 0.25, "g": 0.41, "b": 0.88},  # Blue
    "llm":    {"r": 0.86, "g": 0.08, "b": 0.24},  # Red
    "worker": {"r": 1.00, "g": 0.84, "b": 0.00},  # Yellow
    "media":  {"r": 0.00, "g": 0.81, "b": 0.82},  # Cyan
    "agent":  {"r": 0.58, "g": 0.44, "b": 0.86},  # Purple
    "ui":     {"r": 0.96, "g": 0.96, "b": 0.96},  # White
}

# Evolution stage multipliers for surface height
EVOLUTION_HEIGHT = {
    "base":    0.1,
    "stage_1": 0.2,
    "stage_2": 0.35,
    "mega":    0.5,
}

# Submodule to branch suffix mapping
BRANCH_SUFFIXES = {
    "PMOVES-Agent-Zero": "A0",
    "PMOVES-Archon": "Archon",
    "PMOVES-HiRAG": "HiRAG",
    "PMOVES-ToKenism-Multi": "TKM",
    "PMOVES-transcribe-and-fetch": "TnF",
    "PMOVES.YT": "YT",
    "PMOVES-BotZ-gateway": "BoTZ",
    "PMOVES-BoTZ": "BoTZ-CLI",
    "PMOVES-DoX": "DoX",
    "PMOVES-MAI-UI": "MAI",
    "Pmoves-cipher": "Cipher",
    "PMOVES-E2B-Danger-Room": "E2B",
    "PMOVES-E2B-Danger-Room-Desktop": "E2BD",
    "PMOVES-supabase": "Supa",
    "Pmoves-Jellyfin-AI-Media-Stack": "Jelly",
    "PMOVES-Jellyfin": "JellyBridge",
    "Pmoves-Health-wger": "Health",
    "PMOVES-Headscale": "HS",
    "PMOVES-Remote-View": "RV",
    "PMOVES-surf": "Surf",
    "pmoves-surf": "Surf",
    "PMOVES-llama-throughput-lab": "LLab",
    "PMOVES-AgentGym": "AGym",
    "Pmoves-AgentGym-RL": "AGRL",
    "Pmoves-hyperdimensions": "HD",
    "pmoves-e2b-mcp-server": "E2BMCP",
    "PMOVES-Deep-Serch": "DSerch",
    "PMOVES-Open-Notebook": "ONB",
    "PMOVES-n8n": "N8N",
    "PMOVES-Creator": "Creator",
    "PMOVES-Wealth": "Wealth",
    "PMOVES-crush": "Crush",
    "PMOVES-tensorzero": "TZ",
    "PMOVES-Pipecat": "Pipecat",
    "PMOVES-Tailscale": "TS",
    "PMOVES-A2UI": "A2UI",
    "PMOVES-Danger-infra": "DInfra",
    "PMOVES-E2b-Spells": "E2BS",
    "PMOVES-Pinokio-Ultimate-TTS-Studio": "PinoTTS",
    "PMOVES-Ultimate-TTS-Studio": "UTTS",
}


def load_registry():
    """Load the agent registry YAML."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def agents_for_submodule(registry, submodule_name):
    """Return all agents belonging to a given submodule."""
    agents = registry.get("agents", {})
    result = []
    for key, agent in agents.items():
        if agent.get("submodule") == submodule_name:
            result.append((key, agent))
    return result


def get_all_submodules(registry):
    """Extract unique submodule names from the registry."""
    submodules = set()
    for key, agent in registry.get("agents", {}).items():
        sub = agent.get("submodule")
        if sub:
            submodules.add(sub)
    return sorted(submodules)


def compute_position(agent, index, total):
    """Compute Poincare disk position for an agent."""
    cls = agent.get("class", "standard")
    ptype = agent.get("primary_type", "data")

    r_min, r_max = CLASS_RINGS.get(cls, (0.05, 0.40))
    theta_min, theta_max = TYPE_SECTORS.get(ptype, (0.0, 0.9))

    # Distribute agents within their sector
    if total > 1:
        theta_frac = index / (total - 1)
    else:
        theta_frac = 0.5
    theta = theta_min + theta_frac * (theta_max - theta_min)

    # Radial position: midpoint of class ring
    r = (r_min + r_max) / 2

    return r, theta


def chit_defaults(agent):
    """Extract CHIT toggle defaults from agent registry entry."""
    toggles = agent.get("chit_toggles", {})
    delta = 0.7 if toggles.get("delta_sensitive") else 0.2
    kappa = -0.5 if toggles.get("kappa_sensitive") else 0.0
    hz = 0.6 if toggles.get("hz_sensitive") else 0.1
    fitness = 0.9 if toggles.get("swarm_participant") else 0.5
    attribution = 0.95 if toggles.get("attribution_gated") else 0.4
    return delta, kappa, hz, fitness, attribution


def generate_surface_fn(submodule, agents, primary_type):
    """Generate a surfaceFn customized for the submodule's service type."""
    color = TYPE_COLORS.get(primary_type, TYPE_COLORS["data"])
    n_agents = len(agents)
    stage = "base"
    if agents:
        # Use the highest evolution stage among agents
        stages_order = ["base", "stage_1", "stage_2", "mega"]
        for _, ag in agents:
            ag_stage = ag.get("evolution_stage", "base")
            if stages_order.index(ag_stage) > stages_order.index(stage):
                stage = ag_stage

    height_mult = EVOLUTION_HEIGHT.get(stage, 0.1)

    fn = f"""function surface(input) {{
    // Poincare disk: {submodule} topology
    // {n_agents} agent(s), primary type: {primary_type}, stage: {stage}
    const theta = input.u * 2 * Math.PI;
    const r_raw = input.v * 0.95;
    const r = Math.tanh(r_raw * 2) * 0.95;

    // Geometry state vector
    const delta = input.delta || 0.5;
    const kappa = input.kappa || 0.0;
    const hz = input.hz || 0.2;
    const fitness = input.fitness || 0.7;
    const attrib = input.attribution || 0.8;

    // Toggle density drives surface height
    const density = (delta + (1+kappa) + (1-hz) + fitness + attrib) / 5.0;
    const z = Math.sin(theta * {max(3, n_agents * 2)}) * density * {height_mult} * r;

    // Position on Poincare disk
    const x = r * Math.cos(theta);
    const y = r * Math.sin(theta);

    // Color: {primary_type} type tint modulated by readiness
    const readiness = Math.min(1, density * 1.2);
    const red = {color['r']:.2f} * readiness + (1 - readiness) * 0.3;
    const green = {color['g']:.2f} * readiness + (1 - readiness) * 0.3;
    const blue = {color['b']:.2f} * readiness + (1 - readiness) * 0.3;

    return {{
        x: x * 5,
        y: y * 5,
        z: z,
        r: red,
        g: green,
        b: blue,
        a: 0.85
    }};
}}"""
    return fn


def generate_topology(submodule, agents, registry):
    """Generate a complete topology JSON for a submodule."""
    if not agents:
        # For submodules with no agents in registry, create a minimal topology
        primary_type = "data"
        delta, kappa, hz, fitness, attribution = 0.3, 0.0, 0.1, 0.5, 0.4
    else:
        # Use first agent's primary type as the submodule type
        _, first_agent = agents[0]
        primary_type = first_agent.get("primary_type", "data")
        # Average CHIT defaults across agents
        deltas, kappas, hzs, fits, attrs = [], [], [], [], []
        for _, ag in agents:
            d, k, h, f, a = chit_defaults(ag)
            deltas.append(d)
            kappas.append(k)
            hzs.append(h)
            fits.append(f)
            attrs.append(a)
        delta = sum(deltas) / len(deltas)
        kappa = sum(kappas) / len(kappas)
        hz = sum(hzs) / len(hzs)
        fitness = sum(fits) / len(fits)
        attribution = sum(attrs) / len(attrs)

    surface_fn = generate_surface_fn(submodule, agents, primary_type)

    # Agent metadata
    agent_entries = {}
    for key, ag in agents:
        r, theta = compute_position(ag, agents.index((key, ag)), len(agents))
        agent_entries[key] = {
            "name": ag.get("name", key),
            "class": ag.get("class", "standard"),
            "primary_type": ag.get("primary_type", "data"),
            "port": ag.get("port"),
            "layers": ag.get("layers", []),
            "evolution_stage": ag.get("evolution_stage", "base"),
            "position": {"r": round(r, 4), "theta": round(theta, 4)},
        }

    topology = {
        "surfaceFn": surface_fn,
        "params": {
            "uMin": 0,
            "uMax": 1,
            "vMin": 0,
            "vMax": 1,
            "uSegs": 200,
            "vSegs": 100,
        },
        "surfaceInput": {
            "u": 0,
            "v": 0,
            "delta": round(delta, 2),
            "kappa": round(kappa, 2),
            "hz": round(hz, 2),
            "fitness": round(fitness, 2),
            "attribution": round(attribution, 2),
        },
        "animatedParams": [
            {
                "name": "delta",
                "playing": True,
                "min": 0.1,
                "max": 0.9,
                "step": 0.01,
                "time": 8,
                "phase": 0,
            },
            {
                "name": "fitness",
                "playing": True,
                "min": 0.3,
                "max": 1.0,
                "step": 0.01,
                "time": 12,
                "phase": 1.57,
            },
            {
                "name": "hz",
                "playing": True,
                "min": 0.05,
                "max": 0.8,
                "step": 0.01,
                "time": 6,
                "phase": 3.14,
            },
        ],
        "camera": {
            "position": {"x": 0, "y": 0, "z": 8},
            "target": {"x": 0, "y": 0, "z": 0},
        },
        "shininess": 120,
        "globalSaturation": 1.3,
        "meta": {
            "description": f"{submodule} Topology on Poincare Disk",
            "submodule": submodule,
            "branch_suffix": BRANCH_SUFFIXES.get(submodule, submodule.split("-")[-1]),
            "taxonomy_version": "1.0.0",
            "geometry_state_vector": {
                "delta_proxy": round(delta, 2),
                "curvature_k": round(kappa, 2),
                "spectral_entropy_z": round(hz, 2),
                "swarm_fitness": round(fitness, 2),
                "attribution_confidence": round(attribution, 2),
            },
            "class_rings": {k: {"r_min": v[0], "r_max": v[1]} for k, v in CLASS_RINGS.items()},
            "type_sectors": {k: {"theta_min": v[0], "theta_max": v[1]} for k, v in TYPE_SECTORS.items()},
            "agents": agent_entries,
            "source": "pmoves/config/agent_registry.yaml",
            "docs": "pmoves/docs/AGENTS/PMOVES_AGENT_CLASS_TAXONOMY.md",
        },
    }
    return topology


def submodule_key(name):
    """Convert submodule name to a filesystem-safe key."""
    return name.replace(".", "_").replace(" ", "_")


def update_list_json(new_entries):
    """Update _list.json with new topology entries."""
    with open(LIST_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)

    existing_files = {e["file"] for e in entries}
    added = 0
    for entry in new_entries:
        if entry["file"] not in existing_files:
            entries.append(entry)
            added += 1

    with open(LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)
        f.write("\n")

    return added


def verify_topologies():
    """Validate all topology JSONs in saves/."""
    errors = []
    saves = SAVES_DIR
    for f in saves.glob("*_topology.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # Check required keys
            for key in ["surfaceFn", "params", "surfaceInput", "meta"]:
                if key not in data:
                    errors.append(f"{f.name}: missing key '{key}'")
            meta = data.get("meta", {})
            if not meta.get("submodule"):
                errors.append(f"{f.name}: meta.submodule not set")
            if not meta.get("agents"):
                errors.append(f"{f.name}: meta.agents empty (may be expected for infra-only)")
        except json.JSONDecodeError as e:
            errors.append(f"{f.name}: invalid JSON: {e}")

    if errors:
        print(f"VERIFICATION FAILED ({len(errors)} issues):")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        count = len(list(saves.glob("*_topology.json")))
        print(f"VERIFICATION PASSED: {count} topology files valid")
        return True


def main():
    parser = argparse.ArgumentParser(description="Generate per-submodule topology JSONs")
    parser.add_argument("--verify", action="store_true", help="Validate existing JSONs")
    parser.add_argument("--submodule", type=str, help="Generate for a single submodule")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    if args.verify:
        ok = verify_topologies()
        sys.exit(0 if ok else 1)

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

    new_list_entries = []
    generated = 0

    for sub in targets:
        agents = agents_for_submodule(registry, sub)
        topology = generate_topology(sub, agents, registry)
        key = submodule_key(sub)
        filename = f"{key}_topology.json"
        filepath = SAVES_DIR / filename

        if args.dry_run:
            print(f"[DRY RUN] Would write: {filepath}")
            print(f"  Agents: {[a[0] for a in agents]}")
            continue

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(topology, f, indent=2, ensure_ascii=False)
            f.write("\n")

        suffix = BRANCH_SUFFIXES.get(sub, key)
        display_name = f"{sub} Topology ({suffix})"
        new_list_entries.append({"file": filename, "name": display_name})
        generated += 1
        print(f"  Generated: {filename} ({len(agents)} agents)")

    if not args.dry_run and new_list_entries:
        added = update_list_json(new_list_entries)
        print(f"\nUpdated _list.json: {added} new entries added")

    print(f"\nTotal generated: {generated} topology files")


if __name__ == "__main__":
    main()
