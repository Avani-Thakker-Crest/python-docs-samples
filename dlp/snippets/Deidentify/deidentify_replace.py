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

from typing import List

import google.cloud.dlp

# [START dlp_deidentify_replace]


def deidentify_with_replace(
    project: str,
    input_str: str,
    info_types: List[str],
    replacement_str: str = "REPLACEMENT_STR",
) -> None:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by replacing matched input values with a value you specify.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        input_str: The string to deidentify (will be treated as text).
        info_types: A list of strings representing info types to look for.
        replacement_str: The string to replace all values that match given
            info types.
    Returns:
        None; the response from the API is printed to the terminal.
    """

    # Instantiate a client
    dlp = google.cloud.dlp_v2.DlpServiceClient()

    # Convert the project id into a full resource id.
    parent = f"projects/{project}/locations/global"

    # Construct inspect configuration dictionary
    inspect_config = {"info_types": [{"name": info_type} for info_type in info_types]}

    # Construct deidentify configuration dictionary
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {"string_value": replacement_str}
                        }
                    }
                }
            ]
        }
    }

    # Construct item
    item = {"value": input_str}

    # Call the API
    response = dlp.deidentify_content(
        request={
            "parent": parent,
            "deidentify_config": deidentify_config,
            "inspect_config": inspect_config,
            "item": item,
        }
    )

    # Print out the results.
    print(response.item.value)


# [END dlp_deidentify_replace]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--info_types",
        nargs="+",
        help="Strings representing info types to look for. A full list of "
             "info categories and types is available from the API. Examples "
             'include "FIRST_NAME", "LAST_NAME", "EMAIL_ADDRESS". '
             "If unspecified, the three above examples will be used.",
        default=["FIRST_NAME", "LAST_NAME", "EMAIL_ADDRESS"],
    )
    parser.add_argument(
        "project",
        help="The Google Cloud project id to use as a parent resource.",
    )
    parser.add_argument("item", help="The string to deidentify.")
    parser.add_argument(
        "replacement_str", help="The string to " "replace all matched values with."
    )

    args = parser.parse_args()
    deidentify_with_replace(
        args.project,
        args.item,
        args.info_types,
        replacement_str=args.replacement_str,
    )
