import sys
import random as rd
from datetime import datetime
from typing import Dict, Any
from mazegen.generator import MazeGenerator


def parse_config(filename: str) -> Dict[str, Any]:
    """Parses the configuration file and returns a dictionary of values."""
    config: Dict[str, Any] = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

        required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                    "PERFECT"]
        for r in required:
            if r not in config:
                print(f"Error: Mandatory key '{r}' is missing in config.")
                sys.exit(1)
        return config

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while reading config: {e}")
        sys.exit(1)


def sanitize_config(raw_config: Dict[str, str]) -> Dict[str, Any]:
    """Validates and converts raw config into appropriate Python types."""
    try:
        clean = {}
        clean["WIDTH"] = int(raw_config["WIDTH"])
        clean["HEIGHT"] = int(raw_config["HEIGHT"])

        entry_coords = raw_config["ENTRY"].split(',')
        clean["ENTRY"] = (int(entry_coords[0]), int(entry_coords[1]))

        exit_coords = raw_config["EXIT"].split(',')
        clean["EXIT"] = (int(exit_coords[0]), int(exit_coords[1]))

        clean["OUTPUT_FILE"] = raw_config["OUTPUT_FILE"]
        clean["PERFECT"] = raw_config["PERFECT"].lower() == "true"

        # Boundary Validation
        w, h = clean["WIDTH"], clean["HEIGHT"]
        en_x, en_y = clean["ENTRY"]
        ex_x, ex_y = clean["EXIT"]

        if not (0 <= en_x < w and 0 <= en_y < h):
            print(f"Error: ENTRY {clean['ENTRY']} is out of bounds.")
            sys.exit(1)

        if not (0 <= ex_x < w and 0 <= ex_y < h):
            print(f"Error: EXIT {clean['EXIT']} is out of bounds.")
            sys.exit(1)

        return clean
    except (ValueError, IndexError):
        print("Error: Invalid data format in config file.")
        sys.exit(1)


def main() -> None:
    """Main entry point for the maze generator package."""
    if len(sys.argv) != 2:
        print("\nUsage: a-maze-ing config.txt")
        sys.exit(1)

    config_data = parse_config(sys.argv[1])
    clean_config = sanitize_config(config_data)
    gen_seed = rd.randint(0, 999999)

    mg = MazeGenerator(
        clean_config["WIDTH"],
        clean_config["HEIGHT"],
        gen_seed
    )

    mg.generate(clean_config["PERFECT"])
    path = mg.solve(clean_config["ENTRY"], clean_config["EXIT"])

    mg.export_to_file(
        clean_config["OUTPUT_FILE"],
        clean_config["ENTRY"],
        clean_config["EXIT"],
        path
    )

    try:
        with open("seed_logs.txt", "a") as log:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(
                f"[{ts}] Seed: {mg.seed} | Size: {mg.width}x{mg.height}\n"
            )
    except Exception as e:
        print(f"Warning: Could not write to seed_logs.txt: {e}")

    print(f"\nMaze generated with Seed: {mg.seed}")
    print(f"Output: {clean_config['OUTPUT_FILE']}")


if __name__ == "__main__":
    main()
