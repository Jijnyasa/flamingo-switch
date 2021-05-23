import click
from models.configuration import *
import json
import os

from utils.common import *
components = components_data



@click.group(invoke_without_command=True)
def cli():
    pass


@cli.command('deploy')
@click.option('--component', type=click.Choice(components))
@click.option('--jar', required=True, help='path to the deployable jar')
@click.option('--host', required=True, help='Host to which you want to deploy')
def deploy_component(component, jar, host):
    current_user  = get_current_user()
    absolute_jar_path = os.path.abspath(jar)

    initialize_remote_dir(host)
    copy_data(absolute_jar_path, host, current_user)
    process_id, jar_version_name = get_java_jar_process(host, component)
    replace_jar(absolute_jar_path, host, component, jar_version_name, current_user)
    kill_jps_process(host, process_id)

@cli.command('undeploy')
@click.option('--component', type=click.Choice(components))
@click.option('--host', required=True, help='Host to which you want to deploy')
def undeploy_component(component, host):
    current_user  = get_current_user()
    process_id, jar_version_name = get_java_jar_process(host, component)
    replace_original_jar(host, component, jar_version_name, current_user)
    kill_jps_process(host, process_id)

@cli.command('patch')
@click.option('--component', type=click.Choice(components))
@click.option('--file', required=True, help='path to the java file which you want to patch')
@click.option('--host', required=True, help='Host in which you want to patch')
def patch_component(component, file, host):
    current_user = get_current_user()
    absolute_file_path = os.path.abspath(file)

    initialize_remote_dir(host)
    copy_data(absolute_file_path, host, current_user)
    process_id, jar_version_name = get_java_jar_process(host, component)
    patch_java_process(host, jar_version_name, component, current_user)
    kill_jps_process(host, process_id)

@cli.command('config_reload')
@click.option('--component', type=click.Choice(components))
@click.option('--config', required=True, help='path to the config file which you want to reload')
@click.option('--host', required=True, help='Host in which you want to do config reload')
def config_reload(component, config, host):
    current_user = get_current_user()
    absolute_config_path = os.path.abspath(config)

    initialize_remote_dir(host)
    copy_data(absolute_config_path, host, current_user)
    process_id, java_process = get_java_jar_process(host, component)

    replace_config(absolute_config_path, host, component, current_user)
    kill_jps_process(host, process_id)


if __name__ == '__main__':
    cli()
