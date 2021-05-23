import subprocess
import os
import json
from termcolor import colored
from retrying import retry
from utils.constants import *

def get_configuration():
    with open(os.path.expanduser(config_path), 'r') as json_file:
        data = json.load(json_file)
        components = data['components'].keys()
        return data['components'], data['constants']


components_data, constants = get_configuration()
retry_count = constants['retry_count']
tmp_dir = constants['tmp_dir']
remote_jar_tmp_name = constants["remote_jar_tmp_name"]
remote_config_tmp_name =  constants["remote_config_tmp_name"]

def get_current_user():
    result = subprocess.run(['whoami'], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()


local_retry = retry_count


@retry(stop_max_attempt_number=retry_count)
def execute_remote_command(host, process_command):
    global local_retry
    if local_retry == retry_count:
        print(colored("Executing command {cmd}.".format(cmd=process_command), 'yellow'))
    local_retry = local_retry - 1
    ssh_exec = subprocess.Popen(["ssh", "%s" % host, process_command], shell=False, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
    result = ssh_exec.stdout.readlines()
    if not result:
        print(colored("The command failed, retrying it, number of attempts left are {c}".format(c=local_retry), 'red'))
        print()
        error = ssh_exec.stderr.readlines()
        if local_retry > 0:
            raise Exception("Error")

        print(colored("################################### ERROR ###################################", 'red'))
        print(colored(",".join(error), 'red'))
        print(colored("################################### ERROR ###################################", 'red'))
        print()
        exit()
    print(colored("################################### SUCCESS ###################################", 'green'))
    print(colored(",".join(result), 'green'))
    print(colored("################################### SUCCESS ###################################", 'green'))
    print()
    local_retry = retry_count
    return result


def get_java_jar_process(host, component):
    print(colored("getting java process using command --------->", ))
    java_process_command = 'sudo odoctl exec -a {app_name} jps -l | grep {grep_string} ; ' \
                           'sudo odoctl exec -a {app_name} find {jar_path} -maxdepth 1 -name {jar_name} | head -n 1;'.format(
        app_name=components_data[component]['odo_app_name'], grep_string=components_data[component]['grep_string'],
        jar_name=components_data[component]['jar_name'], jar_path=components_data[component]['jar_path'])
    result = execute_remote_command(host, java_process_command)
    process_result = result[0].split(' ')
    process_result = list(map((lambda x: x.strip()), process_result))
    modified_process_id = process_result[0]

    if len(result) != 2 and len(process_result)!=2:
        colored("The command failed due to issue in jar name or jps configuration, try through other methods", 'red')
        modified_process_id = get_java_user_process(''.join(result[0].strip().split('/')[-1]), host, component)
    result[1] = ''.join(result[1][2:].strip().split('/')[-1])
    return modified_process_id, result[1]


def initialize_remote_dir(host):
    print(colored("Initializing temporary remote directories on the host using command ------->"))
    initialize_command = 'sudo rm -rf {tmp_dir}; mkdir {tmp_dir}; ls -lrth '.format(tmp_dir=tmp_dir)
    result = execute_remote_command(host, initialize_command)


@retry(stop_max_attempt_number=retry_count)
def copy_data(data, host, user):
    global local_retry
    copy_command = 'scp {local_data} {user}@{host}:/home/{user}/{tmp_dir}/'.format(local_data=data, host=host,
                                                                                   user=user,
                                                                                   tmp_dir=tmp_dir)
    if local_retry == retry_count:
        print(colored("Copying data to the remote host using command --------->", ))
        print(colored("Executing command {cmd}".format(cmd=copy_command), 'yellow'))
    ssh_exec = subprocess.call([copy_command], shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    local_retry = local_retry - 1
    if ssh_exec == 0:
        print(colored("################################### SUCCESS ###################################", 'green'))
        print(colored("Data successfully copied", 'green'))
        print(colored("################################### SUCCESS ###################################", 'green'))
        print()
    else:
        print(colored("The command failed, retrying it, number of attempts left are {c}".format(c=local_retry), 'red'))
        print()
        if local_retry > 0:
            raise Exception("Error")
        print(colored("################################### ERROR ###################################", 'red'))
        print(colored("Error in copying, check path / yubiki / vpn", 'red'))
        print(colored("################################### ERROR ###################################", 'red'))
        print()
        exit()
    local_retry = retry_count


def replace_jar(local_jar_path, host, component, remote_jar_name, user):
    print(colored("Replacing jars on the remote host using command ------->", ))
    remote_path = components_data[component]['jar_path']
    app_name = components_data[component]['odo_app_name']
    local_jar_name = local_jar_path.split('/')[-1]
    java_process_command = "sudo odoctl exec -a {app_name}  cp /home/{user}/{tmp_dir}/{local_jar_name} {remote_path} ; " \
                           "sudo odoctl exec -a {app_name}  mv {remote_path}{remote_jar} {remote_path}{remote_jar}{remote_jar_tmp_name} ; " \
                           "sudo odoctl exec -a {app_name}  mv {remote_path}{local_jar_name} {remote_path}{remote_jar} ;" \
                           "sudo odoctl exec -a {app_name}  ls -lrth {remote_path}".format(app_name=app_name,
                                                                                              user=user,
                                                                                              local_jar_name=local_jar_name,
                                                                                              remote_path=remote_path,
                                                                                              remote_jar_tmp_name=remote_jar_tmp_name,
                                                                                              tmp_dir=tmp_dir,
                                                                                              remote_jar=remote_jar_name)
    result = execute_remote_command(host, java_process_command)

def replace_original_jar(host, component, remote_jar_name, user):
    print(colored("Replacing jars on the remote host using command ------->", ))
    remote_path = components_data[component]['jar_path']
    app_name = components_data[component]['odo_app_name']
    java_process_command = "sudo odoctl exec -a {app_name}  mv {remote_path}{remote_jar} {remote_path}{remote_jar}.{user} ; " \
                           "sudo odoctl exec -a {app_name}  mv {remote_path}{remote_jar}{remote_jar_tmp_name} {remote_path}{remote_jar} ;" \
                           "sudo odoctl exec -a {app_name}  ls -lrth {remote_path}".format(app_name=app_name,
                                                                                              user=user,
                                                                                              remote_path=remote_path,
                                                                                              remote_jar_tmp_name=remote_jar_tmp_name,
                                                                                              tmp_dir=tmp_dir,
                                                                                              remote_jar=remote_jar_name)
    result = execute_remote_command(host, java_process_command)


def replace_config(local_config_path, host, component, user):
    print(colored("Replacing config on the remote host using command --------->", ))
    local_config_path_rel = local_config_path.split('config', 1)[1]
    local_config_name = local_config_path.split('/')[-1]
    remote_config_name = local_config_name
    remote_config_path = components_data[component]['config_path'] + '/'.join(
        local_config_path_rel.split('/')[:-1])
    app_name = components_data[component]['odo_app_name']
    java_process_command = "sudo odoctl exec -a {app_name}  mv {remote_config_path}{remote_config_name} {remote_config_path}{remote_config_name}{remote_config_tmp_name} ; " \
                           "sudo odoctl exec -a {app_name}  cp /home/{user}/{tmp_dir}/{local_config_name} {remote_config_path} ; " \
                           "sudo odoctl exec -a {app_name}  ls -lrth {remote_config_path}".format(
        app_name=app_name,
        user=user,
        local_config_name=local_config_name,
        remote_config_path=remote_config_path,
        remote_config_tmp_name=remote_config_tmp_name,
        tmp_dir=tmp_dir,
        remote_config_name=remote_config_name)
    result = execute_remote_command(host, java_process_command)


def kill_jps_process(host, pid):
    print(colored("Killing java process using command ---------->", ))
    java_process_command = "sudo ps -p {pid}; sudo kill -9 {pid};".format(pid=pid)
    result = execute_remote_command(host, java_process_command)


def patch_java_process(host, remote_jar_name, component, user):
    print(colored("Patching java jar using command -------->", ))
    app_name = components_data[component]['odo_app_name']
    remote_path = components_data[component]['jar_path']
    command = "sudo odoctl exec -a {app_name}  cp {remote_path}{remote_jar} {remote_path}{remote_jar}{remote_jar_tmp_name} ; " \
              "sudo odoctl exec -a {app_name}  javac -cp {remote_path}{remote_jar} -d /home/{user}/{tmp_dir}/ /home/{user}/{tmp_dir}/*.java; " \
              "sudo odoctl exec -a {app_name}  jar uvf {remote_path}{remote_jar} -C /home/{user}/{tmp_dir}/ .".format(
        app_name=app_name,
        remote_path=remote_path,
        remote_jar=remote_jar_name,
        remote_jar_tmp_name=remote_jar_tmp_name,
        user=user,
        tmp_dir=tmp_dir)
    result = execute_remote_command(host, command)

def get_java_user_process(jar_name, host, component):
    print(colored("Getting java process as jps has some issues using command -------->", ))
    app_name = components_data[component]['odo_app_name']
    command = "ps aux | grep {jar_name} | grep -v grep | awk '{{print $2}}'".format(
        jar_name=jar_name)
    result = execute_remote_command(host, command)
    result = list(map((lambda x: x.strip()), result))
    return result[0]

