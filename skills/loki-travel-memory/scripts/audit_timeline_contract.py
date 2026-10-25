#!/usr/bin/env python3
"""Validate reusable timing invariants for Loki travel-memory projects."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_FIELDS = {
    "scenes": {
        "id",
        "start",
        "end",
        "event_id",
        "media_ids",
        "primary_subject",
        "protected_regions",
        "max_emphasis_overlays",
        "layout_grammar",
        "layout_reason",
    },
    "transitions": {
        "id",
        "start",
        "end",
        "from_scene_id",
        "to_scene_id",
        "kind",
        "match_basis",
        "reason",
        "audio_bridge",
        "focus_owner_before",
        "focus_owner_after",
        "moving_focus_layers",
        "handoff_mode",
        "music_cue",
    },
    "subtitles": {"id", "start", "end", "text", "source_id"},
    "overlays": {"id", "start", "end", "role", "owner_scene_id", "exit_mode"},
    "speech": {"id", "start", "end", "source_id"},
    "music": {
        "id",
        "start",
        "end",
        "source",
        "title",
        "artist",
        "source_in",
        "source_out",
        "owner_scene_ids",
        "entry_mode",
        "entry_reason",
    },
}


def valid_time(item: dict) -> bool:
    try:
        return float(item["end"]) > float(item["start"])
    except (KeyError, TypeError, ValueError):
        return False


def overlaps(items: list[dict], label: str, errors: list[str], tolerance: float) -> None:
    ordered = sorted(
        (item for item in items if valid_time(item)),
        key=lambda x: (float(x["start"]), float(x["end"])),
    )
    for left, right in zip(ordered, ordered[1:]):
        if float(left["end"]) > float(right["start"]) + tolerance:
            errors.append(
                f"{label} overlap: {left.get('id')} ends {left['end']} after "
                f"{right.get('id')} starts {right['start']}"
            )


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    fps = float(data.get("fps", 0))
    if fps <= 0:
        return ["fps must be a positive number"]
    frame = 1.0 / fps
    tolerance = frame + 1e-6

    for collection_name, required in REQUIRED_FIELDS.items():
        seen_ids: set[str] = set()
        for item in data.get(collection_name, []):
            missing = sorted(required - set(item))
            if missing:
                errors.append(
                    f"{collection_name} item {item.get('id')} misses required fields: "
                    f"{', '.join(missing)}"
                )
            item_id = str(item.get("id", ""))
            if item_id and item_id in seen_ids:
                errors.append(f"{collection_name} contains duplicate id {item_id}")
            seen_ids.add(item_id)
            try:
                start, end = float(item["start"]), float(item["end"])
            except (KeyError, TypeError, ValueError):
                errors.append(f"{collection_name} item {item.get('id')} has invalid start/end")
                continue
            if end <= start:
                errors.append(f"{collection_name} item {item.get('id')} must end after start")

    scenes = {str(x["id"]): x for x in data.get("scenes", []) if x.get("id")}
    subtitles = {str(x["id"]): x for x in data.get("subtitles", []) if x.get("id")}

    for scene in data.get("scenes", []):
        sid = scene.get("id")
        if not str(scene.get("primary_subject", "")).strip():
            errors.append(f"scene {sid} requires non-empty primary_subject")
        for field in ("layout_grammar", "layout_reason"):
            if not str(scene.get(field, "")).strip():
                errors.append(f"scene {sid} requires non-empty {field}")
        protected = scene.get("protected_regions")
        if not isinstance(protected, list):
            errors.append(f"scene {sid} protected_regions must be a list")
        try:
            budget = int(scene.get("max_emphasis_overlays"))
            if budget < 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"scene {sid} max_emphasis_overlays must be a non-negative integer")

    transitions_by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for transition in data.get("transitions", []):
        tid = transition.get("id")
        from_id = str(transition.get("from_scene_id", ""))
        to_id = str(transition.get("to_scene_id", ""))
        source = scenes.get(from_id)
        target = scenes.get(to_id)
        transitions_by_pair[(from_id, to_id)].append(transition)
        if not source:
            errors.append(f"transition {tid} references missing source scene {from_id}")
        if not target:
            errors.append(f"transition {tid} references missing target scene {to_id}")
        if from_id == to_id and from_id:
            errors.append(f"transition {tid} cannot connect a scene to itself")
        for field in ("kind", "reason", "audio_bridge"):
            if not str(transition.get(field, "")).strip():
                errors.append(f"transition {tid} requires non-empty {field}")
        basis = transition.get("match_basis")
        if not basis or (isinstance(basis, str) and not basis.strip()):
            errors.append(f"transition {tid} requires non-empty match_basis")
        for field in ("focus_owner_before", "focus_owner_after", "handoff_mode", "music_cue"):
            if not str(transition.get(field, "")).strip():
                errors.append(f"transition {tid} requires non-empty {field}")
        moving_layers = transition.get("moving_focus_layers")
        if not isinstance(moving_layers, list):
            errors.append(f"transition {tid} moving_focus_layers must be a list")
        elif len(moving_layers) > 1:
            if not transition.get("allow_multi_focus"):
                errors.append(
                    f"transition {tid} moves {len(moving_layers)} focus layers; "
                    "set allow_multi_focus with a concrete reason"
                )
            elif not str(transition.get("multi_focus_reason", "")).strip():
                errors.append(f"transition {tid} allows multi-focus without multi_focus_reason")
        if isinstance(moving_layers, list) and moving_layers:
            focus_after = str(transition.get("focus_owner_after", ""))
            if focus_after not in {str(layer) for layer in moving_layers}:
                errors.append(
                    f"transition {tid} focus_owner_after {focus_after!r} is not the moving focus layer"
                )
        if source and target and valid_time(transition):
            start, end = float(transition["start"]), float(transition["end"])
            seam_start = min(float(source["end"]), float(target["start"]))
            seam_end = max(float(source["end"]), float(target["start"]))
            if start > seam_start + tolerance or end < seam_end - tolerance:
                errors.append(
                    f"transition {tid} does not bridge scene seam {from_id} -> {to_id}"
                )

    ordered_scenes = sorted(
        (scene for scene in data.get("scenes", []) if valid_time(scene) and scene.get("id")),
        key=lambda x: (float(x["start"]), float(x["end"])),
    )
    for left, right in zip(ordered_scenes, ordered_scenes[1:]):
        pair = (str(left["id"]), str(right["id"]))
        if not transitions_by_pair.get(pair):
            errors.append(
                f"missing transition record for adjacent scenes {pair[0]} -> {pair[1]}"
            )

    overlaps(data.get("speech", []), "speech", errors, 1e-6)
    overlaps(data.get("subtitles", []), "subtitle", errors, tolerance)

    for overlay in data.get("overlays", []):
        oid = overlay.get("id")
        owner_id = str(overlay.get("owner_scene_id", ""))
        owner = scenes.get(owner_id)
        if not owner:
            errors.append(f"overlay {oid} references missing owner scene {owner_id}")
            continue
        if not valid_time(overlay) or not valid_time(owner):
            continue
        start, end = float(overlay["start"]), float(overlay["end"])
        if start < float(owner["start"]) - tolerance or end > float(owner["end"]) + tolerance:
            errors.append(f"overlay {oid} falls outside owner scene {owner_id}")
        mode = overlay.get("exit_mode")
        if mode == "with_owner":
            if abs(end - float(owner["end"])) > tolerance:
                errors.append(f"overlay {oid} must end with owner scene {owner_id} within one frame")
        elif mode == "with_subtitle":
            sid = str(overlay.get("linked_subtitle_id", ""))
            subtitle = subtitles.get(sid)
            if not subtitle:
                errors.append(f"overlay {oid} references missing subtitle {sid}")
            elif valid_time(subtitle) and abs(end - float(subtitle["end"])) > tolerance:
                errors.append(f"overlay {oid} must end with subtitle {sid} within one frame")
        elif mode == "explicit":
            if not str(overlay.get("exit_reason", "")).strip():
                errors.append(f"overlay {oid} uses explicit exit without exit_reason")
        else:
            errors.append(f"overlay {oid} has unsupported exit_mode {mode!r}")

    emphasis_roles = {"flower_copy", "progress_number", "explanatory_copy"}
    emphasis_counts: dict[str, int] = defaultdict(int)
    for overlay in data.get("overlays", []):
        if overlay.get("role") in emphasis_roles:
            emphasis_counts[str(overlay.get("owner_scene_id", ""))] += 1
    for scene_id, count in emphasis_counts.items():
        scene = scenes.get(scene_id)
        if not scene:
            continue
        try:
            budget = int(scene.get("max_emphasis_overlays"))
        except (TypeError, ValueError):
            continue
        if count > budget:
            errors.append(
                f"scene {scene_id} has {count} emphasis overlays, exceeding budget {budget}"
            )

    ordered_music = sorted(
        (item for item in data.get("music", []) if valid_time(item)),
        key=lambda x: (float(x["start"]), float(x["end"])),
    )
    for track in ordered_music:
        mid = track.get("id")
        try:
            source_in = float(track["source_in"])
            source_out = float(track["source_out"])
            if source_out <= source_in:
                errors.append(f"music {mid} source_out must be after source_in")
            elif float(track["end"]) - float(track["start"]) > source_out - source_in + tolerance:
                errors.append(f"music {mid} timeline duration exceeds selected source range")
        except (KeyError, TypeError, ValueError):
            errors.append(f"music {mid} has invalid source_in/source_out")

        owner_ids = track.get("owner_scene_ids")
        if not isinstance(owner_ids, list) or not owner_ids:
            errors.append(f"music {mid} owner_scene_ids must be a non-empty list")
            continue
        owners = [scenes.get(str(owner_id)) for owner_id in owner_ids]
        missing_owners = [str(owner_id) for owner_id, owner in zip(owner_ids, owners) if owner is None]
        if missing_owners:
            errors.append(f"music {mid} references missing owner scenes: {', '.join(missing_owners)}")
            continue
        first_start = min(float(owner["start"]) for owner in owners if owner)
        last_end = max(float(owner["end"]) for owner in owners if owner)
        entry_mode = track.get("entry_mode")
        if not str(track.get("entry_reason", "")).strip():
            errors.append(f"music {mid} requires non-empty entry_reason")
        if entry_mode == "with_owner":
            if float(track["start"]) < first_start - tolerance:
                errors.append(f"music {mid} enters before its first owner scene")
        elif entry_mode == "bridge":
            if not str(track.get("entry_reason", "")).strip():
                errors.append(f"music {mid} uses bridge entry without entry_reason")
        else:
            errors.append(f"music {mid} has unsupported entry_mode {entry_mode!r}")
        if float(track["end"]) > last_end + tolerance:
            errors.append(f"music {mid} continues after its last owner scene")

    for left, right in zip(ordered_music, ordered_music[1:]):
        if float(left["end"]) <= float(right["start"]) + tolerance:
            continue
        for track in (left, right):
            if not track.get("allow_overlap") or not str(track.get("overlap_reason", "")).strip():
                errors.append(
                    f"music overlap {left.get('id')} -> {right.get('id')} requires "
                    "allow_overlap and overlap_reason on both tracks"
                )
                break

    media_scenes: dict[str, list[dict]] = defaultdict(list)
    for scene in data.get("scenes", []):
        for media in scene.get("media_ids", []):
            media_scenes[str(media)].append(scene)
        if scene.get("allow_repeat"):
            if not str(scene.get("repeat_reason", "")).strip():
                errors.append(f"scene {scene.get('id')} allows repeats without repeat_reason")
    for media_id, repeated_in in media_scenes.items():
        if len(repeated_in) <= 1:
            continue
        if not all(
            scene.get("allow_repeat") and str(scene.get("repeat_reason", "")).strip()
            for scene in repeated_in
        ):
            errors.append(
                f"media {media_id} is used {len(repeated_in)} times; every repeated scene "
                "must set allow_repeat and repeat_reason"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    data = json.loads(args.contract.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("timeline contract passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
