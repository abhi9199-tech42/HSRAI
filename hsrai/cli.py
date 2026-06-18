import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def _get_version() -> str:
    try:
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject.exists():
            text = pyproject.read_text()
            for line in text.splitlines():
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception as e:
        logger.debug("Could not read pyproject.toml version: %s", e)
        pass
    return __version__


def cmd_process(args):
    from hsrai.output.models import GeneratedOutput
    from hsrai.system.controller import SystemController

    controller = SystemController()
    output: GeneratedOutput = asyncio.run(controller.process_request(args.query))

    print("Output:")
    print(output.content)
    print()

    if output.trust_certificate:
        cert = output.trust_certificate
        print(f"Trust Certificate: {cert.certificate_id}")
        print(f"  Issuer:      {cert.issuer_id}")
        print(f"  Subject:     {cert.subject_id}")
        print(f"  Score:       {cert.trust_score}")
        print(f"  Timestamp:   {cert.timestamp}")
    else:
        print("Trust Certificate: None")


def cmd_verify(args):
    from hsrai.trust.verifier import TrustManager

    manager = TrustManager()
    for cert in manager.certificate_chain:
        if cert.certificate_id == args.cert:
            valid = manager.verify_certificate(cert)
            print("VALID" if valid else "INVALID")
            return

    print(f"Certificate '{args.cert}' not found.")


def cmd_config(args):
    from hsrai.system.config import SystemConfig

    if args.show:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        config = SystemConfig.from_dict(data) if data else SystemConfig()
        print(f"Config ({CONFIG_PATH}):")
        for k, v in vars(config).items():
            print(f"  {k} = {v!r}")

    elif args.set:
        key, _, value = args.set.partition("=")
        if not value and key:
            print("Error: use --set key=value")
            return

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        data[key] = value

        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Set {key} = {value!r}")
    else:
        print("Usage: hsrai config --show | --set key=value")


def cmd_test(args):
    import os
    test_dirs = []
    for d in ["hsrai/tests/", "urcm/tests/", "isre/tests/"]:
        if os.path.isdir(d):
            test_dirs.append(d)
    if not test_dirs:
        test_dirs = ["hsrai/tests/"]
    result = subprocess.run(
        [sys.executable, "-m", "pytest"] + test_dirs + ["-q"],
    )
    sys.exit(result.returncode)


def cmd_serve(args):
    port = args.port or 8000
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "hsrai.api.server:app", "--port", str(port)],
    )


def cmd_version(args):
    print(f"hsrai {_get_version()}")


def main():
    parser = argparse.ArgumentParser(
        prog="hsrai",
        description="Hybrid Semantic Reasoning AI CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # process
    p_process = subparsers.add_parser("process", help="Process text through the pipeline")
    p_process.add_argument("query", help="Input text to process")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify a trust certificate")
    p_verify.add_argument("--cert", required=True, help="Certificate ID to verify")

    # config
    p_config = subparsers.add_parser("config", help="Manage configuration")
    p_config.add_argument("--show", action="store_true", help="Show current configuration")
    p_config.add_argument("--set", metavar="key=value", help="Set a config value")

    # test
    subparsers.add_parser("test", help="Run the test suite")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start the REST API server")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to listen on")

    # version
    subparsers.add_parser("version", help="Show version info")

    args = parser.parse_args()

    commands = {
        "process": cmd_process,
        "verify": cmd_verify,
        "config": cmd_config,
        "test": cmd_test,
        "serve": cmd_serve,
        "version": cmd_version,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
