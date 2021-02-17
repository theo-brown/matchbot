source /home/tab53/3.8_env/bin/activate
cd /home/tab53/programs/tournaBOT
git checkout main
git pull
pipreqs . --force
pip install -r requirements.txt
systemctl --user daemon-reload
systemctl --user restart tournabot.service
