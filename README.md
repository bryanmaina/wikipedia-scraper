# Wikipedia World Leader Scraper

This project scrapes Wikipedia for the biographies of world leaders.

## Installation

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    python -m pip install -r requirements.txt
    ```

## Usage

To run the scraper, execute the following command:

```bash
python src/main.py
```

## Configuration

The application's configuration is managed by `hydra` and can be found in `src/conf/config.yaml`.

-   `name`: The name of the application.
-   `api`: API-related configuration.
    -   `base_url`: The base URL for the country leaders API.
    -   `max_retry`: The maximum number of retries for API requests.
    -   `user_agent`: The user agent to use for HTTP requests.
    -   `min_scrape_delay`: The minimum delay in seconds between Wikipedia scrape requests.
    -   `max_scrape_delay`: The maximum delay in seconds between Wikipedia scrape requests.

## Output

The scraper produces the following files in the `.cache/` directory:

-   `*_leaders.json`: A cached list of leaders for a specific country.
-   `*_bio.json`: A cached biography for a specific leader.
-   `leaders.json`: A consolidated JSON file containing all leaders and their biographies.

