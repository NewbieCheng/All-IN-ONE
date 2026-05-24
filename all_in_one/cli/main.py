from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional

from all_in_one.cli.auth import CookieStore, resolve_cookie
from all_in_one.cli.errors import CLIError, ErrorCategory, error_payload
from all_in_one.cli.output import write_output, verbose_log
from all_in_one.platforms.invoke import invoke_endpoint
from all_in_one.platforms.registry import build_registry
from platformdirs import user_data_dir

UPSTREAM_REPOS = {
    "Spider_XHS": "https://github.com/cv-cat/Spider_XHS.git",
    "WeiboApis": "https://github.com/cv-cat/WeiboApis.git",
    "DouYin_Spider": "https://github.com/cv-cat/DouYin_Spider.git",
}


AUTH_PARAMETERS = {
    "auth",
    "auth_",
    "cookie",
    "cookies",
    "cookies_str",
    "proxies",
}


def _default_upstream_root() -> Path:
    local = Path("upstreams")
    if local.is_dir():
        return local
    return Path(user_data_dir("aione", appauthor=False)) / "upstreams"


def main(
    argv: Optional[Iterable[str]] = None,
    store: Optional[CookieStore] = None,
    upstream_root: Optional[Path] = None,
) -> int:
    if upstream_root is None:
        upstream_root = _default_upstream_root()
    parser = build_parser(upstream_root)
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        if not hasattr(args, "handler"):
            parser.print_help()
            return 0
        result = args.handler(args, store or CookieStore())
        if result is not None:
            print(write_output(result, output=getattr(args, "output", "json"), path=getattr(args, "path", None)))
        return 0
    except CLIError as error:
        print(write_output(error_payload(error), output="json"), file=sys.stderr)
        return error.exit_code
    except ValueError as error:
        wrapped = CLIError(ErrorCategory.VALIDATION_ERROR, str(error))
        print(write_output(error_payload(wrapped), output="json"), file=sys.stderr)
        return 1
    except SystemExit as exit_error:
        return int(exit_error.code or 0)


def build_parser(upstream_root: Optional[Path] = None) -> argparse.ArgumentParser:
    if upstream_root is None:
        upstream_root = _default_upstream_root()
    parser = argparse.ArgumentParser(prog="aione")
    subparsers = parser.add_subparsers(dest="namespace")

    _add_auth_parser(subparsers)
    _add_setup_parser(subparsers)
    registry = build_registry(upstream_root)
    if not registry.endpoints and not upstream_root.is_dir():
        parser.epilog = (
            "No upstream repos found. Run `aione setup` first to clone them."
        )
    for platform in ("xhs", "weibo", "douyin"):
        platform_parser = subparsers.add_parser(platform)
        resource_parsers = platform_parser.add_subparsers(dest="resource")
        platform_endpoints = [
            endpoint for endpoint in registry.endpoints if endpoint.platform == platform
        ]
        for resource in sorted({endpoint.resource for endpoint in platform_endpoints}):
            resource_parser = resource_parsers.add_parser(resource)
            action_parsers = resource_parser.add_subparsers(dest="action")
            for endpoint in sorted(
                [item for item in platform_endpoints if item.resource == resource],
                key=lambda item: item.action,
            ):
                desc = _endpoint_description(endpoint)
                action_parser = action_parsers.add_parser(
                    endpoint.action,
                    description=desc,
                    help=endpoint.docstring or _short_help(endpoint),
                )
                action_parser.set_defaults(handler=_handle_endpoint, endpoint=endpoint)
                _add_common_endpoint_options(action_parser)
                for param in endpoint.parameters:
                    if param in AUTH_PARAMETERS:
                        continue
                    option = f"--{_option_name(param)}"
                    if option not in {action.option_strings[0] for action in action_parser._actions if action.option_strings}:
                        action_parser.add_argument(
                            option, dest=param, help=_param_help(param),
                        )
    return parser


def _add_auth_parser(subparsers) -> None:
    auth_parser = subparsers.add_parser("auth")
    platform_parsers = auth_parser.add_subparsers(dest="platform")
    for platform in ("xhs", "weibo", "douyin"):
        platform_parser = platform_parsers.add_parser(platform)
        command_parsers = platform_parser.add_subparsers(dest="auth_action")

        set_cookie = command_parsers.add_parser("set-cookie")
        set_cookie.add_argument("--profile", default="default")
        set_cookie.add_argument("--cookie")
        set_cookie.add_argument("--cookie-file", type=Path)
        set_cookie.set_defaults(handler=_handle_set_cookie, platform=platform)

        status = command_parsers.add_parser("status")
        status.add_argument("--profile", default="default")
        status.set_defaults(handler=_handle_auth_status, platform=platform)

        clear = command_parsers.add_parser("clear-cookie")
        clear.add_argument("--profile", default="default")
        clear.set_defaults(handler=_handle_clear_cookie, platform=platform)


