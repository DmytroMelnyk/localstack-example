cat << EOF >> /home/vscode/.bashrc
complete -C '/usr/local/bin/aws_completer' aws
complete -C '/usr/local/bin/aws_completer' awslocal
EOF

# fix ownership for windows' mounted volume
sudo chown -R vscode:vscode .git
pip install --user -r requirements.txt
pip install --user -r requirements-dev.txt
pip install --user -r src/common/requirements.txt
pip install --user -r src/api/requirements.txt