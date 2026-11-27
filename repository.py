class HealthPostRepository:
    def __init__(self, connection_factory):
        self._connection_factory = connection_factory

    def authenticate(self, username, password):
        with self._connection_factory() as db:
            row = db.execute(
                "SELECT 1 FROM users WHERE username=? AND password=?",
                (username, password),
            ).fetchone()
        return row is not None

    def dispense(self, patient_id, medicine_id, quantity):
        with self._connection_factory() as db:
            row = db.execute(
                "SELECT stock FROM medicines WHERE id=?", (medicine_id,)
            ).fetchone()
            if row is None or row[0] < quantity:
                return False
            db.execute(
                "UPDATE medicines SET stock=stock-? WHERE id=?",
                (quantity, medicine_id),
            )
            db.execute(
                "INSERT INTO visits(patient_id,medicine_id,quantity) VALUES(?,?,?)",
                (patient_id, medicine_id, quantity),
            )
        return True
