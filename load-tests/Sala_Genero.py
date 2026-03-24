import uuid
from locust import HttpUser, task, between
from faker import Faker

# Inicializa o gerador de dados aleatórios
fake = Faker('pt_BR')

class SalaGeneroUser(HttpUser):
    # Tempo de espera entre as requisições (1 a 2 segundos) para simular um usuário real
    wait_time = between(1, 2)

    def on_start(self):
        """ 
        Executado uma vez para cada usuário virtual.
        Realiza o registro e o login para obter o token JWT.
        """
        self.token = None
        self.sala_id = None
        self.genero_id = None
        
        # Gerar credenciais únicas para este usuário de teste
        test_email = f"load_{uuid.uuid4().hex[:6]}@test.com"
        test_password = "senha_de_teste_123"

        # 1. Registro do Usuário
        reg_payload = {
            "nome": f"Tester {fake.first_name()}",
            "email": test_email,
            "password": test_password
        }
        
        print(f"Tentando registrar usuário: {test_email}")
        self.client.post("/auth/register", json=reg_payload)

        # 2. Login para obter o Token
        login_data = {"email": test_email, "password": test_password}
        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("token")
                print(f"✅ Login realizado com sucesso!")
            else:
                # Caso o /auth/login falhe, tenta com o prefixo /api/auth/login
                with self.client.post("/api/auth/login", json=login_data, catch_response=True) as resp_api:
                    if resp_api.status_code == 200:
                        self.token = resp_api.json().get("token")
                        print(f"✅ Login realizado com sucesso (via /api/auth/login)!")
                    else:
                        print(f"❌ Falha crítica no login: {resp_api.status_code}")
                        resp_api.failure(f"Login falhou: {resp_api.status_code}")

    @task(2)
    def fluxo_sala(self):
        """ Fluxo completo de SALA: POST seguido de GET """
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}

        # 1. POST - Criar Sala
        sala_payload = {
            "nome": f"Sala {fake.word().capitalize()} {uuid.uuid4().hex[:4]}",
            "capacidade": fake.random_int(min=50, max=300)
        }
        
        with self.client.post("/api/salas", json=sala_payload, headers=headers, catch_response=True) as post_res:
            if post_res.status_code in [200, 201]:
                try:
                    # Tenta capturar o ID da sala criada
                    sala_id = post_res.json().get("id")
                    if sala_id:
                        # 2. GET - Ler o registro criado
                        self.client.get(f"/api/salas/{sala_id}", headers=headers, name="GET /api/salas/[id]")
                    post_res.success()
                except Exception:
                    post_res.success()
            else:
                post_res.failure(f"Erro ao criar Sala: {post_res.status_code}")

    @task(1)
    def fluxo_genero(self):
        """ Fluxo completo de GÊNERO: POST seguido de GET """
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}

        # 1. POST - Criar Gênero
        genero_payload = {
            "nome": f"Gênero {fake.word().capitalize()} {uuid.uuid4().hex[:4]}"
        }
        
        with self.client.post("/api/generos", json=genero_payload, headers=headers, catch_response=True) as post_res:
            if post_res.status_code in [200, 201]:
                try:
                    # Tenta capturar o ID do gênero criado
                    genero_id = post_res.json().get("id")
                    if genero_id:
                        # 2. GET - Ler o registro criado
                        self.client.get(f"/api/generos/{genero_id}", headers=headers, name="GET /api/generos/[id]")
                    post_res.success()
                except Exception:
                    post_res.success()
            else:
                post_res.failure(f"Erro ao criar Gênero: {post_res.status_code}")
