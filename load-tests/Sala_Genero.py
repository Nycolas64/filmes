import uuid
from locust import HttpUser, task, between
from faker import Faker

fake = Faker('pt_BR')

class SalaGeneroUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.token = None
        self.sala_id = None
        self.genero_id = None
        
        test_email = f"load_{uuid.uuid4().hex[:6]}@test.com"
        test_password = "senha_de_teste_123"

        # TENTATIVA 1: Registrar com /auth/register
        reg_payload = {"nome": "Tester", "email": test_email, "password": test_password}
        self.client.post("/auth/register", json=reg_payload)

        # TENTATIVA 1: Login com /auth/login
        login_data = {"email": test_email, "password": test_password}
        response = self.client.post("/auth/login", json=login_data)
        
        # Se falhar, tenta com /api/auth/login (alguns projetos usam prefixo)
        if response.status_code == 404:
            print("Tentando login com prefixo /api...")
            response = self.client.post("/api/auth/login", json=login_data)

        if response.status_code == 200:
            self.token = response.json().get("token")
            print(f"🔑 TOKEN OBTIDO!")
            self.prepare_initial_data()
        else:
            print(f"❌ FALHA NO LOGIN: {response.status_code} na URL {response.url}")

    def prepare_initial_data(self):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        # Criar Sala
        self.client.post("/api/salas", json={"nome": "Inicial", "capacidade": 10}, headers=headers)
        # Criar Genero
        self.client.post("/api/generos", json={"nome": "Inicial"}, headers=headers)

    @task
    def test_sala(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/salas", headers=headers, name="GET /api/salas")

    @task
    def test_genero(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/generos", headers=headers, name="GET /api/generos")
