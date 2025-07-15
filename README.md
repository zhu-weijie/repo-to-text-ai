## Development

### Prerequisites

- [Docker](https'://www.docker.com/get-started')
- [Docker Compose](https://docs.docker.com/compose/install/)

### Getting Started

1.  **Build the Docker container:**
    This command builds the Docker image based on the `Dockerfile`.

    ```bash
    docker compose build
    ```

2.  **Start the development container:**
    This command starts the container in detached mode (in the background).

    ```bash
    docker compose up -d
    ```

3.  **Access the container shell:**
    This gives you a bash shell inside the running container, where the full development environment is available.

    ```bash
    docker compose exec dev bash
    ```

4.  **Stopping the container:**
    When you are finished, you can stop the container.

    ```bash
    docker compose down
    ```
