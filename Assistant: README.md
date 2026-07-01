# Odysseus Ingress Proxy

## Popis
Odysseus Ingress Proxy je Python aplikace, která funguje jako předním endem pro klienty a backendovou službu. Spravuje HTTP požadavky, přepisuje adresy URL a spravuje hlavičky, aby zajistila bezproblémové komunikaci mezi klientem a backendem.

Klíčové funkce:
- Přepisování adres URL pro různé cesty (api, static, login, notes, calendar, cookbook, email, memory, gallery, tasks, library, backgrounds).
- Správa hlaviček k odstranění hop-by-hop hlaviček a citlivých odpovědí hlaviček.
- Podpora streamovacích odpovědí pro efektivní zpracování velkých datových objemů.
- Integrace s FastAPI pro správu HTTP požadavků.

## Rychlý Start
1. **Klonujte repozitář:**
   ```bash
   git clone https://github.com/yourusername/odysseus.git
   ```

2. **Přejděte do adresáře projektu:**
   ```bash
   cd odysseus
   ```

3. **Nainstalujte závislosti (pokud jsou nějaké):**
   Ujistěte se, že máte nainstalovaný Python a pip. Potom nainstalujte požadované balíčky:
   ```bash
   pip install fastapi httpx uvicorn
   ```

4. **Spusťte aplikaci:**
   Spusťte proxy server pomocí Uvicorn:
   ```bash
   uvicorn odysseus.ingress_proxy:proxy_app --reload
   ```

5. **Přístup k službě:**
   Otevřete webový prohlížeč nebo použijte nástroj jako `curl` pro přístup ke službě prostřednictvím proxy. Proxy přesměruje požadavky na backendovou službu běžící na `http://127.0.0.1:7000`.

## Konfigurace
- **BACKEND**: Adresa URL backendové služby může být nakonfigurována změnou proměnné `BACKEND` v `odysseus/ingress_proxy.py`.
- **HOP_BY_HOP_HEADERS** a **DROP_RESPONSE_HEADERS**: Tyto sady definují, které hlavičky by měly být odstraněny z požadavku a odpovědi, resp.

## Přispěvání
Příspěvky jsou vítány! Forkněte repozitář a předložte pull request s vašimi změnami. Ujistěte se, že dodržujete existující kódový styl a přidejte vhodné testy.

## Licenze
Tento projekt je licencován pod MIT licencí. Podrobnosti naleznete v souboru [LICENSE](LICENSE).
