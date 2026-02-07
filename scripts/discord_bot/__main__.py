from __future__ import annotations

import argparse
import asyncio
import json
import sys

from discord_bot.client import parse_config, send_notification
from discord_bot.models import EmbedField, NotifyRequest, NotifyResponse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="discord-notify",
        description="Send a rich embed notification to Discord and optionally wait for a reply.",
    )
    parser.add_argument(
        "--config",
        default=".claude/discord-skill.local.md",
        help="Path to config file (default: .claude/discord-skill.local.md)",
    )
    parser.add_argument("--title", default="Notification", help="Embed title")
    parser.add_argument("--message", required=True, help="Embed description/body")
    parser.add_argument(
        "--color",
        default="#5865F2",
        help="Embed color as hex (default: #5865F2)",
    )
    parser.add_argument(
        "--fields",
        default=None,
        help="JSON array of {name, value, inline} objects for embed fields",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Block and wait for a human response",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Wait timeout in seconds (default: 300)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Parse config
    try:
        config = parse_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        resp = NotifyResponse(success=False, error=str(exc))
        print(resp.model_dump_json())
        sys.exit(1)

    # Parse color
    color_str: str = args.color.lstrip("#")
    try:
        color = int(color_str, 16)
    except ValueError:
        resp = NotifyResponse(success=False, error=f"Invalid color: {args.color}")
        print(resp.model_dump_json())
        sys.exit(1)

    # Parse fields
    fields: list[EmbedField] = []
    if args.fields:
        try:
            raw_fields = json.loads(args.fields)
            fields = [EmbedField(**f) for f in raw_fields]
        except (json.JSONDecodeError, TypeError) as exc:
            resp = NotifyResponse(success=False, error=f"Invalid fields JSON: {exc}")
            print(resp.model_dump_json())
            sys.exit(1)

    request = NotifyRequest(
        title=args.title,
        message=args.message,
        color=color,
        fields=fields,
        wait=args.wait,
        timeout=args.timeout,
    )

    # Run the async notification
    try:
        result = asyncio.run(send_notification(config, request))
    except Exception as exc:
        result = NotifyResponse(success=False, error=str(exc))

    print(result.model_dump_json())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
