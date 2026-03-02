import sys
import random as rd
from datetime import datetime
from mazegen.generator import MazeGenerator


def parse_config(filename):
    """Parses the configuration file and returns validated values."""
    conf = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                if "=" not in line or line.strip().startswith("#"):
                    continue

                k, v = [x.strip() for x in line.split("=", 1)]

                if k in conf:
                    sys.exit(f"\nError: Duplicate key '{k}'")

                conf[k] = v

        # Validacao de dados
        w = int(conf["WIDTH"])
        h = int(conf["HEIGHT"])
        en = tuple(map(int, conf["ENTRY"].split(",")))
        ex = tuple(map(int, conf["EXIT"].split(",")))

        if len(en) != 2 or len(ex) != 2:
            sys.exit("Error: ENTRY/EXIT must be X,Y")

        if en == ex:
            sys.exit("\nError: ENTRY and EXIT cannot be the same")

        if conf["PERFECT"].lower() not in ["true", "false"]:
            sys.exit("Error: PERFECT must be True/False")

        return (
            w,
            h,
            en,
            ex,
            conf["OUTPUT_FILE"],
            conf["PERFECT"].lower() == "true",
        )

    except Exception as e:
        sys.exit(f"Config Error: {e}")


def main():
    if len(sys.argv) != 2:
        sys.exit("\nUsage: a-maze-ing config.txt")

    w, h, en, ex, out, perf = parse_config(sys.argv[1])
    seed = rd.randint(0, 999999)

    mg = MazeGenerator(w, h, seed)
    mg.generate(perf)

    # O solver verifica se o path não estão presas no '42'
    path = mg.solve(en, ex)
    if not path:
        print(
            "\nWarning: No shortest path found "
            "(check if ENTRY/EXIT is inside '42')"
        )

    mg.export_to_file(out, en, ex, path)

    with open("seed_logs.txt", "a") as log:
        log.write(
            f"[{datetime.now().isoformat()}] "
            f"Seed: {seed} | Size: {w}x{h}\n"
        )

    print(f"\nMaze generated! Seed: {seed}")


if __name__ == "__main__":
    main()
