# User Guide
************************************************
## Table of Contents

**1. Getting Started**
* 1.1 [Introduction](Concepts/Introduction.md)
* 1.2 [Installation and Initialization](Get_Start/0.Installation_and_Initialization.md)
* 1.3 [Application Project Structure and Explanation](Get_Start/1.Application_Project_Structure_and_Explanation.md)
* 1.4 [Run Your First Tutorial Example](Get_Start/2.Run_Your_First_Tutorial_Example.md)
* 1.5 [Quick Guide to Build Single Agent](Get_Start/3.Quick_Guide_to_Build_Single_Agent.md)
* 1.6 [Building Typical Multi-Agent App](Get_Start/4.Building_Typical_Multi-Agent_App.md)
* 1.7 [Creating and Using Agent Templates](Get_Start/5.Creating_and_Using_Agent_Templates.md)
* 1.8 Advanced Usage Techniques
  * 1.8.1 [Advanced Techniques: Using Memory](Get_Start/7.Advanced_Techniques-Using_Memory.md)
  * 1.8.2 [Advanced Techniques: Prompt Management](Get_Start/8.Advanced_Techniques-Prompt_Manager.md)
  * 1.8.2 [Advanced Techniques: Multimodal Agent](Get_Start/9.Advanced_Techniques-Multimodal_Agents.md)
  
**2. Principle Introduction**

* 2.1 Framework Principles
* 2.2 [Domain Components](In-Depth_Guides/Tutorials/Domain_Component_Principles.md)
  * 2.2.1 [Agent](In-Depth_Guides/Tutorials/Agent/Agent.md)
    * 2.2.1.1 [Create And Use](In-Depth_Guides/Tutorials/Agent/Agent_Create_And_Use.md)
    * 2.2.1.2 [Related Domain Objects](In-Depth_Guides/Tutorials/Agent/Agent_Related_Domain_Objects.md)
  * 2.2.2 [LLM](In-Depth_Guides/Tutorials/LLM/LLM.md)
    * 2.2.2.1 [Define And Use](In-Depth_Guides/Tutorials/LLM/LLM_component_define_and_usage.md)
    * 2.2.2.2 [Related Domain Objects](In-Depth_Guides/Tutorials/LLM/LLM_Related_Domain_Objects.md)
  * 2.2.3 [Tool](In-Depth_Guides/Tutorials/Tool/Tool.md)
    * 2.2.3.1 [Create And Use](In-Depth_Guides/Tutorials/Tool/Tool_Create_And_Use.md)
    * 2.2.3.2 [Related Domain Objects](In-Depth_Guides/Tutorials/Tool/Tool_Related_Domain_Objects.md)
  * 2.2.4 [Knowledge](In-Depth_Guides/Tutorials/Knowledge/Knowledge.md)
    * 2.2.4.1 [Define And Use](In-Depth_Guides/Tutorials/Knowledge/Knowledge_Define_And_Use.md)
    * 2.2.4.2 [Related Domain Objects](In-Depth_Guides/Tutorials/Knowledge/Knowledge_Related_Domain_Objects.md)
  * 2.2.5 [Memory](In-Depth_Guides/Tutorials/Memory/Memory.md)
    * 2.2.5.1 [Define And Use](In-Depth_Guides/Tutorials/Memory/Memory_Define_And_Use.md)
    * 2.2.5.2 [Related Domain Objects](In-Depth_Guides/Tutorials/Memory/Memory_Related_Domain_Objects.md)
  * 2.2.6 [Planner](In-Depth_Guides/Tutorials/Plan/Planner.md)
    * 2.2.5.1 [Define And Use](In-Depth_Guides/Tutorials/Plan/Planner_Define_And_Use.md)
    * 2.2.5.2 [Related Domain Objects](In-Depth_Guides/Tutorials/Plan/Planner_Related_Domain_Objects.md)
* 2.3 Technical Components
  * 2.3.1 [RAG](In-Depth_Guides/Tutorials/RAG.md) 
    * 2.3.1.1 [How to Build Knowledge Base](How-to/Build%20and%20Use%20a%20Knowledge%20Base/How_to_Build_Knowledge_Base.md) 
    * 2.3.1.1 [How to Use Knowledge Base](How-to/Build%20and%20Use%20a%20Knowledge%20Base/How_to_Use_Knowledge_Base.md) 
* 2.4 Others
  * 2.4.1 Service
    * 2.4.1.1 [Registration and Usage](In-Depth_Guides/Tech_Capabilities/Service/Service_Registration_and_Usage.md)
    * 2.4.1.2 [Web Server](In-Depth_Guides/Tech_Capabilities/Service/Web_Server.md)
    * 2.4.1.3 [Web API](In-Depth_Guides/Tech_Capabilities/Service/Web_Api.md)
    * 2.4.1.4 [Service Information Storage](In-Depth_Guides/Tech_Capabilities/Service/Service_Information_Storage.md)
  * 2.4.2 Prompt Management
  * 2.4.3 Multi-turn Dialogue
  * 2.4.4 Logging
    * 2.4.4.1 [Logging Component](In-Depth_Guides/Tech_Capabilities/Log_And_Monitor/Logging_Utils.md)
  * 2.4.5 Data Collection
    * 2.4.5.1 [Monitor Module](In-Depth_Guides/Tech_Capabilities/Log_And_Monitor/Monitor_Module.md)
  * 2.4.6 Data Autonomous
    * 2.4.6.1 [Data Autonomous Agent](In-Depth_Guides/Tutorials/Data_Autonomous_Agent.md)

