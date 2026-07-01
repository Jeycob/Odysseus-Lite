# Odysseus Ingress Proxy

## Description
Odysseus Ingress Proxy is a Python application that acts as an intermediary between clients and a backend service. It handles HTTP requests, rewrites URLs, and manages headers to ensure seamless communication between the client and the backend.

Key Features:
- URL rewriting for various paths (api, static, login, notes, calendar, cookbook, email, memory, gallery, tasks, library, backgrounds).
- Header management to remove hop-by-hop headers and sensitive response headers.
- Support for streaming responses to handle large payloads efficiently.
- Integration with FastAPI for handling HTTP requests.

## Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/odysseus.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd odysseus
   ```

3. **Install dependencies (if any):**
   Ensure you have Python and pip installed. Then, install the required packages:
   ```bash
   pip install fastapi httpx uvicorn
   ```

4. **Run the application:**
   Start the proxy server using Uvicorn:
   ```bash
   uvicorn odysseus.ingress_proxy:proxy_app --reload
   ```

5. **Access the service:**
   Open your web browser or use a tool like `curl` to access the service through the proxy. The proxy will forward requests to the backend service running on `http://127.0.0.1:7000`.

## Configuration
- **BACKEND**: The URL of the backend service can be configured by changing the `BACKEND` variable in `odysseus/ingress_proxy.py`.
- **HOP_BY_HOP_HEADERS** and **DROP_RESPONSE_HEADERS**: These sets define which headers should be removed from the request and response, respectively.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Make sure to follow the existing code style and add appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
Small change
