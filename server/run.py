from app import app
import os
import sys

if os.environ.get("DEBUG", "False") == "True":
    app.config["DEBUG"] = True
    port = int(os.environ.get("PORT", 5001))
    print(f"DEBUG Mode! Port: {port}", file=sys.stderr)
    app.run(port=port, debug=True)
else:
    app.run(port=5001)

print(app.url_map)