import subprocess
import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def run_benchmark(test_dir, config_name, flag, output_dir):
    txt_file = output_dir / f"bench_{config_name}.txt"
    csv_file = output_dir / f"bench_{config_name}.csv"
    eps_file = output_dir / f"bench_{config_name}.eps"

    print(f"Running {config_name} benchmarks...")

    if flag.startswith("-"):
        cmd = ["go", "test", "-bench=.", flag]
    elif flag:
        cmd = ["go", "test", "-bench=.", f"-gcflags={flag}"]
    else:
        cmd = ["go", "test", "-bench=."]

    with open(txt_file, "w") as f:
        subprocess.run(cmd, cwd=test_dir, stdout=f, stderr=subprocess.STDOUT)

    print(f"==== Output for {config_name} ====")
    with open(txt_file) as f:
        print(f.read())

    if not any("ns/op" in line for line in open(txt_file)):
        print(f"No valid benchmarks found in {txt_file} — skipping CSV and plot.")
        return

    with open(csv_file, "w") as f:
        f.write("method,ms_per_op\n")
        with open(txt_file) as raw:
            for line in raw:
                if "ns/op" in line:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        name = parts[0].removeprefix("Benchmark").removesuffix("-8")
                        try:
                            ms = float(parts[2]) / 1_000_000
                            f.write(f"{name},{ms:.3f}\n")
                        except ValueError:
                            continue

    df = pd.read_csv(csv_file)
    df = df.sort_values(by="method")

    plt.figure(figsize=(10, 6))
    plt.bar(df['method'], df['ms_per_op'])
    plt.xlabel("PRE Function")
    plt.ylabel("Milliseconds per Operation")
    plt.title(f"Benchmark: {config_name}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(eps_file)
    print(f"Saved plot to {eps_file}")

def main():
    parser = argparse.ArgumentParser(description="Run Go benchmarks and generate plots")
    parser.add_argument("test_dir", help="Path to the Go test directory")
    args = parser.parse_args()

    base_dir = Path.cwd()
    output_dir = base_dir / "evaluation" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)

    configs = {
        "default": "",
        "noopt": "all=-N -l",
        "noinline": "all=-l",
        "race": "-race"
    }

    for config_name, flag in configs.items():
        run_benchmark(Path(args.test_dir), config_name, flag, output_dir)

if __name__ == "__main__":
    main()
