"""
Hash Verifier
-------------
Generates MD5 and SHA256 hashes for a file and, if a known hash is
supplied, checks whether the file still matches it. This is the core
technique investigators use to prove a piece of digital evidence has
not been altered since it was collected (chain of custody).
"""

import hashlib
import os



def _hash_file(path, algo_name):
    hasher = hashlib.new(algo_name)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_hashes(path):
    """Return a dict with md5 and sha256 hashes for the given file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    return {
        "file": os.path.abspath(path),
        "size_bytes": os.path.getsize(path),
        "md5": _hash_file(path, "md5"),
        "sha256": _hash_file(path, "sha256"),
    }


def verify_hash(path, known_hash):
    """
    Compare a file's hash against a known hash string. Auto-detects
    whether the known hash is MD5 (32 hex chars) or SHA256 (64 hex
    chars) based on length. Returns a result dict including a match
    boolean, safe to hand straight to the report generator.
    """
    known_hash = known_hash.strip().lower()
    algo = "sha256" if len(known_hash) == 64 else "md5" if len(known_hash) == 32 else None

    if algo is None:
        raise ValueError(
            f"'{known_hash}' is not a recognised MD5 (32 chars) or SHA256 (64 chars) hash."
        )

    computed = _hash_file(path, algo)
    match = computed == known_hash

    return {
        "file": os.path.abspath(path),
        "algorithm": algo.upper(),
        "known_hash": known_hash,
        "computed_hash": computed,
        "match": match,
        "verdict": "INTEGRITY VERIFIED - file unchanged" if match
                   else "INTEGRITY FAILED - file has been modified or is not the same file"
    }
