from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig
from google.genai import types
from  google.adk.tools.mcp_tool.mcp_toolset  import StdioServerParameters, StdioConnectionParams

from google.adk.tools import google_search 

from utils.extensions import MCPToolSetWithSchemaAccess
from utils.tools import store_file, get_file_link, list_files
from utils.callbacks import bmc_trim_llm_request, bac_setup_state_variable

import logging
import os

from typing import TextIO
import sys

logging.basicConfig(
    level=logging.INFO)

if os.environ.get("MINIMAL_LOGGING","N") == "Y":
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.ERROR)


def get_all_tools():
  """Get Tools from All MCP servers"""
  logging.info("Attempting to connect to MCP servers...")
  secops_tools = None
  gti_tools = None
  secops_soar_tools = None

  timeout = float(os.environ.get("STDIO_PARAM_TIMEOUT","60.0"))
  
  uv_dir_prefix="../server"
  env_file_path = "../../../app/.env"

  if os.environ.get("REMOTE_RUN","N") == "Y":
    env_file_path="/tmp/.env"
    uv_dir_prefix="./server"

  if os.environ.get("AE_RUN","N") == "Y":
    env_file_path="../../../app/.env"
    uv_dir_prefix="./server"

  logging.info(f"Using Env File Path - {env_file_path}, Current directory is - {os.getcwd()}, uv_dir_prefix is - {uv_dir_prefix}")

  # required temporarily for https://github.com/google/adk-python/issues/1024
  errlog_ae : TextIO = sys.stderr
  if os.environ.get("AE_RUN","N") == "Y":
    errlog_ae = None

  if os.environ.get("LOAD_SECOPS_MCP") == "Y":
    secops_tools = MCPToolSetWithSchemaAccess(
                  connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                                  command='uv',
                                  args=[ "--directory",
                                          uv_dir_prefix + "/secops/secops_mcp",
                                          "run",
                                          "--env-file",
                                          env_file_path,
                                          "server.py"
                                        ]
                    ),
                  timeout=timeout),
                tool_set_name="secops_mcp",
                errlog=errlog_ae
                )

  if os.environ.get("LOAD_GTI_MCP") == "Y":
    gti_tools = MCPToolSetWithSchemaAccess(
                  connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                                  command='uv',
                                  args=[ "--directory",
                                          uv_dir_prefix + "/gti/gti_mcp",
                                          "run",
                                          "--env-file",
                                          env_file_path,
                                          "server.py"
                                        ]
                    ),
                  timeout=timeout),
                tool_set_name="gti_mcp",
                errlog=errlog_ae
                )    


  if os.environ.get("LOAD_SECOPS_SOAR_MCP") == "Y":
    secops_soar_tools = MCPToolSetWithSchemaAccess(
                  connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                                  command='uv',
                                  args=[ "--directory",
                                          uv_dir_prefix + "/secops-soar/secops_soar_mcp",
                                          "run",
                                          "--env-file",
                                          env_file_path,
                                          "server.py",
                                          "--integrations",
                                          os.environ.get("SECOPS_INTEGRATIONS","CSV,OKTA")
                                        ]
                    ),
                  timeout=timeout),
                tool_set_name="secops_soar_mcp",
                errlog=errlog_ae
                )    

  logging.info("MCP Toolsets created successfully.")
  return [secops_tools,gti_tools,secops_soar_tools]

def create_agent():
  tools:any = [item for item in get_all_tools() if item is not None]
  tools.append(store_file)
  tools.append(get_file_link)
  tools.append(list_files)
  tools.append(google_search)

  agent = Agent(
      model=os.environ.get("GOOGLE_MODEL"), 
      name="gus_security_agent",
      instruction=os.environ.get("DEFAULT_PROMPT"),
      tools=tools,
      before_model_callback=bmc_trim_llm_request,
      before_agent_callback=bac_setup_state_variable,
      # sub_agents=[ADD SUB AGENTS HERE],
      description="You are the gus_security_agent."

  )
  return agent

root_agent = create_agent()