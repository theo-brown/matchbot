cd /home/tab53/programs/matchbot
source venv/bin/activate
git checkout main
echo "Saving copy of database...."
cp database/database.db database/database_backup.db
echo "Resetting to last commit..."
git reset --hard origin/main
echo "Pulling from origin..."
git pull
echo "Restoring database..."
cp database/database_backup.db database/database.db
echo "Installing requirements..."
pip install -r requirements.txt
echo "Stopping matchbot.service..."
systemctl --user stop -f matchbot.service
echo "Reloading systemctl files..."
systemctl --user daemon-reload
echo "Starting matchbot.service..."
systemctl --user start matchbot.service
echo "Matchbot service status:"
systemctl --user status matchbot.service
