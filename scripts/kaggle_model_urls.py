"""Signed download URLs for each file of a Kaggle model version, without downloading.

A pod can then fetch the weights straight from Kaggle's storage: a signed URL
is temporary and grants only that file, so no Kaggle credential leaves this
machine. Each URL is taken from the API's redirect (Location), which is never
followed, so the file never passes through here. Prints JSON:
{path: {"size": bytes, "url": signed URL}}. Keep the output out of the repo:
the URLs are bearer-style until they expire.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ingest_kaggle_to_r2 import kaggle_api, redirect_target


def list_files(api, handle):
    owner, model, framework, instance, version = handle.split('/')
    page = api.model_instance_version_files(handle, page_size=100)
    return [(f.name, int(f.size)) for f in page.files]


def signed_url(api, handle, path):
    from kagglesdk.models.types.model_api_service import ApiDownloadModelInstanceVersionRequest
    from kagglesdk.models.types.model_enums import ModelFramework
    owner, model, framework, instance, version = handle.split('/')
    with api.build_kaggle_client() as kaggle:
        http = kaggle.models.model_api_client._client
        http._init_session()
        request = ApiDownloadModelInstanceVersionRequest()
        request.owner_slug, request.model_slug, request.instance_slug = owner, model, instance
        request.framework = ModelFramework['MODEL_FRAMEWORK_' + framework.upper()]
        request.version_number = int(version)
        request.path = path
        prepared = http._prepare_request('models.ModelApiService', 'ApiDownloadModelInstanceVersion', request)
        settings = http._session.merge_environment_settings(prepared.url, {}, None, None, None)
        return redirect_target(http._session, prepared, settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handle', help='owner/model/framework/instance/version')
    args = parser.parse_args()
    api = kaggle_api()
    result = {path: {'size': size, 'url': signed_url(api, args.handle, path)}
              for path, size in list_files(api, args.handle)}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
