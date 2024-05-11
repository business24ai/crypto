from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI


# Uncomment the following line to use an example of a custom tool
from crypto.tools.custom_tool import MyCryptoTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool

# Get the current date and time
current_datetime = datetime.now()

# Format the date and time into a string with the specified format
suffix_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')


@CrewBase
class CryptoCrew():
	"""Crypto crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __init__(self) -> None:
		self.custom_llm = ChatOpenAI(
			model="gpt-3.5-turbo-0125",
		)
	
	# def __init__(self) -> None:
	# 	self.custom_llm = ChatGroq(
	# 		temperature=0.2,
	# 		groq_api_key=os.getenv("GROQ_API_KEY"),
	# 		model_name="llama3-70b-8192",
	# 	)

	@agent
	def portfolio_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['portfolio_manager'],
			tools=[MyCryptoTool()], # Example of custom tool
			verbose=True,
			allow_Delegation=False,
			llm=self.custom_llm
		)


	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			tools=[SerperDevTool()],
			verbose=True,
			allow_Delegation=False,
			llm=self.custom_llm
		)

	@task
	def get_highest_position_in_portfolio_task(self) -> Task:
		return Task(
			config=self.tasks_config['highest_position_task'],
			agent=self.portfolio_manager(),
			human_input=True
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			agent=self.reporting_analyst(),
			output_file=f"crypto_report_{suffix_datetime}.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Crypto crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
		)