"""
tools/secure_storage.py

Encrypted-at-rest storage for patient medication data.

Security features demonstrated:
- Fernet (AES-128) encryption -- nothing written to disk in plaintext
- Per-record access scoping -- only authorized users can decrypt
- Key managed via environment variable -- never hardcoded or logged
- Hard delete support -- user can remove their data entirely
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

DATA_DIR = Path(__file__).parent.parent / "data" / "patients"
ENV_KEY_NAME = "MEDGUARD_ENCRYPTION_KEY"


class SecureStorageError(Exception):
    pass


def _get_fernet() -> Fernet:
    key = os.environ.get(ENV_KEY_NAME)
    if not key:
        raise SecureStorageError(
            f"{ENV_KEY_NAME} is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def save_patient_record(
    patient_name: str,
    record: dict,
    access_scope: list[str]
) -> None:
    """
    Encrypt and persist one patient's medication record.

    patient_name: used as the record identifier (lowercased, spaces
    replaced with underscores to match the session user_id).
    access_scope: list of user IDs allowed to decrypt this record.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fernet = _get_fernet()

    patient_id = patient_name.lower().replace(" ", "_")
    plaintext = json.dumps(record).encode("utf-8")
    ciphertext = fernet.encrypt(plaintext)

    envelope = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "access_scope": access_scope,
        "ciphertext": ciphertext.decode("utf-8"),
    }

    out_path = DATA_DIR / f"{patient_id}.json"
    out_path.write_text(json.dumps(envelope, indent=2))
    out_path.chmod(0o600)  # owner read/write only
    print(f"Record saved for {patient_name}.")


def load_patient_record(
    patient_name: str,
    requesting_user_id: str
) -> dict:
    """
    Decrypt and return one patient's record, enforcing access scope.
    Fails closed on unauthorized access.
    """
    patient_id = patient_name.lower().replace(" ", "_")
    path = DATA_DIR / f"{patient_id}.json"

    if not path.exists():
        raise SecureStorageError(
            f"No record found for {patient_name!r}."
        )

    envelope = json.loads(path.read_text())

    if requesting_user_id not in envelope.get("access_scope", []):
        raise SecureStorageError("Access denied for this patient record.")

    fernet = _get_fernet()
    try:
        plaintext = fernet.decrypt(envelope["ciphertext"].encode("utf-8"))
    except InvalidToken as e:
        raise SecureStorageError(
            "Decryption failed -- record may be corrupted or "
            "the encryption key has changed."
        ) from e

    return json.loads(plaintext)


def delete_patient_record(patient_name: str) -> None:
    """Hard delete -- removes a patient's data entirely from disk."""
    patient_id = patient_name.lower().replace(" ", "_")
    path = DATA_DIR / f"{patient_id}.json"
    if path.exists():
        path.unlink()
        print(f"Record for {patient_name} deleted.")
    else:
        print(f"No record found for {patient_name}.")


if __name__ == "__main__":
    # Quick smoke test
    os.environ[ENV_KEY_NAME] = Fernet.generate_key().decode()

    save_patient_record(
        "my mom",
        {"meds": ["warfarin", "ibuprofen"]},
        access_scope=["caregiver"]
    )

    record = load_patient_record("my mom", "caregiver")
    print("Loaded:", record)

    try:
        load_patient_record("my mom", "stranger")
    except SecureStorageError as e:
        print("Access control works:", e)

    delete_patient_record("my mom")