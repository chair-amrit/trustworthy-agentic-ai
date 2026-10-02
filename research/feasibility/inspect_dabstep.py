"""
inspect_dabstep.py: inspect DABStep tasks and context files
before choosing the feasibility tasks.

Setup:
    pip install datasets huggingface_hub pandas

Usage:
    python inspect_dabstep.py
    python inspect_dabstep.py --split default
    python inspect_dabstep.py --split dev --tasks 5 7 12
    python inspect_dabstep.py --split default --tasks 25 59 38
    python inspect_dabstep.py --download payments.csv manual.md
    python inspect_dabstep.py --peek payments.csv
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download


REPO = "adyen/DABstep"
CONTEXT_PREFIX = "data/context/"
LOCAL_DIR = Path("data/dabstep")


def load_tasks(split: str) -> pd.DataFrame:
    """Load one DABStep task split."""
    return load_dataset(
        REPO,
        name="tasks",
        split=split,
    ).to_pandas()


def overview(df: pd.DataFrame, split: str) -> None:
    """Print task statistics and all tasks in the selected split."""
    n_answers = (
        df["answer"]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ).sum()

    print(
        f"\n=== split: {split} | "
        f"{len(df)} tasks | "
        f"{n_answers} with a public answer ==="
    )

    print("\n=== difficulty ===")
    print(df["level"].value_counts().to_string())

    print(f"\n=== {split} tasks ===")
    for _, r in df.iterrows():
        print(
            f"[{r['task_id']}] "
            f"({r['level']}) "
            f"{r['question']}"
        )


def print_tasks(df: pd.DataFrame, ids: list[str], split: str) -> None:
    """Print selected tasks from the chosen split."""
    for tid in ids:
        hit = df[df["task_id"].astype(str) == str(tid)]

        if hit.empty:
            print(f"\nTask {tid} not found in split '{split}'.")
            continue

        for _, r in hit.iterrows():
            print(
                f"\n--- task {r['task_id']} | "
                f"split={split} | "
                f"level={r['level']} ---"
            )
            print("Question  :", r["question"])
            print("Guidelines:", r["guidelines"])
            print(
                "Answer    :",
                r["answer"]
                if str(r["answer"]).strip()
                else "(not public)",
            )


def list_context() -> None:
    """List DABStep context files available on Hugging Face."""
    info = HfApi().dataset_info(
        REPO,
        files_metadata=True,
    )

    rows = [
        (
            s.rfilename,
            (s.size or 0) / 1e6,
        )
        for s in info.siblings
        if s.rfilename.startswith(CONTEXT_PREFIX)
    ]

    print("\n=== context files ===")

    for name, mb in sorted(rows):
        short_name = name.removeprefix(CONTEXT_PREFIX)
        print(f"{short_name:40s} {mb:10.2f} MB")


def download(names: list[str]) -> None:
    """Download selected context files."""
    for name in names:
        path = hf_hub_download(
            repo_id=REPO,
            repo_type="dataset",
            filename=CONTEXT_PREFIX + name,
            local_dir=LOCAL_DIR,
        )
        print("Downloaded:", path)


def peek(name: str) -> None:
    """Inspect one downloaded context file."""
    path = LOCAL_DIR / CONTEXT_PREFIX / name

    if not path.exists():
        print(
            f"{path} not found. "
            f"Run --download {name} first."
        )
        return

    print(f"\n=== {name} ===")

    if path.suffix == ".csv":
        df = pd.read_csv(path)

        print("shape:", df.shape)
        print("\ndtypes:\n", df.dtypes.to_string())
        print("\nhead:\n", df.head().to_string())

    elif path.suffix == ".json":
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        print(
            "type:",
            type(data).__name__,
            "| length:",
            len(data),
        )

        if isinstance(data, list):
            sample = data[0]
        else:
            sample = next(iter(data.items()))

        print(
            "first item:\n",
            json.dumps(
                sample,
                indent=2,
                default=str,
            )[:1500],
        )

    else:
        print(
            path.read_text(
                encoding="utf-8"
            )[:3000]
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--split",
        choices=["dev", "default"],
        default="dev",
        help="DABStep task split to inspect (default: dev)",
    )

    parser.add_argument(
        "--tasks",
        nargs="*",
        help="task IDs to print from the selected split",
    )

    parser.add_argument(
        "--download",
        nargs="*",
        help="context file names to download",
    )

    parser.add_argument(
        "--peek",
        help="inspect one downloaded context file",
    )

    args = parser.parse_args()

    if args.download:
        download(args.download)

    elif args.peek:
        peek(args.peek)

    else:
        df = load_tasks(args.split)

        if args.tasks:
            print_tasks(
                df,
                args.tasks,
                args.split,
            )
        else:
            overview(
                df,
                args.split,
            )
            list_context()


if __name__ == "__main__":
    main()