from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests
import time
import concurrent.futures

PUSHGATEWAY_HOST = "localhost:9091"
JOB_NAME = "your_job"
HOST_NAME = "your_host"

url_prefix = "some_prefix"

URLS = [
    "/some_resource",
    "/some_resource",
    "/some_resource",
    "/some_resource"
]

WARMUP_REQUESTS = 5
CONCURRENT_REQUESTS = [20, 20, 20]
CONCURRENT_DELAYS = [0.5, 0.1, 0.05]

# Create a Prometheus registry and a Gauge metric for the average response time
registry = CollectorRegistry()
g_avg_response_time = Gauge('page_avg_response_time', 'Average response time for a page', ['label_1', 'label_2', 'label_3', 'label_4', 'label_5', 'label_6'], registry=registry)

def get_status(url):
    resp = requests.get(url=url)
    return resp

# Warm-up phase
print("Starting warm-up phase...")
print(f"Sending warm-up request to {URLS[0]}...")
for i in range(WARMUP_REQUESTS):
    response = requests.get(url_prefix + URLS[0])

# Concurrent requests
for i in range(len(CONCURRENT_REQUESTS)):
    requests_count = CONCURRENT_REQUESTS[i]
    delay = CONCURRENT_DELAYS[i]
    
    print(f"Starting concurrent requests with {requests_count} requests and {delay} second delay...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for url in URLS:
            futures = []

            url_path = url.split("/")[-1]
            if (url_path == "en"):
                url_path = "home"

            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Concurrent - Resource: {url_path} - Delay: {delay}s")
            total_response_time = 0.0
            tm1 = time.perf_counter()
            for j in range(requests_count):
                futures.append(executor.submit(get_status, url=url_prefix + url))
                time.sleep(delay)

            tm2 = time.perf_counter()
            print(f'Total time elapsed: {tm2-tm1:0.2f} seconds')

            for future in concurrent.futures.as_completed(futures):
                total_response_time += future.result().elapsed.total_seconds()

            avg_response_time = total_response_time / requests_count

            print(f"Average response time for {url} - {delay} delay: {avg_response_time} seconds")
            # Set the value of the Gauge metric for the average response time
            g_avg_response_time.labels("label_value_1", "label_value_2", "label_value_3", "label_value_4", "label_value_5", "label_value_6").set(avg_response_time)
            # Push the metric to the Pushgateway
            push_to_gateway(f"http://{PUSHGATEWAY_HOST}/",JOB_NAME, registry=registry)

print("All requests completed!")
