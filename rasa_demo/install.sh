#!/bin/bash
set -Eeuo pipefail

#######################################
#
# installing ansible and roles
#
#######################################
echo "Installing pip and ansible"
sudo apt-get update -y
sudo apt-get install -y python3
sudo apt-get install -y python3-distutils || :  # if the package is not available and the command fails, do nothing,
                                                # the distutils are already installed
curl -O https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo pip install "ansible<2.9"

echo "Installing docker role"
ansible-galaxy install angstwad.docker_ubuntu
echo "Docker installed"


#######################################
#
# downloading the ansible playbook
# for the passed in version or latest
#
#######################################
echo "Downloading Rasa X playbook"
wget -qO rasa_x_playbook.yml https://storage.googleapis.com/rasa-x-releases/0.25.2/rasa_x_playbook.yml

#######################################
#
# running the ansible playbook
# (starts docker und serves Rasa X)
#
#######################################
echo "Running playbook"
ansible-playbook -i "localhost," -c local rasa_x_playbook.yml
