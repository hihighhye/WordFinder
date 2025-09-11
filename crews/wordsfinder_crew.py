from pydantic import BaseModel
from typing import List
from crewai import Crew, Agent, Task
import json


class Refined(BaseModel):
    input: str
    output: str

class Word(BaseModel):
        word: str
        pronunciation: str
        meaning_eng: str
        meaning_native: str

class WordList(BaseModel):
    words: List[Word]

class WordsFinderCrew:
    def __init__(self, native_lang):   
        self.native_lang = native_lang

        self.word_refiner = Agent(
            role="Refining given words",
            goal="Change the form of given word/phrase so as to make it easier to find in the dictionary",
            backstory="""
                Change the given word/phrase as a rule below.
                
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
                You are finding the meaning of English words in dictionaries for people studying English.
                These are essential elements that you should find.
                - word :
                    The refined word from Word Refiner, the previous agent. 
                - pronunciation : 
                    The pronunciation of the words
                - meaning(English) : 
                    The meaning of given words in English dictionary
                    Each meaning should be provided with its grammatical category information(a./ad./v./n....).
                    If the word is verb, add its conjugation(simple-past-past participle) at meaning section.
                - meaning(native) :
                    What the words mean in native language
                    (in other words, how the words can translate in native language)

                e.g.
                    - word : perseverate
                    - pronunciation : /pərˈsɛvəˌreɪt/
                    - meaning(English) : v. (perseverate-perseverated-perseverated) to repeat or prolong an action, thought, or utterance after the stimulus that prompted it has ceased.
                    - meaing(native) : 반복하다, 지속하다
            """,
            verbose=True,
            allow_delegation=False,
        )

        self.refining_word = Task(
            description="Transform given word/phrase as a rule given: {word}",
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
    
    