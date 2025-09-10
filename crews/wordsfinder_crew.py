from pydantic import BaseModel
from typing import List
from crewai import Crew, Agent, Task
import json


class Words(BaseModel):
        word: str
        pronunciation: str
        meaning_eng: str
        meaning_native: str

class WordList(BaseModel):
    words: List[Words]

class WordsFinderCrew:
    def __init__(self, native_lang):   
        self.native_lang = native_lang

        self.agent = Agent(
            role="Searching the meaning of words",
            goal="Find the meaning of given words in English and given native language.",
            backstory="""
                You are finding the meaning of English words in dictionaries for people studying English.
                These are essential elements that you should find.
                - word :
                    The given word. All letters should be lowercases.
                    If the word is a phrase, use the phrase itself.(Do not cut words out.)
                    If the word is noun and given as a form of plural, return it as a form of singular.
                    ex) mandalas > mandala
                    If the word is verb and not written in the simple form of the verb, 
                    transform it to the simple form and add its conjugation(simple-past-past participle) at meaning section.
                    ex) reined > 
                        - word: rein
                        - meaning: (rein-reined-reined) to limit or control (someone or something)
                - pronunciation : 
                    The pronunciation of the words
                - meaning(English) : 
                    The meaning of given words in English dictionary
                    Each meaning should be provided with its grammatical category information(a./ad./v./n....).
                - meaning(native) :
                    What the words mean in native language
                    (in other words, how the words can translate in native language)

                e.g.
                    - word : succinct
                    - pronunciation : /səkˈsɪŋkt/
                    - meaning(English) : a. (especially of something written or spoken) briefly and clearly expressed
                    - meaing(native) : 간결한
            """,
            verbose=True,
            allow_delegation=False,
        )

        self.task = Task(
            description="Find the meaning of given word in English and {native_lang} by searching dictionaries: {word}",
            agent=self.agent,
            expected_output="A Words Object",
            output_json=Words,
        )

        self.crew = Crew(
            tasks=[
                self.task,
            ],
            agents=[
                self.agent,
            ],
            verbose=2,
            cache=True,
        )

    def search_words(self, word):
        result = self.crew.kickoff(
            inputs=dict(
                native_lang=self.native_lang,
                word=word,
            )
        )
        crewai_response = json.loads(result)
        return crewai_response