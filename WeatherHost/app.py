import os
from flask import Flask
from app.routes import get_weather, subscribe, trigger_alert

app = Flask(__name__)

# Configure the application
app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')


# Register routes manually (for now, we can add other routes if needed)
app.add_url_rule('/', 'get_weather', get_weather, methods=['GET'])
app.add_url_rule('/subscribe', 'subscribe', subscribe, methods=['POST'])
app.add_url_rule('/trigger_alert', 'trigger_alert', trigger_alert, methods=['POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("VM1").split(":")[-1],debug=True)
