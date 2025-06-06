
from ccm_benchmate.knowledge_base.knowledge_base import KnowledgeBase

class Project:
    def __init__(self, description, tools=None, knowledge_base=None):
        self.description = description
        self.tools = tools
        self.knowledge_base = knowledge_base
        #TODO dynamic imports

    def add_tool(self, tool):
        pass

    def remove_tool(self, tool):
        pass

    def list_tools(self):
        """
        List all tools in the project.
        :return: A list of tool names.
        """
        if self.tools is None:
            return []
        return [tool.name for tool in self.tools]

    def query_tool(self, tool, id):
        pass




    