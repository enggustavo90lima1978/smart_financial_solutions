"""Ferramentas para formatação da saída do agente"""

import json

from langchain.tools import tool


@tool('json_output_parser', return_direct=True)
def json_output_parser(response: str, graph_id: str = '') -> str:
    """Use this tool to create a valid JSON output after generating the response and as last step. This function receives the response and graph_id values, the graph_id parameter is optional. A string json formatted output is returned."""

    return json.dumps({'response': response, 'graph_id': graph_id})
