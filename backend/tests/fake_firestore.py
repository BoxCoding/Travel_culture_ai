"""A minimal in-memory double for the slice of the Firestore client API this app
actually uses: collection()/document()/get()/set()/add()/where(==)/limit()/stream().
Not a general-purpose Firestore emulator -- just enough to test our routers
without a real GCP project.
"""


class FakeDocSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class FakeQuery:
    def __init__(self, items):
        self._items = items  # list[(doc_id, data)]

    def where(self, field, op, value):
        assert op == "==", f"fake only supports '==', got {op!r}"
        return FakeQuery([(i, d) for i, d in self._items if d.get(field) == value])

    def limit(self, n):
        return FakeQuery(self._items[:n])

    def stream(self):
        return iter(FakeDocSnapshot(i, d) for i, d in self._items)


class FakeDocumentRef:
    def __init__(self, store, doc_id, subcollections):
        self._store = store
        self.id = doc_id
        self._subcollections = subcollections

    def get(self):
        return FakeDocSnapshot(self.id, self._store.get(self.id))

    def set(self, data):
        self._store[self.id] = dict(data)

    def collection(self, name):
        key = (self.id, name)
        if key not in self._subcollections:
            self._subcollections[key] = FakeCollectionRef()
        return self._subcollections[key]


class FakeCollectionRef:
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._sub: dict[tuple, "FakeCollectionRef"] = {}
        self._counter = 0

    def document(self, doc_id: str | None = None):
        if doc_id is None:
            self._counter += 1
            doc_id = f"auto{self._counter}"
        return FakeDocumentRef(self._store, doc_id, self._sub)

    def add(self, data: dict):
        self._counter += 1
        doc_id = f"auto{self._counter}"
        self._store[doc_id] = dict(data)
        return (None, FakeDocumentRef(self._store, doc_id, self._sub))

    def where(self, field, op, value):
        return FakeQuery(list(self._store.items())).where(field, op, value)

    def limit(self, n):
        return FakeQuery(list(self._store.items())).limit(n)

    def stream(self):
        return iter(FakeDocSnapshot(i, d) for i, d in self._store.items())


class FakeFirestoreClient:
    def __init__(self):
        self._collections: dict[str, FakeCollectionRef] = {}

    def collection(self, name: str) -> FakeCollectionRef:
        if name not in self._collections:
            self._collections[name] = FakeCollectionRef()
        return self._collections[name]