def _add_common_endpoint_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cookies", help="cookie string (overrides saved/env)")
    parser.add_argument("--output", choices=("json", "pretty", "file"), default="json", help="output format (default: json)")
    parser.add_argument("--path", type=Path, help="file path for --output file")
    parser.add_argument("--proxy", help="proxy URL (http/https)")
    parser.add_argument("--timeout", type=float, help="request timeout in seconds")
    parser.add_argument("--verbose", action="store_true", help="print debug info to stderr")
    parser.add_argument("--dry-run", action="store_true", help="show command mapping without calling API")


def _add_setup_parser(subparsers) -> None:
    default_root = Path(user_data_dir("aione", appauthor=False)) / "upstreams"
    setup_parser = subparsers.add_parser(
        "setup", description="Clone upstream repos and install npm dependencies."
    )
    setup_parser.add_argument(
        "--upstream-root", type=Path, default=default_root,
        help=f"where to store upstream repos (default: {default_root})",
    )
    setup_parser.set_defaults(handler=_handle_setup)


def _handle_setup(args, store: CookieStore):
    root = args.upstream_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    results = []

    for name, url in UPSTREAM_REPOS.items():
        repo_dir = root / name
        if repo_dir.exists():
            print(f"[setup] {name}: already exists, skipping clone")
        else:
            print(f"[setup] {name}: cloning from {url} ...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, str(repo_dir)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"[setup] {name}: cloned successfully")
            except FileNotFoundError:
                print(f"[setup] {name}: FAILED - git not found")
                results.append({"repo": name, "status": "failed", "reason": "git not found"})
                continue
            except subprocess.CalledProcessError as exc:
                print(f"[setup] {name}: FAILED - {exc.stderr.strip()}")
                results.append({"repo": name, "status": "failed", "reason": exc.stderr.strip()})
                continue

        pkg_json = repo_dir / "package.json"
        node_modules = repo_dir / "node_modules"
        if pkg_json.exists() and not node_modules.exists():
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            if shutil.which(npm_cmd):
                print(f"[setup] {name}: running npm install ...")
                try:
                    subprocess.run(
                        [npm_cmd, "install"],
                        cwd=str(repo_dir),
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print(f"[setup] {name}: npm install done")
                except subprocess.CalledProcessError as exc:
                    npm_err = exc.stderr.strip().split("\n")[0] if exc.stderr else "unknown"
                    print(f"[setup] {name}: npm install had issues: {npm_err}")
                    print(f"[setup] {name}: try running `cd {repo_dir} && npm install` manually")
            else:
                print(f"[setup] {name}: npm not found, skip npm install")
                print(f"[setup] {name}: install Node.js then run `cd {repo_dir} && npm install`")
        elif pkg_json.exists() and node_modules.exists():
            print(f"[setup] {name}: node_modules already exists")

        results.append({"repo": name, "status": "ok", "path": str(repo_dir)})

    print(f"\n[setup] Done. {len([r for r in results if r['status']=='ok'])}/{len(UPSTREAM_REPOS)} repos ready.")
    print("[setup] Next: run `aione auth <platform> set-cookie --cookie \"<cookie>\"` to configure auth.")
    return None


def _handle_set_cookie(args, store: CookieStore):
    cookie = args.cookie
    if args.cookie_file:
        if not args.cookie_file.exists():
            raise CLIError(
                ErrorCategory.VALIDATION_ERROR,
                (
                    f"Cookie file not found: {args.cookie_file}. "
                    "Pass an absolute path or put the file in the current working directory."
                ),
                platform=args.platform,
            )
        try:
            cookie = args.cookie_file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise CLIError(
                ErrorCategory.VALIDATION_ERROR,
                f"Could not read cookie file {args.cookie_file}: {exc}",
                platform=args.platform,
            ) from exc
    if not cookie:
        raise CLIError(
            ErrorCategory.VALIDATION_ERROR,
            "--cookie or --cookie-file is required",
            platform=args.platform,
        )
    path = store.save_cookie(
        args.platform, cookie, profile=args.profile, source="cli"
    )
    return {
        "platform": args.platform,
        "profile": args.profile,
        "saved": True,
        "path": str(path),
    }


def _handle_auth_status(args, store: CookieStore):
    resolved = resolve_cookie(args.platform, profile=args.profile, store=store)
    payload = {
        "platform": args.platform,
        "profile": args.profile,
        "configured": resolved is not None,
    }
    if resolved is not None:
        payload["source"] = resolved.source
    return payload


def _handle_clear_cookie(args, store: CookieStore):
    return {
        "platform": args.platform,
        "profile": args.profile,
        "cleared": store.clear_cookie(args.platform, profile=args.profile),
    }


def _handle_endpoint(args, store: CookieStore):
    endpoint = args.endpoint
    is_verbose = args.verbose
    arguments = {}
    for param in endpoint.parameters:
        if param in AUTH_PARAMETERS:
            continue
        value = getattr(args, param, None)
        if value is not None:
            arguments[param] = value

    verbose_log(
        f"target: {endpoint.module_name}:{endpoint.class_name or ''}.{endpoint.function_name}",
        is_verbose,
    )
    verbose_log(f"auth_profile: {endpoint.auth_profile}", is_verbose)

    if args.dry_run:
        return {
            "dry_run": True,
            "platform": endpoint.platform,
            "resource": endpoint.resource,
            "action": endpoint.action,
            "auth_profile": endpoint.auth_profile,
            "target": {
                "module": endpoint.module_name,
                "class": endpoint.class_name,
                "function": endpoint.function_name,
                "source": str(endpoint.source_file),
            },
            "arguments": arguments,
        }

    cookie = resolve_cookie(
        endpoint.platform,
        profile=endpoint.auth_profile,
        cli_cookie=args.cookies,
        store=store,
    )
    if _requires_auth(endpoint) and cookie is None:
        raise CLIError(
            ErrorCategory.AUTH_MISSING,
            (
                f"{endpoint.platform} command requires cookies. "
                f"Run `aione auth {endpoint.platform} set-cookie --profile {endpoint.auth_profile} --cookie \"<cookie>\"` "
                "or retry this command with --cookies."
            ),
            platform=endpoint.platform,
            auth_profile=endpoint.auth_profile,
        )

    if cookie:
        verbose_log(f"cookie_source: {cookie.source}, profile: {cookie.profile}", is_verbose)
    verbose_log(f"arguments: {arguments}", is_verbose)
    if args.proxy:
        verbose_log(f"proxy: {args.proxy}", is_verbose)
    if args.timeout:
        verbose_log(f"timeout: {args.timeout}s", is_verbose)

    result = invoke_endpoint(
        endpoint,
        arguments=arguments,
        cookie=cookie,
        proxy=args.proxy,
        timeout=args.timeout,
    )

    result_type = type(result).__name__
    if isinstance(result, dict):
        verbose_log(f"response: dict with {len(result)} keys", is_verbose)
    elif isinstance(result, list):
        verbose_log(f"response: list with {len(result)} items", is_verbose)
    else:
        verbose_log(f"response: {result_type}", is_verbose)

    return result


def _requires_auth(endpoint) -> bool:
    return any(param in {"auth", "auth_", "cookie", "cookies", "cookies_str"} for param in endpoint.parameters)


def _option_name(parameter_name: str) -> str:
    with_boundaries = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", parameter_name)
    return with_boundaries.replace("_", "-").lower()


def _endpoint_description(endpoint) -> str:
    parts = [f"Upstream: {endpoint.target_id}"]
    parts.append(f"Auth profile: {endpoint.auth_profile}")
    if endpoint.docstring:
        parts.insert(0, endpoint.docstring)
    return " | ".join(parts)


def _short_help(endpoint) -> str:
    tokens = endpoint.action.replace("-", " ").split()
    resource = endpoint.resource.replace("-", " ")
    return f"{' '.join(tokens)} ({resource})"


PARAM_HELP = {
    "query": "search keyword",
    "page": "page number (1-based)",
    "url": "content URL",
    "user_id": "user ID",
    "user_url": "user profile URL",
    "note_id": "note ID",
    "cursor": "pagination cursor",
    "max_cursor": "pagination cursor",
    "offset": "pagination offset",
    "num": "number of results to fetch",
    "require_num": "number of results to fetch",
    "count": "number of items per page",
    "limit": "max number of results",
    "sort_type": "sort type (0=default)",
    "sort_type_choice": "sort type (0=default)",
    "publish_time": "publish time filter (0=all)",
    "note_type": "note type filter (0=all)",
    "comment": "comment ID (for inner comments)",
    "content": "text content",
    "aweme_id": "video/aweme ID",
    "room_id": "live room ID",
    "live_id": "live stream ID",
    "sec_id": "encrypted user ID (sec_uid)",
    "keyword": "search keyword",
    "word": "keyword",
    "file": "file path",
    "path_or_file": "file path",
    "media_type": "media type (image/video)",
    "noteInfo": "note data as JSON string",
    "note_info": "note data as JSON string",
    "work_id": "post/work ID",
    "mid": "weibo message ID",
    "category": "content category",
    "digg_type": "like type (1=like, 0=unlike)",
    "action": "action type (1=collect, 0=uncollect)",
    "collect_name": "collection name",
    "collect_id": "collection ID",
    "conversation_id": "DM conversation ID",
    "conversation_short_id": "DM conversation short ID",
    "ticket": "message ticket",
    "to_user_id": "recipient user ID",
    "anchor_id": "live anchor ID",
    "sec_anchor_id": "encrypted anchor ID",
    "reply_id": "reply-to comment ID",
    "profile": "auth profile name",
    "xsec_token": "security token",
    "xsec_source": "security source",
    "video_id": "video ID",
    "file_id": "uploaded file ID",
    "img_url": "image URL",
}


def _param_help(param: str) -> str:
    return PARAM_HELP.get(param, param.replace("_", " "))

