class AuthenticationService:
    def __init__(self, repository):
        self._repository = repository

    def authenticate(self, username, password):
        return self._repository.authenticate(username, password)


class DispensingService:
    def __init__(self, repository):
        self._repository = repository

    def dispense(self, patient_id, medicine_id, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        return self._repository.dispense(patient_id, medicine_id, quantity)
