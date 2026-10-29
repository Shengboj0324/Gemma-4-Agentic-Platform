"""Stage an explicit, credential-free training worker source bundle.

This is not a runtime environment or model bundle. Both are independently
verified by the worker on the Pod. No cloud or GPU execution occurs here.
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, inventory, verify

FILES = [
    'scripts/run_p1_training.py', 'scripts/run_p1_training_worker.py',
    'zenithsync/__init__.py', 'zenithsync/artifacts.py', 'zenithsync/contracts.py',
    'scripts/transfer_artifact.py', 'zenithsync/object_store.py',
    'scripts/verify_architecture_layout.py', 'zenithsync/architecture_layout.py',
    'zenithsync/model_intake.py',
    'zenithsync/conversation.py', 'zenithsync/process_supervisor.py',
    'zenithsync/quantized_layout.py', 'zenithsync/training_batch.py',
    'zenithsync/training_fixture.py', 'zenithsync/training_masks.py',
    'zenithsync/training_pilot.py', 'zenithsync/training_state.py',
    'zenithsync/gpu_memory.py', 'configs/p1-training-pilot.json',
    'zenithsync/optimizer_checkpoint.py',
    'zenithsync/training_corpus.py', 'zenithsync/splits.py',
    'scripts/inspect_training_corpus.py',
    'scripts/plan_corpus_updates.py', 'zenithsync/training_schedule.py',
    'zenithsync/corpus_optimization.py',
    'zenithsync/corpus_training.py',
    'zenithsync/training_rng.py',
    'zenithsync/checkpoint_storage.py',
    'zenithsync/adapter_checkpoint.py',
    'zenithsync/training_session.py',
    'zenithsync/session_report.py',
    'zenithsync/corpus_run.py', 'zenithsync/gemma_training.py',
    'scripts/run_corpus_training.py', 'scripts/run_corpus_training_worker.py',
    'configs/p1-corpus-qualification.json',
    'requirements/serving-linux-py312-httpfix.lock.txt',
    'requirements/training-peft-supplement.lock.txt',
    'evidence/p1/model-intake-001/model-manifest.json',
    'docs/32-full-checkpoint-gpu-qualification.md',
    # R2 is the corpus's durable home, so the Pod must be able to stage from it
    # and independently re-verify what it staged before training on it.
    'zenithsync/r2_client.py', 'zenithsync/corpus_transport.py',
    'zenithsync/corpus_audit.py', 'zenithsync/corpus_admission.py',
    'zenithsync/campaign_plan.py',
    'scripts/stage_corpus_from_r2.py', 'scripts/publish_corpus_to_r2.py',
    'scripts/verify_admitted_corpus.py', 'scripts/admit_training_corpus.py',
    'scripts/plan_training_campaign.py',
    # The host check the worker's own preconditions mirror; run it first on a pod.
    'zenithsync/runtime_preflight.py', 'scripts/verify_training_runtime.py',
    # One command that proves, from the bucket alone, that the data path a run
    # needs is complete — and the shipment tool that keeps the bucket complete.
    'scripts/verify_r2_training_readiness.py',
    'zenithsync/evidence_shipment.py', 'scripts/ship_evidence_to_r2.py',
    'requirements/r2-transport.lock.txt',
    'docs/42-training-unblock-and-data-scale.md',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=False)
    args.output.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        source = ROOT / name
        identity = file_record(source)
        destination = args.directory / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if file_record(destination) != identity:
            raise ValueError('Source changed during staging: ' + name)
    env = {**os.environ, 'PYTHONPATH': '', 'PYTHONDONTWRITEBYTECODE': '1'}
    checks = []
    with tempfile.TemporaryDirectory() as isolated:
        for script in ['run_p1_training.py', 'run_p1_training_worker.py',
                       'transfer_artifact.py',
                       'verify_architecture_layout.py',
                       'inspect_training_corpus.py', 'plan_corpus_updates.py',
                       'run_corpus_training.py', 'run_corpus_training_worker.py',
                       'stage_corpus_from_r2.py', 'publish_corpus_to_r2.py',
                       'verify_admitted_corpus.py', 'admit_training_corpus.py',
                       'plan_training_campaign.py', 'verify_training_runtime.py',
                       'verify_r2_training_readiness.py', 'ship_evidence_to_r2.py']:
            command = [sys.executable, '-I', '-B',
                       str((args.directory / 'scripts' / script).resolve()), '--help']
            result = subprocess.run(command, cwd=isolated, env=env, capture_output=True,
                                    text=True, timeout=30)
            (args.output / (script + '.log')).write_text(result.stdout + result.stderr)
            if result.returncode != 0:
                raise ValueError('Staged CLI import failed: ' + script)
            checks.append(script)
    manifest = inventory(args.directory, kind='candidate', source='explicit P1 training worker sources', revision='001')
    verify(args.directory, manifest)
    (args.output / 'manifest.json').write_bytes(canonical_json(manifest))
    (args.output / 'receipt.json').write_bytes(canonical_json({
        'schema_version': 1, 'status': 'source_bundle_imports_verified',
        'cli_import_checks': checks, 'file_count': len(manifest['files']),
        'total_bytes': sum(row['size_bytes'] for row in manifest['files']),
        'model_manifest': file_record(args.directory / 'evidence/p1/model-intake-001/model-manifest.json'),
        'preparer': file_record(Path(__file__)),
        'scope': 'Source closure and help only; not pinned Linux runtime, CUDA or full checkpoint validation'}))
    print('Training source bundle staged and isolated CLI imports verified')


if __name__ == '__main__':
    main()
