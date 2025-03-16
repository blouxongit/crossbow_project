import argparse

from src.run_experience import run_experience


def entrypoint():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, required=True, help="The path to the configuration file to be used")
    args = parser.parse_args()

    run_experience(args.config)


if __name__ == "__main__":
    entrypoint()
