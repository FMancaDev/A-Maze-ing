import sys
import random as rd
from datetime import datetime
from mazegen.generator import MazeGenerator


def parse_config(filename):
    """Parses and validates the maze configuration file robustly."""
    conf = {}
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = [x.strip() for x in line.split("=", 1)]
                if k in conf:
                    sys.exit(f"\nError: Duplicate key '{k}'")
                conf[k] = v

        for r in required:
            if r not in conf:
                sys.exit(f"\nError: Missing mandatory key '{r}'")

        # converte e valida WIDTH e HEIGHT
        try:
            w = int(conf["WIDTH"])
            h = int(conf["HEIGHT"])
        except ValueError:
            sys.exit("\nError: WIDTH and HEIGHT must be integers")

        if w < 1 or h < 1:
            sys.exit("\nError: WIDTH and HEIGHT must be positive integers")
        elif w < 3 or h < 3:
            sys.exit("\nError: Minimum dimensions are 3x3")

        for key_name in ["ENTRY", "EXIT"]:
            parts = conf[key_name].split(",")
            if len(parts) != 2:
                sys.exit(f"\nError: {key_name} must have exactly X,Y")
            try:
                coords = tuple(int(x.strip()) for x in parts)
            except ValueError:
                sys.exit(f"\nError: {key_name} coordinates must be integers")
            conf[key_name] = coords

        en = conf["ENTRY"]
        ex = conf["EXIT"]

        for coord, name in [(en, "ENTRY"), (ex, "EXIT")]:
            if not (0 <= coord[0] < w and 0 <= coord[1] < h):
                sys.exit(
                    f"\nError: {name} {coord} is outside maze bounds ({w}x{h})"
                )
        if en == ex:
            sys.exit("\nError: ENTRY and EXIT cannot be the same")

        # valida PERFECT (booleano)
        perfect_val = conf["PERFECT"].strip().lower()
        if perfect_val == "true":
            perfect = True
        elif perfect_val == "false":
            perfect = False
        else:
            sys.exit("\nError: PERFECT must be True or False")

        return w, h, en, ex, conf["OUTPUT_FILE"], perfect

    except Exception as e:
        sys.exit(f"\nConfig Error: {e}")


def main():
    """Main entry point for the a-maze-ing package."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.exit("\nUsage: a-maze-ing config.txt [seed]")

    w, h, en, ex, out, perfect = parse_config(sys.argv[1])

    # USER
    if len(sys.argv) == 3:
        try:
            seed = int(sys.argv[2])
        except ValueError:
            sys.exit("\nError: Seed must be an integer.")
    else:
        seed = rd.randint(0, 999999)

    mg = MazeGenerator(w, h, en, ex, seed)
    mg.generate(perfect)

    path = mg.solve(en, ex)
    if not path:
        print("\nWarning: No path found (Check if ENTRY/EXIT is blocked)")

    mg.export_to_file(out, en, ex, path)

    try:
        with open("seed_logs.txt", "a") as log:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{ts}] Seed: {seed} | Size: {w}x{h} | File: {out}\n")
    except Exception:
        pass

    print(f"\nMaze generated! Seed: {seed}")
    print(f"Output saved to: {out}")


if __name__ == "__main__":
    main()
