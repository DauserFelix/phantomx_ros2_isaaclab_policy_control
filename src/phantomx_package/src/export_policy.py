#!/usr/bin/env python3
# export_policy.py

import argparse
import os
import torch


def export_policy(checkpoint_path: str, output_path: str):
    print(f"[INFO] Lade Checkpoint: {checkpoint_path}")
    ckpt = torch.load(checkpoint_path, map_location="cpu")

    actor_state = ckpt["actor_state_dict"]

    # Nur mlp.* Keys, prefix "mlp." entfernen
    mlp_state = {
        k.replace("mlp.", ""): v
        for k, v in actor_state.items()
        if k.startswith("mlp.")
    }
    print(f"[INFO] MLP Keys: {list(mlp_state.keys())}")

    # Netzwerk-Dimensionen ableiten
    layer_keys = sorted([k for k in mlp_state.keys() if "weight" in k])
    input_size   = mlp_state[layer_keys[0]].shape[1]
    hidden_sizes = [mlp_state[k].shape[0] for k in layer_keys[:-1]]
    output_size  = mlp_state[layer_keys[-1]].shape[0]

    print(f"[INFO] Architektur: {input_size} → {hidden_sizes} → {output_size}")

    # MLP aufbauen (rsl_rl verwendet ELU)
    layers = []
    sizes = [input_size] + hidden_sizes
    for i in range(len(sizes) - 1):
        layers.append(torch.nn.Linear(sizes[i], sizes[i + 1]))
        layers.append(torch.nn.ELU())
    layers.append(torch.nn.Linear(hidden_sizes[-1], output_size))
    actor = torch.nn.Sequential(*layers)

    actor.load_state_dict(mlp_state)
    actor.eval()

    # TorchScript exportieren
    example_input = torch.zeros(1, input_size)
    traced = torch.jit.trace(actor, example_input)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    traced.save(output_path)
    print(f"[INFO] Policy exportiert: {output_path}")

    # Schnelltest
    with torch.no_grad():
        out = traced(example_input)
    print(f"[INFO] Test: {example_input.shape} → {out.shape} ✓")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--output",     type=str, required=True)
    args = parser.parse_args()
    export_policy(args.checkpoint, args.output)