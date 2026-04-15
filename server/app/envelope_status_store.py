import threading
from datetime import datetime, timezone


class EnvelopeStatusStore:
    """In-memory storage for envelope statuses and websocket clients."""

    def __init__(self):
        self._records = {}
        self._clients = set()
        self._lock = threading.RLock()

    def upsert(self, data):
        envelope_id = data.get('envelope_id')
        if not data['event'].startswith('extension-'):
            record = {
                'envelope_id': envelope_id,
                'event': data['event'],
                'subject': data['subject'],
                'status': data['status'],
                'status_timestamp': data['status_timestamp'],
                'signer_name': data['signer_name'],
                'extension_events': [],
            }
            with self._lock:
                if self._records.get(envelope_id):
                    self._records[envelope_id]['envelope_id'] = envelope_id
                    self._records[envelope_id]['subject'] = data['subject']
                    self._records[envelope_id]['status'] = data['status']
                    self._records[envelope_id]['status_timestamp'] = data['status_timestamp']
                    self._records[envelope_id]['signer_name'] = data['signer_name']
                else:
                    self._records[envelope_id] = record
        else:
            record = {
                'event': data['event'],
                'actionContract': data['action_contract'],
                'appName': data['app_name'],
                'attempt_time': data['attempt_time'],
                'verified': data['verified'],
            }
            with self._lock:
                self._records[envelope_id]['extension_events'].append(record)
        return self._records.values()

    def get(self, envelope_id):
        with self._lock:
            return self._records.get(envelope_id)

    def all(self):
        with self._lock:
            return list(self._records.values())

    def register_client(self, ws):
        with self._lock:
            self._clients.add(ws)

    def unregister_client(self, ws):
        with self._lock:
            self._clients.discard(ws)

    def clients(self):
        with self._lock:
            return list(self._clients)


envelope_status_store = EnvelopeStatusStore()
