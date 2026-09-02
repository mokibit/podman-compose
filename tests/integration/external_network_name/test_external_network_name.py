# SPDX-License-Identifier: GPL-2.0

import os
import unittest

from tests.integration.test_utils import RunSubprocessMixin
from tests.integration.test_utils import podman_compose_path
from tests.integration.test_utils import test_path


def compose_yaml_path() -> str:
    return os.path.join(os.path.join(test_path(), "external_network_name"), "docker-compose.yml")


class TestExternalNetworkName(unittest.TestCase, RunSubprocessMixin):
    def test_external_network_with_name(self) -> None:
        # Pre-create the external network
        self.run_subprocess_assert_returncode(
            ["podman", "network", "create", "external_network_name_backend"],
        )
        try:
            self.run_subprocess_assert_returncode(
                [podman_compose_path(), "-f", compose_yaml_path(), "up", "-d"],
            )

            container_id_out, _ = self.run_subprocess_assert_returncode(
                [
                    podman_compose_path(),
                    "-f",
                    compose_yaml_path(),
                    "ps",
                    "--format",
                    '{{.ID}}',
                ],
            )
            container_id = container_id_out.decode('utf-8').split('\n')[0]
            output, _ = self.run_subprocess_assert_returncode(
                [
                    "podman",
                    "inspect",
                    container_id,
                    "--format",
                    "{{range $key, $value := .NetworkSettings.Networks }}{{ $key }}\n{{ end }}",
                ],
            )
            self.assertEqual(output.decode('utf-8').strip(), "external_network_name_backend")
        finally:
            self.run_subprocess_assert_returncode([
                podman_compose_path(),
                "-f",
                compose_yaml_path(),
                "down",
                "-t",
                "0",
            ])
            self.run_subprocess_assert_returncode(
                ["podman", "network", "rm", "-f", "external_network_name_backend"],
            )
