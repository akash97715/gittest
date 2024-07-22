[11:09 AM] Deep, Akash (External)
"""Util that calls Tavily Search API.
 
In order to set this up, follow instructions at:
https://docs.tavily.com/docs/tavily-api/introduction
"""
 
import json
from typing import Dict, List, Optional
 
import aiohttp
import requests
from langchain_core.pydantic_v1 import BaseModel, Extra, SecretStr, root_validator
from langchain_core.utils import get_from_dict_or_env
 
TAVILY_API_URL = "https://api.tavily.com"
 
 
class TavilySearchAPIWrapper(BaseModel):
    """Wrapper for Tavily Search API."""
 
    tavily_api_key: SecretStr
 
    class Config:
        """Configuration for this pydantic object."""
 
        extra = Extra.forbid
 
    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and endpoint exists in environment."""
        tavily_api_key = get_from_dict_or_env(
            values, "tavily_api_key", "TAVILY_API_KEY"
        )
        values["tavily_api_key"] = tavily_api_key
 
        return values
 
    def raw_results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
    ) -> Dict:
        params = {
            "api_key": self.tavily_api_key.get_secret_value(),
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
        }
        response = requests.post(
            # type: ignore
            f"{TAVILY_API_URL}/search",
            json=params,
        )
        response.raise_for_status()
        return response.json()
 
    def results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
    ) -> List[Dict]:
        """Run query through Tavily Search and return metadata.
 
        Args:
            query: The query to search for.
            max_results: The maximum number of results to return.
            search_depth: The depth of the search. Can be "basic" or "advanced".
            include_domains: A list of domains to include in the search.
            exclude_domains: A list of domains to exclude from the search.
            include_answer: Whether to include the answer in the results.
            include_raw_content: Whether to include the raw content in the results.
            include_images: Whether to include images in the results.
        Returns:
            query: The query that was searched for.
            follow_up_questions: A list of follow up questions.
            response_time: The response time of the query.
            answer: The answer to the query.
            images: A list of images.
            results: A list of dictionaries containing the results:
                title: The title of the result.
                url: The url of the result.
                content: The content of the result.
                score: The score of the result.
                raw_content: The raw content of the result.
        """
        raw_search_results = self.raw_results(
            query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
        )
        return self.clean_results(raw_search_results["results"])
 
    async def raw_results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
    ) -> Dict:
        """Get results from the Tavily Search API asynchronously."""
 
        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "api_key": self.tavily_api_key.get_secret_value(),
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_domains": include_domains,
                "exclude_domains": exclude_domains,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{TAVILY_API_URL}/search", json=params) as res:
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        raise Exception(f"Error {res.status}: {res.reason}")
 
        results_json_str = await fetch()
        return json.loads(results_json_str)
 
    async def results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
    ) -> List[Dict]:
        results_json = await self.raw_results_async(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
        )
        return self.clean_results(results_json["results"])
 
    def clean_results(self, results: List[Dict]) -> List[Dict]:
        """Clean results from Tavily Search API."""
        clean_results = []
        for result in results:
            clean_results.append(
                {
                    "url": result["url"],
                    "content": result["content"],
                }
            )
        return clean_results
 
Introduction | Tavily AI
Tavily Search API is a search engine optimized for LLMs and RAG, aimed at efficient, quick and persistent search results. Unlike other search APIs such as Serp or Google, Tavily focuses on optimizi...
 
[11:10 AM] Deep, Akash (External)
"""Tool for the Tavily search API."""
 
from typing import Dict, List, Optional, Type, Union
 
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
 
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
 
 
class TavilyInput(BaseModel):
    """Input for the Tavily tool."""
 
    query: str = Field(description="search query to look up")
 
 
class TavilySearchResults(BaseTool):
    """Tool that queries the Tavily Search API and gets back json.
 
    Setup:
        Install ``langchain-openai`` and ``tavily-python``, and set environment variable ``TAVILY_API_KEY``.
 
        .. code-block:: bash
 
            pip install -U langchain-openai
            export TAVILY_API_KEY="your-api-key"
 
    Instantiate:
 
        .. code-block:: python
 
            from langchain_community.tools.tavily_search import TavilySearchResults
 
            tool = TavilySearchResults(
                # max_results= 5
                # search_depth = "advanced"
                # include_domains = []
                # exclude_domains = []
                # include_answer = False
                # include_raw_content = False
                # include_images = False
            )
 
    Invoke:
 
        .. code-block:: python
 
            tool = TavilySearchResults(max_results=3)
            tool.invoke("What is the weather?")
 
        .. code-block:: python
 
            [{'url': 'https://www.weatherapi.com/',
            'content': "{'location': {'name': 'Current', 'region': 'Harbour Island', 'country': 'Bahamas', 'lat': 25.43, 'lon': -76.78, 'tz_id': 'America/Nassau', 'localtime_epoch': 1718077801, 'localtime': '2024-06-10 23:50'}, 'current': {'last_updated_epoch': 1718077500, 'last_updated': '2024-06-10 23:45', 'temp_c': 27.9, 'temp_f': 82.1, 'is_day': 0, 'condition': {'text': 'Patchy rain nearby', 'icon': '//cdn.weatherapi.com/weather/64x64/night/176.png', 'code': 1063}, 'wind_mph': 14.5, 'wind_kph': 23.4, 'wind_degree': 161, 'wind_dir': 'SSE', 'pressure_mb': 1014.0, 'pressure_in': 29.94, 'precip_mm': 0.01, 'precip_in': 0.0, 'humidity': 88, 'cloud': 74, 'feelslike_c': 33.1, 'feelslike_f': 91.5, 'windchill_c': 27.9, 'windchill_f': 82.1, 'heatindex_c': 33.1, 'heatindex_f': 91.5, 'dewpoint_c': 25.6, 'dewpoint_f': 78.1, 'vis_km': 10.0, 'vis_miles': 6.0, 'uv': 1.0, 'gust_mph': 20.4, 'gust_kph': 32.9}}"},
            {'url': 'https://www.localconditions.com/weather-ninnescah-kansas/67069/',
            'content': 'The following chart reports what the hourly Ninnescah, KS temperature has been today, from 12:56 AM to 3:56 AM Tue, May 21st 2024. The lowest temperature reading has been 73.04 degrees fahrenheit at 3:56 AM, while the highest temperature is 75.92 degrees fahrenheit at 12:56 AM. Ninnescah KS detailed current weather report for 67069 in Kansas.'},
            {'url': 'https://www.weather.gov/forecastmaps/',
            'content': 'Short Range Forecasts. Short range forecast products depicting pressure patterns, circulation centers and fronts, and types and extent of precipitation. 12 Hour | 24 Hour | 36 Hour | 48 Hour.'}]
 
        When converting ``TavilySearchResults`` to a tool, you may want to not return all of the content resulting from ``invoke``. You can select what parts of the response to keep depending on your use case.
 
    """  # noqa: E501
 
    name: str = "tavily_search_results_json"
    description: str = (
        "A search engine optimized for comprehensive, accurate, and trusted results. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: TavilySearchAPIWrapper = Field(default_factory=TavilySearchAPIWrapper)  # type: ignore[arg-type]
    max_results: int = 5
    """Max search results to return, default is 5"""
    search_depth: str = "advanced"
    '''The depth of the search. It can be "basic" or "advanced"'''
    include_domains: List[str] = []
    """A list of domains to specifically include in the search results. Default is None, which includes all domains."""  # noqa: E501
    exclude_domains: List[str] = []
    """A list of domains to specifically exclude from the search results. Default is None, which doesn't exclude any domains."""  # noqa: E501
    include_answer: bool = False
    """Include a short answer to original query in the search results. Default is False."""  # noqa: E501
    include_raw_content: bool = False
    """Include cleaned and parsed HTML of each site search results. Default is False."""
    include_images: bool = False
    """Include a list of query related images in the response. Default is False."""
    args_schema: Type[BaseModel] = TavilyInput
 
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[List[Dict], str]:
        """Use the tool."""
        try:
            return self.api_wrapper.results(
                query,
                self.max_results,
                self.search_depth,
                self.include_domains,
                self.exclude_domains,
                self.include_answer,
                self.include_raw_content,
                self.include_images,
            )
        except Exception as e:
            return repr(e)
 
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Union[List[Dict], str]:
        """Use the tool asynchronously."""
        try:
            return await self.api_wrapper.results_async(
                query,
                self.max_results,
                self.search_depth,
                self.include_domains,
                self.exclude_domains,
                self.include_answer,
                self.include_raw_content,
                self.include_images,
            )
        except Exception as e:
            return repr(e)
 
 
