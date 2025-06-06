# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-nested-blocks, too-many-branches, too-many-statements
# pylint: disable=too-many-positional-arguments, too-many-arguments
# pylint: disable=unnecessary-lambda, protected-access, consider-using-f-string, wrong-import-order

from collections.abc import Callable
import json
import requests

ZEPHYR_API_URL = "https://api.zephyrscale.smartbear.com/v2"


class ZephyrScaleApiService():

    def __init__(self, zephyr_api: str, cache_results: bool=True):
        self.cache_results = cache_results
        self.cache = {}

        if zephyr_api is None:
            raise ValueError("Zephyr Scale API Key not set")
        self.zephyr_api = zephyr_api
        self.headers = {"Authorization": f"Bearer {self.zephyr_api}"}

    def clear_cache(self):
        self.cache = {}

    def check_cache(self, key: str, value_getter: Callable) -> any:
        if not self.cache_results:
            return value_getter()

        cache_key = key
        value = self.cache.get(cache_key) or value_getter()
        self.cache[cache_key] = value

        return value

    def get_test_cases(self, issue_key: str):

        return self.check_cache(
            f"test-case:{issue_key}",
            lambda: json.loads(
                requests.get(
                    f"{ZEPHYR_API_URL}/issuelinks/{issue_key}/testcases",
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_test_case(self, test_case_url: str):
        if not test_case_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return self.check_cache(
            f"test-case-url:{test_case_url}",
            lambda: json.loads(
                requests.get(
                    test_case_url,
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_test_case_status(self, test_case_status_url: str):
        if not test_case_status_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return self.check_cache(
            f"test-case-status:{test_case_status_url}",
            lambda: json.loads(
                requests.get(
                    test_case_status_url,
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_project(self, project_url: str):
        if not project_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return self.check_cache(
            f"test-project:{project_url}",
            lambda: json.loads(
                requests.get(
                    project_url,
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_folder(self, folder_url: str):
        if not folder_url.startswith(ZEPHYR_API_URL):
            raise ValueError("Invalid host or differs from Zephyr")

        return self.check_cache(
            f"test-folder:{folder_url}",
            lambda: json.loads(
                requests.get(
                    folder_url,
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_test_case_latest_executions(self, test_case_key: str):

        return self.check_cache(
            f"test-case-latest-execution:{test_case_key}",
            lambda: json.loads(
                requests.get(
                    f"{ZEPHYR_API_URL}/testexecutions?testCase={test_case_key}&onlyLastExecutions=true",
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_test_case_execution_status(self, test_case_execution_status_url: str):

        return self.check_cache(
            f"test-case-execution-status:{test_case_execution_status_url}",
            lambda: json.loads(
                requests.get(
                    test_case_execution_status_url,
                    headers=self.headers,
                    timeout=5
                ).text
            )
        )

    def get_test_cycles(self):

        def get():
            response = json.loads(
                requests.get(
                    f"{ZEPHYR_API_URL}/testcycles?maxResults=50",
                    headers=self.headers,
                    timeout=5
                ).text
            )
            results = response['values']
            while not response['isLast']:
                response = json.loads(
                    requests.get(
                        response['next'],
                        headers=self.headers,
                        timeout=5
                    ).text
                )
                results.append(response['values'])

            return results

        return self.check_cache("test-cycles filter", get)

    def get_test_cycle_filter(self, test_cycle_filter: Callable[[any], bool]):

        def get(test_cycle_filter):
            response = json.loads(
                requests.get(
                    f"{ZEPHYR_API_URL}/testcycles?maxResults=50",
                    headers=self.headers,
                    timeout=5
                ).text
            )
            results = response['values']

            for result in response['values']:
                if test_cycle_filter(result):
                    return result

            while not response['isLast']:
                response = json.loads(
                    requests.get(
                        response['next'],
                        headers=self.headers,
                        timeout=5
                    ).text
                )

                for result in response['values']:
                    if test_cycle_filter(result):
                        return result

                results.append(response['values'])

            return None

        return self.check_cache(
            f"test-cycle-filter{str(test_cycle_filter)}",
            lambda: get(test_cycle_filter)
        )

    def get_test_cycle_test_executions(self, test_cycle_key: str):

        def get():
            response = json.loads(
                requests.get(
                    f"{ZEPHYR_API_URL}/testexecutions/?maxResults=50&testCycle={test_cycle_key}",
                    headers=self.headers,
                    timeout=5
                ).text
            )
            results = response['values']
            while not response['isLast']:
                response = json.loads(
                    requests.get(
                        response['next'],
                        headers=self.headers,
                        timeout=5
                    ).text
                )
                results.append(response['values'])

            return results

        return self.check_cache(f"test_cycle_test_executions: {test_cycle_key}", get)
