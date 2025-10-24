import uuid
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List
from rich import print
from app.prompts.extract_prompt import (
    new_chunk_title_prompt,
    new_chunk_summary_prompt,
    find_relevant_chunk_prompt,
    update_chunk_title_prompt,
    update_chunk_summary_prompt,
    get_propositions_prompt,
)
from enum import Enum


class GetType(Enum):
    DICT = "dict"
    LIST_OF_STRING = "list_of_string"


class AgenticChunker:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chunks = {}
        self.id_truncate_limit = 5

        # on new information update title and summary
        self.print_logging = True
        self.generate_new_metadata = True

    def _get_new_chunk_title(self, summary):
        chain = new_chunk_title_prompt | self.llm
        return chain.invoke({"summary": summary}).content

    def _get_new_chunk_summary(self, proposition):
        chain = new_chunk_summary_prompt | self.llm
        return chain.invoke({"proposition": proposition}).content

    def _update_chunk_title(self, chunk):
        chain = update_chunk_title_prompt | self.llm
        return chain.invoke(
            {
                "proposition": chunk["propositions"][-1],
                "current_summary": chunk["summary"],
                "current_title": chunk["title"],
            }
        ).content

    def _update_chunk_summary(self, chunk):
        chain = update_chunk_summary_prompt | self.llm
        return chain.invoke(
            {
                "proposition": chunk["propositions"][-1],
                "current_summary": chunk["summary"],
            }
        ).content

    def _create_new_chunk(self, proposition):
        new_chunk_id = str(uuid.uuid4())
        new_chunk_summary = self._get_new_chunk_summary(proposition=proposition)
        new_chunk_title = self._get_new_chunk_title(summary=new_chunk_summary)

        self.chunks[new_chunk_id] = {
            "chunk_id": new_chunk_id,
            "title": new_chunk_title,
            "summary": new_chunk_summary,
            "propositions": [proposition],
            "chunk_index": len(self.chunks),
        }

        if self.print_logging:
            print(f"Created new chunk {new_chunk_id}: {new_chunk_title}")

    def _get_chunk_outline(self):
        """
        Get a string outline of the current chunks
        """
        chunk_outline = ""

        for chunk_id, chunk in self.chunks.items():
            single_chunk_string = f"""
            - Chunk ID: ({chunk_id})\n
            - Chunk Title:{chunk["title"]}\n
            - Summary: {chunk["summary"]}\n\n
            """

            chunk_outline += single_chunk_string

        return chunk_outline

    def _find_relevant_chunk(self, proposition):
        class ChunkID(BaseModel):
            chunk_id: str

        current_chunk_outline = self._get_chunk_outline()
        chain = find_relevant_chunk_prompt | self.llm.with_structured_output(ChunkID)
        chunk_found = chain.invoke(
            {
                "proposition": proposition,
                "current_chunk_outline": current_chunk_outline,
            }
        )

        if chunk_found.chunk_id is None:
            return None

        return chunk_found.chunk_id

    def _add_proposition_to_chunk(self, chunk_id, proposition):
        self.chunks[chunk_id]["propositions"].append(proposition)
        # update title and summary of the chunk
        if self.generate_new_metadata:
            self.chunks[chunk_id]["title"] = self._update_chunk_title(
                self.chunks[chunk_id]
            )
            self.chunks[chunk_id]["summary"] = self._update_chunk_summary(
                self.chunks[chunk_id]
            )

    def add_proposition(self, proposition):
        # create new chunk if chunks are empty
        if len(self.chunks) == 0:
            self._create_new_chunk(proposition)
            return

        chunk_id = self._find_relevant_chunk(proposition)

        if chunk_id == None or chunk_id == "No chunks":
            self._create_new_chunk(proposition)
            return

        self._add_proposition_to_chunk(chunk_id, proposition)
        return

    def add_propositions(self, propositions):
        for proposition in propositions:
            self.add_proposition(proposition)

    def get_propositions(self, text: str):
        class Sentences(BaseModel):
            sentences: List[str]

        chain = get_propositions_prompt | self.llm.with_structured_output(Sentences)
        return chain.invoke({"input": text}).sentences

    def get_chunks(self, get_type: GetType = GetType.DICT):
        if get_type == GetType.DICT:
            return self.chunks

        if get_type == GetType.LIST_OF_STRING:
            chunks = []
            for chunk_id, chunk in self.chunks.items():
                print(chunk)
                chunks.append(" ".join([x for x in chunk["propositions"]]))
            return chunks

    def pretty_print_chunks(self):
        print(f"Chunks length: {len(self.chunks)}\n")
        for chunk_id, chunk in self.chunks.items():
            print(f"Chunk ID: {chunk_id}")
            print(f"Title: {chunk['title']}")
            print(f"Summary: {chunk['summary']}")
            print(f"Propositions:")
            for proposition in chunk["propositions"]:
                print(f"- {proposition}")
            print("\n\n")

    def pretty_print_chunk_outline(self):
        print("Chunk outline:\n")
        print(self._get_chunk_outline())
