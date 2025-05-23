import os
from disaster_relief_app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # fallback for local dev
    app.run(host='0.0.0.0', port=port, debug=False)
