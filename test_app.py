from app import app

def test_hello_endpoint():
    client = app.test_client()
    response = client.get('/hello?name=TEST')
    assert response.status_code == 200
    assert b"Hello, TEST!" in response.data
    print("TEST UNITARIO APROBADO: Respuesta esperada recibida.")

if __name__ == '__main__':
    test_hello_endpoint()