"""
YASL CLI main entry point.
"""
import argparse
import sys
import logging
from io import StringIO
try:
    from ruamel.yaml import YAML
except ImportError:
    YAML = None
import json

from yasl import TypeDef, gen_enum_from_enumeration, gen_pydantic_type_model, load_and_validate_data_with_lines, load_and_validate_yasl_with_lines

YASL_VERSION = "0.1.0"

class YamlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if YAML is None:
            return f"YAML formatter unavailable: ruamel.yaml not installed. {record.getMessage()}"
        yaml = YAML()
        log_dict = {
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
        }
        stream = StringIO()
        log_list = []
        log_list.append(log_dict)
        yaml.dump(log_list, stream)
        return stream.getvalue().strip()

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
        }
        return json.dumps(log_dict)

def setup_logging(verbose: bool, quiet: bool, logfmt: str):
    logger = logging.getLogger()
    logger.handlers.clear()
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler()
    if logfmt == "json":
        handler.setFormatter(JsonFormatter())
    elif logfmt == "yaml":
        handler.setFormatter(YamlFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

def main():
    parser = argparse.ArgumentParser(
        description="YASL - YAML Advanced Schema Language CLI Tool"
    )
    parser.add_argument(
        "command",
        choices=["init", "check", "package", "import", "eval", "version"],
        help="Command to execute"
    )
    parser.add_argument(
        "param",
        nargs="?",
        help="Parameter for the command (Project name for 'init', YAML file for 'check', URI for 'import', YAML file for 'eval')"
    )
    # Removed --project-name argument; 'param' will be used for project name in 'init'
    parser.add_argument(
        "schema",
        nargs="?",
        help="YASL schema file for the 'eval' command (required for 'eval', ignored otherwise)"
    )
    parser.add_argument(
        "model_name",
        nargs="?",
        help="YASL schema name for the 'eval' command (required for 'eval', ignored otherwise)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except for errors"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--logfmt",
        choices=["text", "json", "yaml"],
        default="text",
        help="Set log output format (text, json, yaml). Default is text."
    )

    args = parser.parse_args()

    if args.verbose and args.quiet:
        print("Cannot use both --quiet and --verbose.", file=sys.stderr)
        sys.exit(1)

    setup_logging(args.verbose, args.quiet, args.logfmt)
    log = logging.getLogger("yasl")

    if args.command == "version":
        log.info(f"YASL version {YASL_VERSION}")
        return
    # project-based commands
    if args.command == "init":
        if not args.param:
            log.error("'init' requires a project name as parameter.")
            sys.exit(1)
        project_name = args.param
        log.info(f"Initializing YASL project: {project_name}")
        # TODO: Implement init logic using project_name
    elif args.command == "check":
        if not args.param:
            log.error("'check' requires a YAML file as parameter.")
            sys.exit(1)
        log.info(f"Checking YAML file: {args.param}")
        # TODO: Implement check logic
    elif args.command == "package":
        if not args.param:
            log.error("'package' requires a YAML file as parameter.")
            sys.exit(1)
        log.info(f"Packaging YAML file: {args.param}")
        # TODO: Implement package logic
    elif args.command == "import":
        if not args.param:
            log.error("'import' requires a URI as parameter.")
            sys.exit(1)
        log.info(f"Importing from URI: {args.param}")
        # TODO: Implement import logic
    # Non-project-based commands
    elif args.command == "eval":
        if not args.param or not args.schema or not args.model_name:
            log.error("'eval' requires a YAML file, a YASL schema file, and a model name as parameters.")
            sys.exit(1)
        log.debug(f"Evaluating YAML file '{args.param}' against schema '{args.schema}' and model '{args.model_name}'")
        # TODO: Implement eval logic
        models = {}
        yasl = load_and_validate_yasl_with_lines(args.schema)
        if yasl.project is not None:
            log.debug(f"Evaluating project: {yasl.project.name}")
        for type_def in yasl.types or []:
            log.debug(f"Evaluating type definition: {type_def.name}")
            model = gen_pydantic_type_model(type_def)
            models[type_def.name] = model
        for enum in yasl.enums or []:
            log.debug(f"Evaluating enum: {enum.name}")
            model = gen_enum_from_enumeration(enum)
        if args.model_name not in models:
            log.error(f"Model '{args.model_name}' not found in schema.")
            sys.exit(1)
        data = load_and_validate_data_with_lines(models[args.model_name], args.param)
    else:
        log.error(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
