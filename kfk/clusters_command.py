import click
import os
import yaml

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf
from kfk.commons import *
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *


@click.option('-n', '--namespace', help='Namespace to use')
@click.option('--delete-config', help='A cluster configuration override to be removed for an existing cluster',
              multiple=True)
@click.option('--config', help='A cluster configuration override for the cluster being altered.',
              multiple=True)
@click.option('--alter', help='Alter the cluster.', is_flag=True)
@click.option('--delete', help='Delete the cluster.', is_flag=True)
@click.option('--create', help='Create the cluster.', is_flag=True)
@click.option('--describe', help='List details for the given cluster.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if=['list'])
@kfk.command()
def clusters(cluster, list, create, describe, delete, alter, config, delete_config, output, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system(Kubectl().get().kafkas().namespace(namespace).build())
    elif create:
        with open('{strimzi_path}/examples/kafka/kafka-ephemeral.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            cluster_temp_file = create_temp_file(file.read())
            open_file_in_system_editor(cluster_temp_file.name)
            is_confirmed = click.confirm("Are you sure you want to create the cluster with the saved configuration?")
            if is_confirmed:
                os.system(Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                    cluster_temp_file_path=cluster_temp_file.name))
            cluster_temp_file.close()

    elif describe:
        if output is not None:
            os.system(Kubectl().get().kafkas(cluster).namespace(namespace).output(output).build())
        else:
            os.system(Kubectl().describe().kafkas(cluster).namespace(namespace).build())
    elif delete:
        is_confirmed = click.confirm("Are you sure you want to delete the cluster?")
        if is_confirmed:
            os.system(Kubectl().delete().kafkas(cluster).namespace(namespace).build())
    elif alter:
        if len(config) > 0 or len(delete_config) > 0:
            if resource_exists("kafkas", cluster, cluster, namespace):
                stream = get_resource_as_stream("kafkas", cluster, namespace)
                cluster_dict = yaml.full_load(stream)

                delete_last_applied_configuration(cluster_dict)

                if len(config) > 0:
                    if cluster_dict["spec"]["kafka"].get("config") is None:
                        cluster_dict["spec"]["kafka"]["config"] = {}
                    add_resource_kv_config(config, cluster_dict["spec"]["kafka"]["config"])

                if len(delete_config) > 0:
                    if cluster_dict["spec"]["kafka"].get("config") is not None:
                        delete_resource_config(delete_config, cluster_dict["spec"]["config"])

                cluster_yaml = yaml.dump(cluster_dict)
                cluster_temp_file = create_temp_file(cluster_yaml)
                os.system(
                    Kubectl().apply().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                        cluster_temp_file_path=cluster_temp_file.name))
                cluster_temp_file.close()
            else:
                print_resource_not_found_msg(cluster, namespace)
        else:
            os.system(Kubectl().edit().kafkas(cluster).namespace(namespace).build())
    else:
        print_missing_options_for_command("clusters")
