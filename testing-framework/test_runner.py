#!/usr/bin/env python3

import argparse
import math
import threading
import subprocess
import time
import os
from datetime import datetime
import docker
docker_client = docker.from_env()

parser = argparse.ArgumentParser(description='Test framework for running openpilot with CARLA')
parser.add_argument('-t', '--terminal', help='Terminal application to use when launching openpilot', default='gnome-terminal')
parser.add_argument('-d', '--test_directory', help='Directory to store the test results', default='%s/test_results' % (os.getcwd()))
parser.add_argument('-o', '--timeout', help='Maximum test duration', default='60')

args = parser.parse_args()
test_directory = args.test_directory
test_directory += '/%s/' %  datetime.now().isoformat().replace(':', '_')
MAX_DURATION = float(args.timeout)

CARLA_CONTAINER_NAME = 'openpilot_carla'
OPENPILOT_CONTAINER_NAME = 'openpilot_client'
ALL_CONTAINERS = [CARLA_CONTAINER_NAME, OPENPILOT_CONTAINER_NAME]


run_file_contents = '''source ~/.bashrc
./start_openpilot_docker.sh
exit
'''
run_carla_contents = '''source ~/.bashrc
./start_carla.sh
exit
'''
carla_file = '%s/carla_run_file.sh' % os.getcwd()
with open(carla_file, 'w') as f:
  f.write(run_carla_contents)


def kill_container(container):
  os.system('docker kill %s' % container)


def kill_all_containers():
  for container in ALL_CONTAINERS:
    kill_container(container)


def is_carla_running():
  return CARLA_CONTAINER_NAME in [container.name for container in docker_client.containers.list()]
  
  
def is_openpilot_running():
  return OPENPILOT_CONTAINER_NAME in [container.name for container in docker_client.containers.list()]


def start_carla():
  subprocess.Popen([args.terminal, '--', 'bash', '--rcfile', '%s' % carla_file])


def ensure_carla():
  if not is_carla_running():
    start_carla()


def ensure_no_openpilot():
  if is_openpilot_running():
    kill_container(OPENPILOT_CONTAINER_NAME)


def run_test(test_num):
  ensure_no_openpilot()
  ensure_carla()
  start_time = time.time()
  open_pilot_env = os.environ.copy()
  open_pilot_env['MOUNT_OPENPILOT'] = '1'
  cur_dir = test_directory + ('test%d/' % test_num)
  os.makedirs(cur_dir)
  run_file = cur_dir + 'run_file.sh'
  with open(run_file, 'w') as f:
    f.write(run_file_contents)
  open_pilot_env['TEST_DIRECTORY'] = cur_dir[:-1]
  open_pilot = subprocess.Popen([args.terminal, '--', 'bash', '--rcfile', '%s' % run_file], env=open_pilot_env)
  running = True
  killing = False
  time.sleep(5)
  timing_str = ''
  while running:
    time.sleep(1)
    running = is_openpilot_running()
    if (time.time() - start_time) > MAX_DURATION and not killing:
      killing = True
      print('Test timeout reached, killing docker')
      timing_str += 'Test timeout reached, killing docker\n'
      kill_all_containers()
  timing_str += 'Test %d finished after %0.1f sec\n' % (test_num, time.time() - start_time)
  print('Test %d finished after %0.1f sec' % (test_num, time.time() - start_time))
  with open('%stiming.txt' % cur_dir, 'w') as f:
    f.write(timing_str)



if __name__ == '__main__':
  for i in range(20):
    run_test(i)
  

  
