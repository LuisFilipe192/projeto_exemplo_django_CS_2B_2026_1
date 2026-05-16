import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class GarageViewE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:8000/forum/"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_busca(self):
        driver = self.driver
        driver.get(self.base_url)
        busca = driver.find_element(By.NAME, "q")
        busca.send_keys("fiat")
        busca.send_keys(Keys.RETURN)
        self.assertIn("fiat", driver.page_source.lower())

    def test_02_filtro_preco(self):
        driver = self.driver
        driver.get(self.base_url)
        min_price = driver.find_element(By.NAME, "min_price")
        max_price = driver.find_element(By.NAME, "max_price")
        min_price.clear()
        max_price.clear()
        min_price.send_keys("100")
        max_price.send_keys("100000")
        driver.find_element(By.XPATH, "//button[contains(text(),'Aplicar')]").click()
        self.assertTrue("Preço mínimo" in driver.page_source)

    def test_03_criar_anuncio(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element(By.LINK_TEXT, "Criar anúncio").click()
        driver.find_element(By.ID, "titulo").send_keys("Teste E2E")
        driver.find_element(By.ID, "preco").send_keys("12345")
        driver.find_element(By.ID, "imagem_url").send_keys("")
        driver.find_element(By.ID, "descricao").send_keys("Descrição do teste E2E")
        driver.find_element(By.ID, "vendedor").send_keys("Usuário E2E")
        driver.find_element(By.ID, "contato").send_keys("11 90000-0000")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Salvar e publicar']").click()
        self.assertIn("Teste E2E", driver.page_source)

    def test_04_editar_anuncio(self):
        driver = self.driver
        driver.get(self.base_url)
        # Clica no anúncio criado
        driver.find_element(By.LINK_TEXT, "Teste E2E").click()
        driver.find_element(By.XPATH, "//button[contains(text(),'Editar')]").click()
        campo_titulo = driver.find_element(By.ID, "titulo")
        campo_titulo.clear()
        campo_titulo.send_keys("Teste E2E Editado")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Salvar e publicar']").click()
        self.assertIn("Teste E2E Editado", driver.page_source)

    def test_05_excluir_anuncio(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element(By.LINK_TEXT, "Teste E2E Editado").click()
        excluir_btn = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Excluir']")
        excluir_btn.click()
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)
        driver.get(self.base_url)
        self.assertNotIn("Teste E2E Editado", driver.page_source)

    def test_06_perfil(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element(By.LINK_TEXT, "Perfil").click()
        self.assertIn("Perfil do Usuário", driver.page_source)

if __name__ == "__main__":
    unittest.main()