class TavilyAnswer(BaseTool):
    """Tool that queries the Tavily Search API and gets back an answer."""
 
    name: str = "tavily_answer"
    description: str = (
        "A search engine optimized for comprehensive, accurate, and trusted results. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. "
        "This returns only the answer - not the original source data."
    )
    api_wrapper: TavilySearchAPIWrapper = Field(default_factory=TavilySearchAPIWrapper)  # type: ignore[arg-type]
    args_schema: Type[BaseModel] = TavilyInput
 
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[List[Dict], str]:
        """Use the tool."""
        try:
            return self.api_wrapper.raw_results(
                query,
                max_results=5,
                include_answer=True,
                search_depth="basic",
            )["answer"]
        except Exception as e:
            return repr(e)
 
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Union[List[Dict], str]:
        """Use the tool asynchronously."""
        try:
            result = await self.api_wrapper.raw_results_async(
                query,
                max_results=5,
                include_answer=True,
                search_depth="basic",
            )
            return result["answer"]
        except Exception as e:
            return repr(e)
 
 
[11:10 AM] Deep, Akash (External)
import json
from typing import Any, Dict, Optional, Type
import boto3
from langchain_core.pydantic_v1 import BaseModel
#from api.agent_state import AgentState
from pydantic import BaseModel, create_model, ValidationError, Field
from fastapi import HTTPException
from datamodel_code_generator import InputFileType, generate, DataModelType
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import sys
 
