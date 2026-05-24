from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Mapping, Optional

from all_in_one.cli.auth import CookieResolution
from all_in_one.cli.errors import CLIError, ErrorCategory
from all_in_one.platforms.discovery import Endpoint


AUTH_NAMES = {"auth", "auth_", "cookie", "cookies", "cookies_str"}


@dataclass
class SimpleDouyinAuth:
    cookie_str: str
    cookie: Dict[str, str]
    msToken: str


def invoke_endpoint(
    endpoint: Endpoint,
    arguments: Mapping[str, Any],
    cookie: Optional[CookieResolution] = None,
    proxy: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Any:
    target = _load_target(endpoint)
    signature = inspect.signature(target)
    kwargs: Dict[str, Any] = {}

    for name, parameter in signature.parameters.items():
        if name in {"self", "cls"}:
            continue
        if name in AUTH_NAMES:
            if cookie is None:
                raise CLIError(
                    ErrorCategory.AUTH_MISSING,
                    (
                        f"{endpoint.platform} command requires cookies. "
                        f"Run `aione auth {endpoint.platform} set-cookie --cookie \"<cookie>\"` "
                        "or pass --cookies."
                    ),
                    platform=endpoint.platform,
                )
            kwargs[name] = _auth_argument(endpoint, name, cookie)
            continue
        if name == "proxies":
            if proxy:
                kwargs[name] = {"http": proxy, "https": proxy}
            continue
        if name == "timeout":
            if timeout is not None:
                kwargs[name] = timeout
            continue
        if name in arguments:
            kwargs[name] = _coerce(arguments[name], parameter)

    repo_root = _repo_root_for(endpoint.source_file)
    saved_cwd = os.getcwd()
    if repo_root:
        os.chdir(str(repo_root))
    try:
        return target(**kwargs)
    except CLIError:
        raise
    except Exception as exc:
        raise CLIError(
            ErrorCategory.UPSTREAM_ERROR,
            f"{endpoint.platform} {endpoint.resource} {endpoint.action}: {type(exc).__name__}: {exc}",
            platform=endpoint.platform,
        ) from exc
    finally:
        os.chdir(saved_cwd)


def _auth_argument(endpoint: Endpoint, parameter_name: str, cookie: CookieResolution):
    if endpoint.platform == "douyin" and parameter_name in {"auth", "auth_"}:
        return _douyin_auth(endpoint, cookie.value)
    return cookie.value


def _douyin_auth(endpoint: Endpoint, cookie_value: str):
    repo_root = _repo_root_for(endpoint.source_file)
    repo_str = str(repo_root.resolve()) if repo_root else None
    inserted = False
    if repo_str and repo_str not in sys.path:
        sys.path.insert(0, repo_str)
        inserted = True
    try:
        from builder.auth import DouyinAuth

        return DouyinAuth(cookie_value)
    except Exception:
        parsed = _parse_cookie(cookie_value)
        return SimpleDouyinAuth(
            cookie_str=cookie_value,
            cookie=parsed,
            msToken=parsed.get("msToken", ""),
        )
    finally:
        if inserted and repo_str:
            try:
                sys.path.remove(repo_str)
            except ValueError:
                pass


def _parse_cookie(cookie_value: str) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    for part in cookie_value.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        if key:
            parsed[key] = value.strip()
    return parsed


def _load_target(endpoint: Endpoint):
    module = _load_module(endpoint.source_file)
    if endpoint.class_name:
        owner = getattr(module, endpoint.class_name)
        try:
            instance = owner()
            return getattr(instance, endpoint.function_name)
        except TypeError:
            return getattr(owner, endpoint.function_name)
    return getattr(module, endpoint.function_name)


def _load_module(source_file: Path) -> ModuleType:
    source = Path(source_file).resolve()
    module_name = f"socialctl_upstream_{abs(hash(source))}"
    repo_root = _repo_root_for(source)
    inserted = False
    repo_str = str(repo_root.resolve()) if repo_root else None
    if repo_str and repo_str not in sys.path:
        sys.path.insert(0, repo_str)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, source)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import {source}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as exc:
        raise CLIError(
            ErrorCategory.UPSTREAM_ERROR,
            f"Failed to import upstream module {source}: {exc}",
        ) from exc
    finally:
        if inserted and repo_str:
            try:
                sys.path.remove(repo_str)
            except ValueError:
                pass


def _repo_root_for(source_file: Path) -> Optional[Path]:
    source = Path(source_file).resolve()
    for parent in source.parents:
        if parent.name in {"Spider_XHS", "WeiboApis", "DouYin_Spider"}:
            return parent
    return source.parent


def _coerce(value: Any, parameter: inspect.Parameter) -> Any:
    annotation = parameter.annotation
    if annotation in {int, "int"}:
        return int(value)
    if annotation in {float, "float"}:
        return float(value)
    if annotation in {bool, "bool"}:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    default = parameter.default
    if default is not inspect._empty and default is not None:
        if isinstance(default, int) and not isinstance(default, bool):
            return int(value)
        if isinstance(default, float):
            return float(value)
        if isinstance(default, bool):
            return str(value).strip().lower() in {"1", "true", "yes", "on"}
    return value
