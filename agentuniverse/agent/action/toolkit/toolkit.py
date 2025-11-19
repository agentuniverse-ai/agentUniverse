# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy
from typing import List, Optional, Any

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class Toolkit(ComponentBase):
    """Toolkit class for managing collections of tools in agentUniverse framework.
    
    Toolkit is a component that groups related tools together, providing a
    convenient way to manage and access multiple tools as a single unit.
    This is particularly useful for organizing tools by functionality or
    domain-specific use cases.
    
    Attributes:
        name (str): The name of the toolkit. Defaults to empty string.
        description (Optional[str]): Optional description of the toolkit's 
            functionality.
        include (Optional[List[str]]): List of tool names included in this toolkit.
            Defaults to empty list.
        as_mcp_tool (Any): Optional MCP (Model Context Protocol) tool configuration.
    
    Example:
        >>> toolkit = Toolkit()
        >>> toolkit.name = "web_tools"
        >>> toolkit.include = ["web_search", "url_reader", "html_parser"]
        >>> 
        >>> # Get tool names
        >>> tool_names = toolkit.tool_names
        >>> print(f"Tools: {tool_names}")
        >>> 
        >>> # Get tool descriptions
        >>> descriptions = toolkit.tool_descriptions
        >>> for desc in descriptions:
        ...     print(desc)
    
    Note:
        The `func_call_list` property raises NotImplementedError and must be
        implemented by subclasses that need function call capabilities.
    """

    name: str = ""
    description: Optional[str] = None
    include: Optional[List[str]] = []
    as_mcp_tool: Any = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.TOOLKIT, **kwargs)

    @property
    def tool_names(self) -> list:
        """Return all tool names in toolkit.
        
        Returns a deep copy of the include list to prevent external modification
        of the internal tool list.
        
        Returns:
            list: List of tool names included in this toolkit.
        
        Example:
            >>> toolkit = Toolkit()
            >>> toolkit.include = ["search_tool", "calculator"]
            >>> names = toolkit.tool_names
            >>> print(names)  # ['search_tool', 'calculator']
        """
        return copy.deepcopy(self.include)


    @property
    def tool_descriptions(self) -> list:
        """Return all tools' descriptions in toolkit.
        
        Retrieves the tool instances for all tools in the include list and
        formats their names and descriptions into a readable string format.
        
        Returns:
            list: List of formatted tool descriptions. Each description includes
                the tool name and description in a standardized format.
        
        Example:
            >>> toolkit = Toolkit()
            >>> toolkit.include = ["search_tool", "calculator"]
            >>> descriptions = toolkit.tool_descriptions
            >>> for desc in descriptions:
            ...     print(desc)
            # Output:
            # tool name:search_tool
            # tool description:Tool for searching the web
            # 
            # tool name:calculator
            # tool description:Tool for mathematical calculations
        """
        tools = [ToolManager().get_instance_obj(tool_name, new_instance=False) for tool_name in self.include]
        tools_descriptions = [f'tool name:{tool.name}\ntool description:{tool.description}\n' for tool in tools]
        return tools_descriptions

    @property
    def func_call_list(self) -> list:
        """Return the function call list for tools in this toolkit.
        
        This property should be implemented by subclasses that need to provide
        function call capabilities for the tools in the toolkit.
        
        Returns:
            list: List of function call objects for tools in this toolkit.
        
        Raises:
            NotImplementedError: This method must be implemented by subclasses
                that require function call functionality.
        
        Note:
            This is an abstract property that must be implemented by concrete
            toolkit subclasses that need function call capabilities.
        """
        raise NotImplementedError

    def get_instance_code(self) -> str:
        """Return the full name of the toolkit.
        
        Generates a unique identifier for this toolkit instance by combining
        the application name, component type, and toolkit name.
        
        Returns:
            str: Full name in the format 'appname.toolkit.toolkit_name'.
        
        Example:
            >>> toolkit = Toolkit()
            >>> toolkit.name = "web_tools"
            >>> code = toolkit.get_instance_code()
            >>> print(code)  # 'myapp.toolkit.web_tools'
        """
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'Toolkit':
        """Initialize the Toolkit by the ComponentConfiger object.
        
        This method configures the Toolkit instance using the provided
        configuration object. It sets all configuration attributes and
        calls the internal initialization method.
        
        Args:
            component_configer (ComponentConfiger): A configuration object 
                containing Toolkit configuration information including name,
                description, and include list.
        
        Returns:
            Toolkit: The configured Toolkit instance (self).
        
        Example:
            >>> config = ComponentConfiger()
            >>> config.name = "web_tools"
            >>> config.description = "Tools for web operations"
            >>> config.include = ["web_search", "url_reader"]
            >>> toolkit = Toolkit()
            >>> configured_toolkit = toolkit.initialize_by_component_configer(config)
        """
        try:
            for key, value in component_configer.configer.value.items():
                if key != 'metadata':
                    setattr(self, key, value)
        except Exception as e:
            print(f"Error during configuration initialization: {str(e)}")
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if hasattr(component_configer, "include"):
            self.include = component_configer.include
        self._initialize_by_component_configer(component_configer)
        return self
