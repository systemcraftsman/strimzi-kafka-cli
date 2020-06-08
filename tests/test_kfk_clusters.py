from unittest import TestCase, mock
from click.testing import CliRunner
from kfk_clusters import kfk
from kubectl_command_builder import Kubectl


class TestKfkClusters(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['clusters', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk clusters" in result.output

    @mock.patch('kfk_clusters.os')
    def test_list_clusters(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--list', '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().get().kafkas().namespace(self.namespace).build())

    @mock.patch('kfk_clusters.os')
    def test_describe_clusters(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--describe', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().describe().kafkas(self.cluster).namespace(self.namespace).build())

    @mock.patch('kfk_clusters.os')
    def test_describe_clusters_output_yaml(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['clusters', '--describe', '--cluster', self.cluster, '-n', self.namespace, '-o',
                                     'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkas(self.cluster).namespace(self.namespace).output("yaml").build())