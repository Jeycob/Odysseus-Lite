# Odysseus Ingress Proxy

## English

### Description
Odysseus Ingress Proxy is a Python application that acts as an intermediary between clients and a backend service. It handles HTTP requests, rewrites URLs, and manages headers to keep communication between the client and backend service seamless.

### Key Features
- URL rewriting for paths such as api, static, login, notes, calendar, cookbook, email, memory, gallery, tasks, library, and backgrounds.
- Header management for removing hop-by-hop headers and sensitive response headers.
- Streaming response support for large payloads.
- FastAPI integration for handling HTTP requests.

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/odysseus.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd odysseus
   ```

3. **Install dependencies:**
   Make sure Python and pip are installed, then install the required packages:
   ```bash
   pip install fastapi httpx uvicorn
   ```

4. **Run the application:**
   Start the proxy server with Uvicorn:
   ```bash
   uvicorn odysseus.ingress_proxy:proxy_app --reload
   ```

5. **Access the service:**
   Open the service in a browser or use a tool such as `curl`. The proxy forwards requests to the backend service running at `http://127.0.0.1:7000`.

### Configuration
- **BACKEND**: The backend service URL can be configured by changing the `BACKEND` variable in `odysseus/ingress_proxy.py`.
- **HOP_BY_HOP_HEADERS** and **DROP_RESPONSE_HEADERS**: These sets define which headers should be removed from requests and responses.

### Contributing
Contributions are welcome. Please fork the repository and submit a pull request with your changes. Follow the existing code style and add appropriate tests when needed.

### License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Small change

---

## Česky

### Popis
Odysseus Ingress Proxy je Python aplikace, která funguje jako prostředník mezi klienty a backendovou službou. Zpracovává HTTP požadavky, přepisuje URL adresy a spravuje hlavičky tak, aby komunikace mezi klientem a backendovou službou probíhala hladce.

### Hlavní funkce
- Přepisování URL pro cesty jako api, static, login, notes, calendar, cookbook, email, memory, gallery, tasks, library a backgrounds.
- Správa hlaviček pro odstranění hop-by-hop hlaviček a citlivých hlaviček odpovědi.
- Podpora streamovaných odpovědí pro velké objemy dat.
- Integrace s FastAPI pro zpracování HTTP požadavků.

### Rychlý start
1. **Naklonujte repozitář:**
   ```bash
   git clone https://github.com/yourusername/odysseus.git
   ```

2. **Přejděte do adresáře projektu:**
   ```bash
   cd odysseus
   ```

3. **Nainstalujte závislosti:**
   Ujistěte se, že máte nainstalovaný Python a pip, a potom nainstalujte potřebné balíčky:
   ```bash
   pip install fastapi httpx uvicorn
   ```

4. **Spusťte aplikaci:**
   Proxy server spusťte pomocí Uvicornu:
   ```bash
   uvicorn odysseus.ingress_proxy:proxy_app --reload
   ```

5. **Otevřete službu:**
   Otevřete službu v prohlížeči nebo použijte nástroj jako `curl`. Proxy bude předávat požadavky backendové službě běžící na `http://127.0.0.1:7000`.

### Konfigurace
- **BACKEND**: URL backendové služby lze nastavit změnou proměnné `BACKEND` v souboru `odysseus/ingress_proxy.py`.
- **HOP_BY_HOP_HEADERS** a **DROP_RESPONSE_HEADERS**: Tyto množiny určují, které hlavičky se mají odstraňovat z požadavků a odpovědí.

### Přispívání
Příspěvky jsou vítané. Forkněte repozitář a pošlete pull request se svými změnami. Dodržujte existující styl kódu a podle potřeby přidejte vhodné testy.

### Licence
Projekt je licencován pod licencí MIT. Podrobnosti najdete v souboru [LICENSE](LICENSE).

Malá změna
