import sys
from typing import Dict, Any
from mazegen.generator import MazeGenerator


def parse_config(filename: str) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                # ignora linhas vazias e omentarios
                if not line or line.startswith('#'):
                    continue

                # divide a linha em chave e valor
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

        # validar chaves
        required = ["WIDTH", "HEIGHT", "ENTRY",
                    "EXIT", "OUTPUT_FILE", "PERFECT"]
        for r in required:
            if r not in config:
                print(f"Erro: Required key {r} missing.")
                sys.exit(1)

        return config

    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        sys.exit(1)
    except Exception as erro:
        print(f"Unexpected error while reading config: {erro}")
        sys.exit(1)


def sanitize_config(raw_config: Dict[str, str]) -> Dict[str, Any]:
    try:
        clean = {}
        clean["WIDTH"] = int(raw_config["WIDTH"])
        clean["HEIGHT"] = int(raw_config["HEIGHT"])

        # Converte a string "0,0" numa tupla (0, 0)
        entry_coords = raw_config["ENTRY"].split(',')
        clean["ENTRY"] = (int(entry_coords[0]), int(entry_coords[1]))

        exit_coords = raw_config["EXIT"].split(',')
        clean["EXIT"] = (int(exit_coords[0]), int(exit_coords[1]))

        clean["OUTPUT_FILE"] = raw_config["OUTPUT_FILE"]

        # converte a string "True e false" num booleano real
        clean["PERFECT"] = raw_config["PERFECT"].lower() == "true"

        clean["SEED"] = int(raw_config.get("SEED", 42))

        return clean
    except (ValueError, IndexError):
        print(
            "\nERROR: Invalid data format in config.txt"
            " (ex. WIDTH must be a number)"
        )
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    config_data = parse_config(sys.argv[1])
    clean_config = sanitize_config(config_data)

    mg = MazeGenerator(
        clean_config["WIDTH"],
        clean_config["HEIGHT"],
        clean_config["SEED"]
    )

    mg.generate(clean_config["PERFECT"])

    path = mg.solve(clean_config["ENTRY"], clean_config["EXIT"])

    mg.export_to_file(
        clean_config["OUTPUT_FILE"],
        clean_config["ENTRY"],
        clean_config["EXIT"],
        path
    )

    print(
        f"\nMaze successfully generated and exported to"
        f" {clean_config['OUTPUT_FILE']}"
    )