class LambdaWrapper(BaseModel):
    """Wrapper for AWS Lambda SDK."""
    lambda_client: Any  #: :meta private:
    function_name: Optional[str] = None
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None
    is_conditional_fn: bool = False
    input_schema: Type[BaseModel] = None
    output_schema: Type[BaseModel] = None
       
    @classmethod
    def create(cls, function_name: str, tool_name: str, tool_description: str, region: str, is_conditional: bool = False, input_schema: Type[BaseModel] = None, output_schema: Type[BaseModel] = None):
        lambda_client = boto3.client("lambda", region_name=region)
        return cls(
            lambda_client=lambda_client,
            function_name=function_name,
            awslambda_tool_name=tool_name,
            awslambda_tool_description=tool_description,
            is_conditional_fn=is_conditional,
            input_schema=input_schema,
            output_schema=output_schema
        )
 
    def set_is_conditional(self, is_conditional: bool = False) -> None:
        self.is_conditional_fn = is_conditional
 
    def run(self, state: AgentState) -> str:
        res = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": state}),
        )
        try:
            payload_stream = res["Payload"]
            payload_string = payload_stream.read().decode("utf-8")
            response = json.loads(payload_string)
        except StopIteration:
            return "Failed to parse response from Lambda"
        if response is None or response == "":
            return "Request failed."
        else:
            if self.is_conditional_fn:
                print(f"{self.awslambda_tool_name} returned {response['body']}")
                return str(response["body"])
            updated_payload = state["payload"]
            if updated_payload is not None:
                updated_payload.update(response)
            else:
                updated_payload = response
            return {"messages": [], "payload": updated_payload }
 
