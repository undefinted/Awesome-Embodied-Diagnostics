#!/usr/bin/env python3
"""Apply an explicit, reviewable taxonomy mapping to the curated P5 projects."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


MAPPING = {
    "P5PRJ01": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "closed_loop_research", "force and image-quality feedback guide contact and trajectory"),
    "P5PRJ02": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "shared_control_or_teleoperation", "robot arms, sensors, remote control and haptic feedback"),
    "P5PRJ03": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "autonomous_planned_acquisition", "selected region, autonomous path planning, robot acquisition and 3D reconstruction"),
    "P5PRJ04": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "closed_loop_research", "planned path with maintained contact force"),
    "P5PRJ05": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "closed_loop_research", "learning-based carotid scanning extended with tactile feedback"),
    "P5PRJ06": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "shared_control_or_predefined_autonomy", "teleoperation plus predetermined autonomous survey trajectories"),
    "P5PRJ07": ("T1", "超声检查与主动扫查", "ultrasound", "robotic_manipulator_arm", "automatic_acquisition_feedback_unclear", "automatic scanning reported; online evidence-driven adaptation requires source-level confirmation"),
    "P5PRJ08": ("T5", "眼科主动对准与成像", "slit_lamp_stereo_imaging", "dedicated_mechatronic_scanner", "human_in_loop_physical_acquisition", "remote clinician controls the physical slit lamp and acquires patient images"),
    "P5PRJ09": ("T7", "主动听诊与声学检查", "acoustic_physiological_sound", "robotic_manipulator_arm", "closed_loop_research", "visual registration, contact control and autonomous auscultation"),
    "P5PRJ10": ("T7", "主动听诊与声学检查", "acoustic_physiological_sound", "robotic_manipulator_arm", "closed_loop_research", "LiDAR registration, autonomous placement and passive force control"),
    "P5PRJ11": ("T9", "临床任务未定或跨任务采集技术", "confocal_endomicroscopy", "robotic_manipulator_arm", "closed_loop_research_platform", "autonomous tissue scanning with live mosaicing and 3D fusion; clinical examination procedure unspecified"),
    "P5PRJ12": ("T3", "主动或磁控胶囊内镜检查", "OCT;endomicroscopy", "magnetic_active_capsule", "closed_loop_research_project", "magnetic navigation and microscopic observation; proposed sampling is a separate task phase"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with args.projects.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output_rows = []
    for row in rows:
        project_id = row["project_id"]
        if project_id not in MAPPING:
            raise SystemExit(f"Missing explicit taxonomy mapping for {project_id}")
        task_code, task_cn, modality, carrier, loop_level, rationale = MAPPING[project_id]
        row.update({
            "primary_task_code": task_code,
            "primary_task_cn": task_cn,
            "modality_tags": modality,
            "carrier_tags": carrier,
            "loop_characterization": loop_level,
            "classification_rationale": rationale,
            "source_access_checked": "2026-08-14",
            "counting_note": "curated named project/system; never added to publication counts",
        })
        output_rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"projects={len(output_rows)}")


if __name__ == "__main__":
    main()
