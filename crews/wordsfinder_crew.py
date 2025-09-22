from pydantic import BaseModel
from typing import List
from crewai import Crew, Agent, Task
import json
from crewai_tools import SerperDevTool


class Word(BaseModel):
    word: str
    pronunciation: str
    meaning_eng: str
    meaning_native: str
    img: str

class WordList(BaseModel):
    words: List[Word]

class WordsFinderCrew:
    def __init__(self, native_lang):   
        self.native_lang = native_lang

        self.word_refiner = Agent(
            role="Refining given words",
            goal="Change the form of given word/phrase so as to make it easier to find in the dictionary",
            backstory="""
                Change the given word/phrase as rules below.
                
                All letters should be lowercases except for the case that it is the name of something.
                ex) - input: Somatic / output: somatic
                    - input: Vulcan / output: Vulcan

                If is is noun and given as a form of plural, return it as a form of singular.
                ex) - input: mandalas / output: mandala

                If is is verb and not written in the simple form of the verb, 
                transform it to the simple form.
                ex) - input: reined / output: rein
                But if the word has exceptional meaning as a given form, do not transform it.
                ex) - input: stress-boggled / output: stress-boggled

                Otherwise, the word shouldn't be transformed. Return the given word back.
                If it is a phrase, use the phrase itself.(Do not cut words out.)
                **Make sure not to subtitute given word by the other.**
            """,
            verbose=True,
            allow_delegation=False,
        )

        self.meaning_searcher = Agent(
             role="Searching the meaning of words",
            goal="Find the meaning of given words in English and given native language.",
            backstory="""
                You are finding the meaning of English word in dictionaries for people studying English.
                These are essential elements that you should find.
                - word :
                    The refined word from Word Refiner, the previous agent. 
                - pronunciation : 
                    The pronunciation of the word
                - meaning(English) : 
                    The meaning of given word in English dictionary
                    Each meaning should be provided with its grammatical category information(a./ad./v./n....).
                    If the word is verb, add its conjugation(simple-past-past participle) at meaning section.
                - meaning(native) :
                    What the word means in native language
                    (in other words, how the word can translate in native language)
                - image :
                    The url of the image that illustrates the word well
                    Find an image on the internet using search tool.
                    **Make sure the url should end with one of proper extentions.(ex. .jpg, .png, ...)**

                e.g.
                    - word : perseverate
                    - pronunciation : /pərˈsɛvəˌreɪt/
                    - meaning(English) : v. (perseverate-perseverated-perseverated) to repeat or prolong an action, thought, or utterance after the stimulus that prompted it has ceased.
                    - meaing(native) : 반복하다, 지속하다
                    - img : https://www.publicationcoach.com/wp-content/uploads/2012/03/what-does-perseverate-mean-3-28-12.jpg
            """,
            verbose=True,
            allow_delegation=False,
            tools=[
                SerperDevTool(),
            ]
        )

        self.example_generator = Agent(
             role="Generating an example sentence with given word/phrase",
            goal="Generate an example sentence involving given word/phrase so that human can understand how the word is used in sentences.",
            backstory="""
                You are helping students who are learning English.
                Return a sentence which is involving given word/phrase.
                If the word is verb, you can transform it's tense.
            """,
            verbose=True,
            allow_delegation=False,
        )

        self.refining_word = Task(
            description="Transform given word/phrase as given rules: {word}",
            agent=self.word_refiner,
            expected_output="A transformed word/phrase",
            # output_json=str,
        )

        self.searching_meaning = Task(
            description="Find the meaning of given word in English and {native_lang} by searching dictionaries: {word}",
            agent=self.meaning_searcher,
            expected_output="A Word Object",
            output_json=Word,
        )

        self.generating_example = Task(
            description="Generate an example sentence with: {word}",
            agent=self.example_generator,
            expected_output="An example sentence involving given word/phrase",
            # output_json=str,
        )

        self.preprocess_crew = Crew(
            tasks=[
                self.refining_word,
            ],
            agents=[
                self.word_refiner,
            ],
            verbose=2,
            cache=True,
        )

        self.main_crew = Crew(
             tasks=[
                self.searching_meaning,
            ],
            agents=[
                self.meaning_searcher,
            ],
            verbose=2,
            cache=True,
        )

        self.example_crew = Crew(
             tasks=[
                self.generating_example,
            ],
            agents=[
                self.example_generator,
            ],
            verbose=2,
            cache=True,
        )

    def preprocess(self, word):
        res = self.preprocess_crew.kickoff(
            inputs=dict(
                word=word,
            )
        )
        return res

    def search_words(self, word):
        res = self.main_crew.kickoff(
            inputs=dict(
                native_lang=self.native_lang,
                word=word,
            )
        )
        return json.loads(res)
    
    def generate_example(self, word):
        res = self.example_crew.kickoff(
            inputs=dict(
                word=word,
            )
        )
        return res
    

    