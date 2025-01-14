# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Uses of the Data Loss Prevention API for deidentifying sensitive data."""

from __future__ import annotations

import argparse

import base64

import google.cloud.dlp

# [START dlp_reidentify_free_text_with_fpe_using_surrogate]


def reidentify_free_text_with_fpe_using_surrogate(
    project: str,
    input_str: str,
    alphabet: str = "NUMERIC",
    surrogate_type: str = "PHONE_TOKEN",
    unwrapped_key: str = "YWJjZGVmZ2hpamtsbW5vcA==",
) -> None:
    """Uses the Data Loss Prevention API to reidentify sensitive data in a
    string that was encrypted by Format Preserving Encryption (FPE) with
    surrogate type. The encryption is performed with an unwrapped key.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        input_str: The string to deidentify (will be treated as text).
        alphabet: The set of characters to replace sensitive ones with. For
            more information, see https://cloud.google.com/dlp/docs/reference/
            rest/v2beta2/organizations.deidentifyTemplates#ffxcommonnativealphabet
        surrogate_type: The name of the surrogate custom info type to used
            during the encryption process.
        unwrapped_key: The base64-encoded AES-256 key to use.
    Returns:
        None; the response from the API is printed to the terminal.
    """

    # Instantiate a client
    dlp = google.cloud.dlp_v2.DlpServiceClient()

    # Convert the project id into a full resource id.
    parent = f"projects/{project}/locations/global"

    # The wrapped key is base64-encoded, but the library expects a binary
    # string, so decode it here.
    unwrapped_key = base64.b64decode(unwrapped_key)

    # Construct Deidentify Config
    transformation = {
        "primitive_transformation": {
            "crypto_replace_ffx_fpe_config": {
                "crypto_key": {"unwrapped": {"key": unwrapped_key}},
                "common_alphabet": alphabet,
                "surrogate_info_type": {"name": surrogate_type},
            }
        }
    }

    reidentify_config = {
        "info_type_transformations": {"transformations": [transformation]}
    }

    inspect_config = {
        "custom_info_types": [
            {"info_type": {"name": surrogate_type}, "surrogate_type": {}}
        ]
    }

    # Convert string to item
    item = {"value": input_str}

    # Call the API
    response = dlp.reidentify_content(
        request={
            "parent": parent,
            "reidentify_config": reidentify_config,
            "inspect_config": inspect_config,
            "item": item,
        }
    )

    # Print results
    print(response.item.value)


# [END dlp_reidentify_free_text_with_fpe_using_surrogate]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "project",
        help="The Google Cloud project id to use as a parent resource.",
    )
    parser.add_argument(
        "input_str",
        help="The string to re-identify. " "Example: string = 'My SSN is 372819127'",
    )
    parser.add_argument(
        "unwrapped_key",
        help="The base64-encoded AES-256 key to use.",
    )
    parser.add_argument(
        "-a",
        "--alphabet",
        default="ALPHA_NUMERIC",
        help="The set of characters to replace sensitive ones with. Commonly "
             'used subsets of the alphabet include "NUMERIC", "HEXADECIMAL", '
             '"UPPER_CASE_ALPHA_NUMERIC", "ALPHA_NUMERIC", '
             '"FFX_COMMON_NATIVE_ALPHABET_UNSPECIFIED"',
    )
    parser.add_argument(
        "-s",
        "--surrogate_type",
        help="The name of the surrogate custom info type to use. Only "
             "necessary if you want to reverse the de-identification process. Can "
             "be essentially any arbitrary string, as long as it doesn't appear "
             "in your dataset otherwise.",
    )

    args = parser.parse_args()

    reidentify_free_text_with_fpe_using_surrogate(
        args.project,
        args.input_str,
        args.alphabet,
        args.surrogate_type,
        args.unwrapped_key,
    )
