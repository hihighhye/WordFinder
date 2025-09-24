from pydantic import BaseModel
from crewai import Crew, Agent, Task, LLM
import json
import os


class TranslatorCrew:
    def __init__(self):  # , openai_api_key
        # os.environ['OPENAI_API_KEY'] = openai_api_key

        # self.llm = LLM(
        #     temperature=0.1,
        #     model="gpt-4o-mini",
        #     streaming=True,
        #     api_key=openai_api_key,
        # )

        self.translator = Agent(
            role="Interpreter",
            goal="Translate given {depart_lang} sentences or phrases in given {destin_lang} language.",
            backstory="""
                You are a decent interpreter.
                You are translating sentences or phrases for people studying English.
                Return the translation of the given sentences.
            """,
            verbose=True,
            allow_delegation=False,
            # llm=self.llm,
        )

        self.translating = Task(
            description="Translate given {depart_lang} sentences or phrases in {destin_lang}: {phrase}",
            agent=self.translator,
            expected_output="Translated sentences/phrases",
        )

        self.translator_crew = Crew(
            tasks=[
                self.translating,
            ],
            agents=[
                self.translator,
            ],
            verbose=True,
            cache=True,
        )

    def translate(self, depart_lang, destin_lang, phrase):
        result = self.translator_crew.kickoff(
            inputs=dict(
                depart_lang=depart_lang,
                destin_lang=destin_lang,
                phrase=phrase,
            )
        )
        return result.raw