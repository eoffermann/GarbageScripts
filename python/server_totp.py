#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server_totp.py

A simple TOTP "server" emulator that generates a shared secret key, displays
a QR code for provisioning an authenticator app, and prints the current
6-digit one‑time passcode to the console each time it changes.
"""

import argparse
import sys
import time
from typing import Optional

import pyotp
import qrcode
from PIL.Image import Image  # type: ignore


def generate_shared_secret() -> str:
    """
    Generate a base32-encoded shared secret key.

    Returns:
        str: A randomly generated 32-character base32 secret.
    """
    return pyotp.random_base32()


def create_provisioning_uri(secret: str, account_name: str, issuer_name: str) -> str:
    """
    Create a provisioning URI for TOTP setup in authenticator apps.

    Args:
        secret (str): The shared secret key.
        account_name (str): The user/account identifier (e.g., email).
        issuer_name (str): The service or organization name.

    Returns:
        str: A URI containing the TOTP parameters for QR code generation.
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=account_name, issuer_name=issuer_name)


def display_qr_code(data: str) -> Optional[Image]:
    """
    Generate and display a QR code for the given data.

    Args:
        data (str): The string to encode in the QR code.

    Returns:
        PIL.Image.Image: The generated QR code image, or None on failure.
    """
    try:
        img = qrcode.make(data)
        img.show()
        return img
    except Exception as e:
        print(f"Failed to generate or display QR code: {e}", file=sys.stderr)
        return None


def print_totp_codes(secret: str) -> None:
    """
    Continuously compute and print the current TOTP code whenever it changes.

    Args:
        secret (str): The shared secret key for TOTP generation.
    """
    totp = pyotp.TOTP(secret)
    previous_code = ""
    try:
        while True:
            current_code = totp.now()
            if current_code != previous_code:
                print(f"TOTP code: {current_code}")
                previous_code = current_code
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")


def main() -> None:
    """
    Parse command-line arguments, generate a shared secret,
    display a provisioning QR code, and print TOTP codes.
    """
    parser = argparse.ArgumentParser(
        description="Emulate a TOTP server: generate secret, show QR code, and print codes."
    )
    parser.add_argument(
        "-u", "--account-name",
        type=str,
        default="user@example.com",
        help="Account name for provisioning (e.g., your email)."
    )
    parser.add_argument(
        "-i", "--issuer-name",
        type=str,
        default="MyService",
        help="Issuer name for provisioning (e.g., your service)."
    )
    args = parser.parse_args()

    # 1. Generate shared secret
    secret = generate_shared_secret()
    print(f"Shared secret: {secret}")

    # 2. Create provisioning URI and display QR code
    uri = create_provisioning_uri(secret, args.account_name, args.issuer_name)
    print(f"Provisioning URI: {uri}")
    print("Displaying QR code. Scan it with your authenticator app.")
    display_qr_code(uri)

    # 3. Print TOTP codes as they update
    print_totp_codes(secret)


if __name__ == "__main__":
    main()

