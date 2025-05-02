import requests

# Trigger your background worker restart via Render Deploy Hook
requests.post("https://api.render.com/deploy/srv-xxxxxxxxxxxxx/deploys",
              headers={"Authorization": "Bearer YOUR_RENDER_API_KEY"})
