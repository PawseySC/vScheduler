import argparse
from vscheduler.lib.config import Config
config = Config()

def main():
    """
    help module using argparse package
    argparse features listed on https://code.google.com/archive/p/argparse/:
    - handling positional arguments
    - supporting sub-commands
    - allowing alternative option prefixes like + and /
    - handling zero-or-more and one-or-more style arguments
    - producing more informative usage messages
    - providing a much simpler interface for custom types and actions
    """
    parser = argparse.ArgumentParser(
        description="Session Management and Reporting Platform [Vscheduler] - Pawsey Supercomputing Centre",
        epilog="Example: vreport -u <user> -n <node> -d <YYYY-MM-DD> <YYYY-MM-DD> --verbose"
    )

    # Positional arguments
    # parser.add_argument("input", help="Path to input image file")
    # parser.add_argument("output", help="Path to output image file")

    # Create subparsers for subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Subcommand: vset ---
    vset_parser = subparsers.add_parser("vset", help="set node status")
    # resize_parser.add_argument("input", help="Input image file")
    # resize_parser.add_argument("output", help="Output image file")
    vset_parser.add_argument("-status", type=str, required=True, help="New status")

    # --- Subcommand: vexcept ---
    vexcept_parser = subparsers.add_parser("vexcept", help="set wall time different to others")
    # resize_parser.add_argument("input", help="Input image file")
    # resize_parser.add_argument("output", help="Output image file")
    vexcept_parser.add_argument("-mode", type=str, required=True, help="New wall time")

    # Optional arguments
    parser.add_argument("-u", type=str, metavar="USERNAME", help="Optional: no username will run across all users")
    parser.add_argument("-n", type=str, metavar="NODE", help="Optional: no node name will run across all nodes")
    parser.add_argument("-d", type=str, metavar="DATE", help="date in YYYY-MM-DD format followed by date1 date2. Having only one date will search from first db record. No date will serach across all records")
    # parser.add_argument("--resize", type=int, help="Resize image to specified width (height scaled)")
    # parser.add_argument("--format", choices=["png", "jpg", "bmp"], help="Output format (default is same as input)")
    # parser.add_argument("--status", metavar="STATUS", choices=["up", "down", "maint", "dev"], help="vset node status: up|down|maint|dev ex: vset -n <node> up -v")
    # parser.add_argument("--mode", metavar="MODE", choices=["create", "delete", "status", "list", "activate", "deactivate"], help="vexcept mode: create|delete|status|list|activate|deactivate ex: vexcept activate -u <user> -t 336 OR vexcept list -v")
    parser.add_argument("--verbose", action="store_true", help="Print detailed logs during processing")
    parser.add_argument("--version", action="version", version=f"vscheduler v{config.get('version.v')}")

    # Show help message with -h or --help automatically
    args = parser.parse_args()

    # Example usage
    if args.verbose:
        print("Starting image processing...")
        print(f"Input file: {args.input}")
        print(f"Output file: {args.output}")
        if args.resize:
            print(f"Resizing to width: {args.resize}")
        if args.format:
            print(f"Output format: {args.format}")
        print("Processing complete!")

if __name__ == "__main__":
    main()
