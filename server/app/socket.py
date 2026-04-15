import json

from flask_sock import Sock

from app.envelope_status_store import envelope_status_store

sock = Sock()


def _broadcast(payload):
    serialized = json.dumps(payload)
    stale_clients = []
    for client in envelope_status_store.clients():
        try:
            client.send(serialized)
        except Exception:
            stale_clients.append(client)

    for client in stale_clients:
        envelope_status_store.unregister_client(client)


def publish_envelope_status():
    records = envelope_status_store.all()
    _broadcast(records)


def init_realtime(app):
    sock.init_app(app)

    @sock.route('/api/ws/envelopes')
    def envelope_updates(ws):
        envelope_status_store.register_client(ws)
        try:
            ws.send(envelope_status_store.all())

            while True:
                message = ws.receive()
                if message is None:
                    break
        except Exception:
            pass
        finally:
            envelope_status_store.unregister_client(ws)