**3. Component Reference Manual**
* 3.1 Domain Components
  * 3.1.1 List of Agents
  * 3.1.2 [List of LLMs](In-Depth_Guides/Components/LLMs/0.List_Of_LLMs.md)
    * 3.1.2.1 [OpenAI Usage Instructions](In-Depth_Guides/Components/LLMs/OpenAI_LLM_Use.md)
    * 3.1.2.2 [Qwen Usage Instructions](In-Depth_Guides/Components/LLMs/Qwen_LLM_Use.md)
    * 3.1.2.3 [WenXin Usage Instructions](In-Depth_Guides/Components/LLMs/WenXin_LLM_Use.md)
    * 3.1.2.4 [Kimi Usage Instructions](In-Depth_Guides/Components/LLMs/Kimi_LLM_Use.md)
    * 3.1.2.5 [BaiChuan Usage Instructions](In-Depth_Guides/Components/LLMs/BaiChuan_LLM_Use.md)
    * 3.1.2.6 [Claude Usage Instructions](In-Depth_Guides/Components/LLMs/Claude_LLM_Use.md)
    * 3.1.2.7 [Ollama Usage Instructions](In-Depth_Guides/Components/LLMs/Ollama_LLM_Use.md)
    * 3.1.2.8 [DeepSeek Usage Instructions](In-Depth_Guides/Components/LLMs/DeepSeek_LLM_Use.md)
    * 3.1.2.9 [GLM Usage Instructions](In-Depth_Guides/Components/LLMs/GLM_LLM_Use.md)
    * 3.1.2.10 [General OpenAI Protocol Style Wrapper](In-Depth_Guides/Components/LLMs/OpenAIStyleLLM_Use.md)
  * 3.1.3 List of Tools
    * 3.1.3.1 [Integration Tool Details](In-Depth_Guides/Components/Tools/Integrated_Tools.md)
    * 3.1.3.2 [LangChain Tool Wrapper](In-Depth_Guides/Components/Tools/Integrated_LangChain_Tools.md)
  * 3.1.4 List of Knowledge
  * 3.1.5 List of Memories
  * 3.1.6 List of Planners
* 3.2 Technical Components
  * 3.2.1 RPC
    * 3.2.1.1 [gRPC](In-Depth_Guides/Tech_Capabilities/Service/gRPC.md)
  * 3.2.2 Store
    * 3.2.2.1 [SQLDBWrapper](In-Depth_Guides/Tech_Capabilities/Storage/SQLDB_WRAPPER.md)
    * 3.2.2.2 [Milvus](In-Depth_Guides/Tech_Capabilities/Storage/Milvus.md)
    * 3.2.2.3 [ChromaDB](In-Depth_Guides/Tech_Capabilities/Storage/ChromaDB.md)
    * 3.2.2.4 [Sqlite](In-Depth_Guides/Tech_Capabilities/Storage/Sqlite.md)
  * 3.2.3 Msg
  * 3.2.4 Logging
    * 3.2.4.1 [Alibaba Cloud SLS](In-Depth_Guides/Tech_Capabilities/Log_And_Monitor/Alibaba_Cloud_SLS.md)

**[4. API Reference Manual](In-Depth_Guides/Tech_Capabilities/Others/API_Reference.md)**

**5. Best Practices**
* 5.1 Operations and Deployment
  * 5.1.1 [Docker Containerization Solution](In-Depth_Guides/Deployment/Docker_Container_Deployment.md)
  * 5.1.2 [K8S Solution](In-Depth_Guides/Deployment/K8S_Deployment.md)

**6. Use Cases**
* 6.1 RAG-Type Agent Examples
  * 6.1.1 [Legal Consultation Agent v2](Examples/Legal_Advice.md)
* 6.2 ReAct-Type Agent Examples
  * 6.2.1 [Python Code Generation and Execution Agent](Examples/Python_Auto_Runner.md)
* 6.3 [Discussion Group Based on Multi-Turn Multi-Agent Mode](Examples/Discussion_Group.md)
* 6.4 PEER Multi-Agent Cooperation Examples
  * 6.4.1 [Financial Event Analysis Case](Examples/Financial_Event_Analysis.md)
* 6.5 [Andrew Ng's Reflexive Workflow Translation Agent Replication](Examples/Translation_Assistant.md)

**7.Product Platform**
* 7.1 [Quick Use](How-to/Guide%20to%20Visual%20Agentic%20Workflow%20Platform/Product_Platform_Quick_Start.md)
* 7.2 [Advancement Guide](How-to/Guide%20to%20Visual%20Agentic%20Workflow%20Platform/Product_Platform_Advancement_Guide.md)

**8. Series of Articles**

**9. Frequently Asked Questions (FAQ)**

**[10.Citation](Concepts/Citation_PEER.md)**

**[11. Contact Us](Contact_Us.md)**
