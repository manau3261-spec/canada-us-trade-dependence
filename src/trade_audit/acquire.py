import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .sources import METADATA_URL, SOURCES, Source

TIMEOUT = (10, 60)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                        encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def validate_zip(path: Path, source: Source) -> dict:
    """Check members and read through each to verify its CRC. Never extract paths."""
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or source.data_member not in names:
            raise ValueError(f"Expected unique archive members including {source.data_member}")
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"CRC failed for {corrupt}")
        return {
            item.filename: {"bytes": item.file_size, "crc32": f"{item.CRC:08x}"}
            for item in archive.infolist()
        }


def session() -> requests.Session:
    client = requests.Session()
    client.headers["User-Agent"] = "CanadaTradeResearch/0.2 (official public dataset acquisition)"
    # Do not retry authentication failures or rate-limited requests.
    retry = Retry(total=1, connect=1, read=0, status=0, other=0,
                  allowed_methods={"GET"}, respect_retry_after_header=False)
    client.mount("https://", HTTPAdapter(max_retries=retry))
    return client


def download(client: requests.Session, root: Path, source: Source) -> dict:
    directory = root / "data" / "raw" / source.pid
    directory.mkdir(parents=True, exist_ok=True)
    start = utc_now()
    temp = None
    try:
        with client.get(source.url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            headers = {
                key: response.headers.get(key)
                for key in ("Last-Modified", "ETag", "Content-Type", "Content-Length")
            }
            with NamedTemporaryFile(dir=directory, suffix=".part", delete=False) as stream:
                temp = Path(stream.name)
                for chunk in response.iter_content(1024 * 1024):
                    stream.write(chunk)
            members = validate_zip(temp, source)
            digest = sha256(temp)
            target = directory / f"{digest}.zip"
            os.replace(temp, target)
            return {
                "pid": source.pid, "table": source.table, "url": source.url,
                "table_url": source.table_url, "resolved_url": response.url,
                "started_at_utc": start, "downloaded_at_utc": utc_now(),
                "status": "downloaded", "http_status": response.status_code,
                "headers": headers, "path": target.relative_to(root).as_posix(),
                "bytes": target.stat().st_size, "sha256": digest, "members": members,
            }
    except (requests.RequestException, OSError, BadZipFile, ValueError) as error:
        response = getattr(error, "response", None)
        return {
            "pid": source.pid, "table": source.table, "url": source.url,
            "table_url": source.table_url, "started_at_utc": start,
            "finished_at_utc": utc_now(), "status": "failed",
            "http_status": response.status_code if response is not None else None,
            "error": str(error),
        }
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def cube_metadata(client: requests.Session, root: Path, source_ids: list[str]) -> tuple[dict, dict]:
    result = {"url": METADATA_URL, "retrieved_at_utc": utc_now(), "status": "failed"}
    try:
        response = client.post(METADATA_URL, json=[{"productId": int(pid)} for pid in source_ids],
                               timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Expected list of WDS responses")
        by_pid = {
            str(item["object"]["productId"]): item["object"]
            for item in payload if item.get("status") == "SUCCESS"
            and isinstance(item.get("object"), dict) and "productId" in item["object"]
        }
        date_fields = ("productId", "cubeStartDate", "cubeEndDate", "releaseTime",
                       "correctionId", "correctionDate", "correctionNoteEn", "correctionNoteFr",
                       "frequencyCode", "archived")
        # Preserve the exact WDS response with its digest as evidence.
        digest = hashlib.sha256(response.content).hexdigest()
        target = root / "data" / "raw" / f"wds-metadata-{digest}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=target.parent, suffix=".part", delete=False) as stream:
            temp = Path(stream.name)
        try:
            temp.write_bytes(response.content)
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)
        result.update(status="downloaded", path=target.relative_to(root).as_posix(),
                      sha256=digest, http_status=response.status_code,
                      retrieved_at_utc=utc_now())
        return result, {pid: {key: record[key] for key in date_fields if key in record}
                        for pid, record in by_pid.items()}
    except (requests.RequestException, OSError, ValueError, TypeError, KeyError) as error:
        result["error"] = str(error)
        return result, {}


def acquire(root: Path) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    manifest = root / "data" / "provenance" / f"acquisition-{run_id}.json"
    record = {"schema_version": 1, "run_id": run_id, "started_at_utc": utc_now(), "sources": []}
    rate_limited = False
    with session() as client:
        for source in SOURCES:
            if rate_limited:
                item = {"pid": source.pid, "table": source.table, "url": source.url,
                        "table_url": source.table_url, "status": "skipped",
                        "error": "Remaining same-host requests deferred after HTTP 429"}
            else:
                item = download(client, root, source)
                rate_limited = item.get("http_status") == 429
            record["sources"].append(item)
            write_json(manifest, record)
            print(f"{source.table} {item['status']}", flush=True)
        if rate_limited:
            metadata, by_pid = {"url": METADATA_URL, "status": "skipped",
                                "error": "Same-host requests deferred after HTTP 429"}, {}
        else:
            metadata, by_pid = cube_metadata(client, root, [source.pid for source in SOURCES])
        record["wds_metadata"] = metadata
        for item in record["sources"]:
            item["publisher_metadata"] = by_pid.get(item["pid"], {})
        record["finished_at_utc"] = utc_now()
        write_json(manifest, record)
    return manifest
