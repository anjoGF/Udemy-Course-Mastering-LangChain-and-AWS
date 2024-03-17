import redis
import openai
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.utilities import SerpAPIWrapper
import uuid
from datetime import datetime, timedelta
import math
from langchain_experimental.sql import SQLDatabaseChain
from dateutil import parser
import os
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_community.tools import AIPluginTool  
from langchain_openai import OpenAIEmbeddings  
from langchain_openai import OpenAI 
from dateutil.parser import parse
from dateutil import parser

# Load environment variables from .env file
load_dotenv()

class EconomicDataAgent:
    def __init__(self, api_key, db_uri):
        self.api_key = api_key
        self.db_uri = db_uri or os.getenv('DATABASE_URI')
        openai.api_key = self.api_key  
        self.redis_url = os.getenv('REDIS_URL', 'redis://langchain-redis:6379/0')
        self.agent_executor = self.initialize_agent()

    def initialize_agent(self):
        try:
            self.message_history = self.initialize_redis_memory()
            self.memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=self.message_history)
            self.serpapi_tool = self.initialize_serpapi_tool()
            self.db = self.initialize_sql_database()
            self.tools = self.initialize_tools()
            self.llm = self.initialize_llm()
            self.db_chain = self.initialize_sql_database_chain()
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm, chat_message_history=self.message_history)
            self.sql_agent = self.create_sql_agent()
            self.sql_agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                top_k=10,
                extra_tools=self.tools,  
                max_iterations=7,
            )
            return self.sql_agent
        except Exception as e:
            print(f"An error occurred during agent initialization: {e}")
            raise e

    def set_api_key(self):
        openai.api_key = self.api_key
        
    def generate_session_id(self, interval_minutes=5):
        try:
            now = datetime.utcnow()  # Get the current UTC time
            minutes_since_midnight = now.hour * 60 + now.minute  # Calculate minutes since midnight
            interval_count = math.floor(minutes_since_midnight / interval_minutes)  # Calculate the interval count
            session_id = now.strftime("%Y%m%d") + f"_{interval_count}"  
            return session_id
        except Exception as e:
            print(f"Error in generating session ID: {e}")  
            return None        

    def run_agent_query(self, query):
        try:
            return self.sql_agent.invoke(query)
        except openai.BadRequestError as e:
            print(f"Token limit exceeded: {e}")
            return "Sorry, the query is too long to process."
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__}, {str(e)}")
            return f"An error occurred: {str(e)}"

    def initialize_redis_memory(self):
        session_id = self.generate_session_id()
        return RedisChatMessageHistory(url=self.redis_url, ttl=1, session_id=session_id)

    def initialize_serpapi_tool(self):
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
        return Tool(name="Search", func=search.run, description="useful for when you need to answer questions about the yield curve, finance or economics")

    def initialize_sql_database(self):
        try:
            return SQLDatabase.from_uri(
                self.db_uri,
                include_tables=["economic_indicators", "yield_curve_prices", "business_cycles", "production_data"],
                sample_rows_in_table_info=1
            )
        except Exception as e:
            print(f"Failed to initialize SQL Database: {e}")
            return None
        
    @staticmethod
    def format_date_for_db(query_date: str):
        try:
            date_obj = parser.parse(query_date)
            # Format the date to match the database format (e.g., 'YYYY-MM-DD 00:00:00')
            formatted_date = date_obj.strftime("%Y-%m-%d 00:00:00")
            return formatted_date
        except ValueError as e:
            return f"Error: {e}"      
        
    def initialize_tools(self):
        try:
            few_shots = self.create_few_shots()
            retriever_tool = self.create_retriever_tool(few_shots)
            date_format_tool = Tool(
                name="DateFormatTool",
                func=self.format_date_for_db,
                description="Formats the date to match the database format 'YYYY-MM-DD 00:00:00'."
            )
            return [retriever_tool, date_format_tool]
        except Exception as e:
            print(f"Failed to initialize tools: {e}")
            return []

    def create_few_shots(self):
        try:
            few_shots = {
                "What was the highest unemployment rate last year?": 
                '''SELECT MAX("UNRATE") FROM economic_indicators WHERE "Date" >= '2022-01-01' AND "Date" <= '2022-12-31';''',
    
                "Average industrial production for the previous month?": 
                '''SELECT AVG("IPN213111S") FROM production_data WHERE "Date" >= date('now', 'start of month', '-1 month') AND "Date" < date('now', 'start of month');''',
    
                "Show the five lowest 10-year yield rates of the current year.": 
                '''SELECT "DGS10" FROM yield_curve_prices WHERE "Date" >= '2023-01-01' ORDER BY "DGS10" ASC LIMIT 5;''',
    
                "List the economic indicators for the first quarter of 2023.": 
                '''SELECT * FROM economic_indicators WHERE "Date" >= '2023-01-01' AND "Date" <= '2023-03-31';''',
    
                "What are the latest available production numbers for Saudi Arabia?": 
                '''SELECT "SAUNGDPMOMBD" FROM production_data WHERE "Date" = (SELECT MAX("Date") FROM production_data);''',
    
                "Compare the unemployment rate at the beginning and end of the last recession.": 
                '''SELECT "UNRATE" FROM economic_indicators WHERE "Date" IN (SELECT "Start_Date" FROM business_cycles WHERE "Phase" = 'Contraction' ORDER BY "Start_Date" DESC LIMIT 1) OR "Date" IN (SELECT "End_Date" FROM business_cycles WHERE "Phase" = 'Contraction' ORDER BY "End_Date" DESC LIMIT 1);''',
    
                "Find the average civilian labor force participation rate for the last year.": 
                '''SELECT AVG("CIVPART") FROM economic_indicators WHERE "Date" >= '2022-01-01' AND "Date" <= '2022-12-31';''',
    
                "Show the change in 2-year yield rates over the past six months.": 
                '''SELECT "DGS2" FROM yield_curve_prices WHERE "Date" >= date('now', '-6 months') ORDER BY "Date";''',
    
                "What was the maximum production of natural gas in Qatar last year?": 
                '''SELECT MAX("QATNGDPMOMBD") FROM production_data WHERE "Date" >= '2022-01-01' AND "Date" <= '2022-12-31';''',
    
                "List the top 3 longest economic expansions since 2000.": 
                '''SELECT "Start_Date", "End_Date" FROM business_cycles WHERE "Phase" = 'Expansion' AND "Start_Date" >= '2000-01-01' ORDER BY ("End_Date" - "Start_Date") DESC LIMIT 3;'''
            }
            return few_shots
        except Exception as e:
            print(f"Failed to create create few shots: {e}")
            return None

    def create_retriever_tool(self, few_shots):
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            few_shot_docs = [Document(page_content=question, metadata={"sql_query": few_shots[question]}) for question in few_shots.keys()]
            vector_db = FAISS.from_documents(few_shot_docs, embeddings)
            retriever = vector_db.as_retriever()
            tool_description = """
            Retrieves similar PostgresSQL examples, please use the 00:00:00 datetime format.
            """
            return create_retriever_tool(retriever, name="sql_get_similar_examples", description=tool_description)
        except Exception as e:
            print(f"Failed to create retriever tool: {e}")
            return None
        
    def create_prompt(self):
        self.prefix = """
        As an economic data analyst and a SQLite expert, I specialize in interpreting economic indicators and performing data analysis using specific SQL queries. 
        My expertise includes the following tables and their respective fields, you also have access to these tools: 
        
        1. economic_indicators (DATE, UNRATE, PAYEMS, ICSA, CIVPART, INDPRO)
        2. yield_curve_prices (Date, DGS1MO, DGS3MO, DGS6MO, DGS1, DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30)
        3. production_data (Date, SAUNGDPMOMBD, ARENGDPMOMBD, IRNNGDPMOMBD, SAUNXGO, QATNGDPMOMBD, KAZNGDPMOMBD, IRQNXGO, IRNNXGO, KWTNGDPMOMBD, IPN213111S, PCU213111213111, DPCCRV1Q225SBEA)
        4. business_cycles (Peak_Month, Trough_Month, Start_Date, End_Date, Phase)
        
        Please ask me questions related to these tables and fields. I will use SQL queries and web searches to provide accurate information on economic trends, indicators, and analysis based on this data. 
        Note that my responses are constrained to the data available in these tables, and web search via the serpapi_tool. If I do not know an answer, I will say I do not know.
        """
        
        self.suffix = """
        Begin!
        
        {chat_history}
        Question: {input}
        {agent_scratchpad}
        """
        return ZeroShotAgent.create_prompt(tools=self.tools, prefix=self.prefix, suffix=self.suffix, input_variables=["input", "chat_history", "agent_scratchpad"])

    def initialize_llm(self):
        return OpenAI(openai_api_key=self.api_key, temperature=0, verbose=True)

    def initialize_sql_database_chain(self):
        return SQLDatabaseChain.from_llm(self.llm, self.db, verbose=False, use_query_checker=True, return_intermediate_steps=False, top_k=5)

    def create_sql_agent(self):
        return create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            top_k=5,
            extra_tools=self.tools,  
            max_iterations=3
        )

if __name__ == "__main__":
    API_KEY = os.getenv('OPENAI_API_KEY')
    DB_URI = os.getenv('DATABASE_URI')
    agent = EconomicDataAgent(API_KEY, DB_URI)
    query = "What was the shape of the yield curve on December 15th 2009? What was the spread between the 2 year and the 10 year?"
    response = agent.run_agent_query(query)
    print("Query Result:", response)