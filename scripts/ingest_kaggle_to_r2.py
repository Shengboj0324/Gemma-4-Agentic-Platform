"""Ingest a Kaggle competition's files or a Kaggle dataset into R2 by digest.

Each file is downloaded, size-checked against Kaggle's listing, hashed, uploaded
to its content address with readback, and deleted; then one manifest is
committed. Writes listing.json, manifest.json and receipt.json to a new
--output. Uses the local Kaggle credential; it is never copied anywhere.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, validate_manifest
from zenithsync.kaggle_ingest import Journal, ingest, ingest_zip, normalise_listing
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client


def kaggle_api():
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api


def list_files(api, *, competition=None, dataset=None):
    rows, token = [], None
    while True:
        if competition:
            page = api.competition_list_files(competition, page_token=token, page_size=200)
        else:
            page = api.dataset_list_files(dataset, page_token=token, page_size=200)
        rows.extend((f.name, int(f.total_bytes), str(f.creation_date)) for f in page.files)
        token = page.next_page_token
        if not token:
            return rows


REDIRECTS = (301, 302, 303, 307, 308)


def redirect_target(session, prepared, settings):
    """Send `prepared` without following redirects or reading the body; return Location."""
    settings = {**settings, 'stream': True}
    response = session.send(prepared, allow_redirects=False, timeout=60, **settings)
    try:
        location = response.headers.get('Location')
        if response.status_code not in REDIRECTS or not location:
            raise ValueError(f'Expected a redirect to the archive, got HTTP {response.status_code}')
        return location
    finally:
        response.close()


def bulk_url(api, competition):
    """One API call: the signed URL of the archive of every competition file.

    kagglesdk's `download_data_files` follows the redirect without streaming, so
    it reads the whole archive (22 GB here) into memory before returning. This
    sends the same request but stops at the redirect.
    """
    from kagglesdk.competitions.types.competition_api_service import ApiDownloadDataFilesRequest
    with api.build_kaggle_client() as kaggle:
        http = kaggle.competitions.competition_api_client._client
        http._init_session()
        request = ApiDownloadDataFilesRequest()
        request.competition_name = competition
        prepared = http._prepare_request('competitions.CompetitionApiService', 'ApiDownloadDataFiles', request)
        settings = http._session.merge_environment_settings(prepared.url, {}, None, None, None)
        return redirect_target(http._session, prepared, settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--competition')
    source.add_argument('--dataset')
    parser.add_argument('--include', action='append', default=[],
                        help='Only paths starting with this prefix (repeatable)')
    parser.add_argument('--exclude', action='append', default=[],
                        help='Drop paths starting with this prefix (repeatable)')
    parser.add_argument('--files-from', type=Path,
                        help='Only these exact listed paths, one per line; all must exist')
    parser.add_argument('--revision', required=True)
    parser.add_argument('--bulk', action='store_true',
                        help='One API call: read the all-files archive by HTTP range (competitions only)')
    parser.add_argument('--journal', type=Path,
                        help='Resume record of files already published; reruns skip them')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    api = kaggle_api()
    listed = list_files(api, competition=args.competition, dataset=args.dataset)
    selected = [row for row in listed
                if (not args.include or any(row[0].startswith(p) for p in args.include))
                and not any(row[0].startswith(p) for p in args.exclude)]
    if args.files_from:
        wanted = {line.strip() for line in args.files_from.read_text().splitlines() if line.strip()}
        missing = wanted - {row[0] for row in selected}
        if missing:
            raise ValueError(f'Requested paths not in the listing: {sorted(missing)[:5]}')
        selected = [row for row in selected if row[0] in wanted]
    listing = normalise_listing([(name, size) for name, size, _ in selected])
    client, bucket, connection = build_client(env_file=args.env_file,
                                              max_concurrency=4, max_pool_connections=4 * args.workers + 4)
    store = ArtifactStore(client, bucket, verify_once_per_run=True)

    def fetch(path, directory):
        if args.competition:
            api.competition_download_file(args.competition, path, path=str(directory), quiet=True)
        else:
            api.dataset_download_file(args.dataset, path, path=str(directory), quiet=True)

    origin = (f'https://www.kaggle.com/competitions/{args.competition}' if args.competition
              else f'https://www.kaggle.com/datasets/{args.dataset}')
    started = datetime.now(timezone.utc).isoformat()
    journal = Journal(args.journal) if args.journal else None
    with tempfile.TemporaryDirectory(prefix='kaggle-ingest-') as scratch:
        if args.bulk:
            if not args.competition or journal is None:
                raise ValueError('--bulk needs --competition and --journal')
            url = bulk_url(api, args.competition)

            def open_archive():
                import zipfile
                from zenithsync.remote_zip import HTTPRangeReader
                return zipfile.ZipFile(HTTPRangeReader(url))
            records, uploaded = ingest_zip(listing, open_archive, store, Path(scratch),
                                           journal=journal, workers=args.workers)
        else:
            records, uploaded = ingest(listing, fetch, store, Path(scratch), workers=args.workers)
    manifest = validate_manifest({'schema_version': 1, 'kind': 'harness', 'source': origin,
                                  'revision': args.revision, 'files': records})
    shipment = store.commit_manifest(manifest)
    args.output.mkdir(parents=True)
    (args.output / 'listing.json').write_bytes(canonical_json(
        [{'path': n, 'size_bytes': s, 'created': c} for n, s, c in sorted(selected)]))
    (args.output / 'manifest.json').write_bytes(canonical_json(manifest))
    receipt = {'schema_version': 1, 'status': 'kaggle_source_ingested', 'source': origin,
               'include': args.include, 'exclude': args.exclude, 'bulk_archive': args.bulk,
               'files_from': file_record(args.files_from) if args.files_from else None,
               'files': len(records), 'uploaded_files': uploaded,
               'bytes': sum(r['size_bytes'] for r in records), 'started_utc': started,
               'finished_utc': datetime.now(timezone.utc).isoformat(),
               'manifest': file_record(args.output / 'manifest.json'), 'shipment': shipment,
               'connection': connection, 'verify_once_per_run': True,
               'script': file_record(Path(__file__)),
               'module': file_record(ROOT / 'zenithsync/kaggle_ingest.py'),
               'scope': 'Digests computed at ingest; Kaggle lists sizes only, so these attest '
                        'what was stored, not publisher intent.'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps({k: receipt[k] for k in ('status', 'files', 'uploaded_files', 'bytes')}
                     | {'manifest_sha256': shipment['manifest_sha256']}))


if __name__ == '__main__':
    main()
