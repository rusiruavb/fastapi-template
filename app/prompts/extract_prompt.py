from langchain_core.prompts import ChatPromptTemplate

get_propositions_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Decompose the "Content" into clear and simple propositions, ensuring they are interpretable out of
            context.
            1. Split compound sentence into simple sentences. Maintain the original phrasing from the input
            whenever possible.
            2. For any named entity that is accompanied by additional descriptive information, separate this
            information into its own distinct proposition.
            3. Decontextualize the proposition by adding necessary modifier to nouns or entire sentences
            and replacing pronouns (e.g., "it", "he", "she", "they", "this", "that") with the full name of the
            entities they refer to.
            4. Present the results as a list of strings, formatted in JSON.

            Example:

            Input: Title: ¯Eostre. Section: Theories and interpretations, Connection to Easter Hares. Content:
            The earliest evidence for the Easter Hare (Osterhase) was recorded in south-west Germany in
            1678 by the professor of medicine Georg Franck von Franckenau, but it remained unknown in
            other parts of Germany until the 18th century. Scholar Richard Sermon writes that "hares were
            frequently seen in gardens in spring, and thus may have served as a convenient explanation for the
            origin of the colored eggs hidden there for children. Alternatively, there is a European tradition
            that hares laid eggs, since a hare’s scratch or form and a lapwing’s nest look very similar, and
            both occur on grassland and are first seen in the spring. In the nineteenth century the influence
            of Easter cards, toys, and books was to make the Easter Hare/Rabbit popular throughout Europe.
            German immigrants then exported the custom to Britain and America where it evolved into the
            Easter Bunny."
            Output: [ "The earliest evidence for the Easter Hare was recorded in south-west Germany in
            1678 by Georg Franck von Franckenau.", "Georg Franck von Franckenau was a professor of
            medicine.", "The evidence for the Easter Hare remained unknown in other parts of Germany until
            the 18th century.", "Richard Sermon was a scholar.", "Richard Sermon writes a hypothesis about
            the possible explanation for the connection between hares and the tradition during Easter", "Hares
            were frequently seen in gardens in spring.", "Hares may have served as a convenient explanation
            for the origin of the colored eggs hidden in gardens for children.", "There is a European tradition
            that hares laid eggs.", "A hare’s scratch or form and a lapwing’s nest look very similar.", "Both
            hares and lapwing’s nests occur on grassland and are first seen in the spring.", "In the nineteenth
            century the influence of Easter cards, toys, and books was to make the Easter Hare/Rabbit popular
            throughout Europe.", "German immigrants exported the custom of the Easter Hare/Rabbit to
            Britain and America.", "The custom of the Easter Hare/Rabbit evolved into the Easter Bunny in
            Britain and America."]
            """,
        ),
        (
            "human",
            """
            Decompose the following:
            {input}
            """,
        ),
    ]
)

new_chunk_title_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
            You should generate a very brief few word chunk title which will inform viewers what a chunk group is about.

            A good chunk title is brief but encompasses what the chunk is about

            You will be given a summary of a chunk which needs a title

            Your titles should anticipate generalization. If you get a proposition about apples, generalize it to food.
            Or month, generalize it to "date and times".

            Example:
            Input: Summary: This chunk is about dates and times that the author talks about
            Output: Date & Times

            Only respond with the new chunk title, nothing else.
            """,
        ),
        (
            "user",
            "Determine the title of the chunk that this summary belongs to:\n{summary}",
        ),
    ]
)

new_chunk_summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
            You should generate a very brief 1-sentence summary which will inform viewers what a chunk group is about.

            A good summary will say what the chunk is about, and give any clarifying instructions on what to add to the chunk.

            You will be given a proposition which will go into a new chunk. This new chunk needs a summary.

            Your summaries should anticipate generalization. If you get a proposition about apples, generalize it to food.
            Or month, generalize it to "date and times".

            Example:
            Input: Proposition: Greg likes to eat pizza
            Output: This chunk contains information about the types of food Greg likes to eat.

            Only respond with the new chunk summary, nothing else.
            """,
        ),
        (
            "user",
            "Determine the summary of the new chunk that this proposition will go into:\n{proposition}",
        ),
    ]
)

update_chunk_title_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
            A new proposition was just added to one of your chunks, you should generate a very brief updated chunk title which will inform viewers what a chunk group is about.

            A good title will say what the chunk is about.

            You will be given a group of propositions which are in the chunk, chunk summary and the chunk title.

            Your title should anticipate generalization. If you get a proposition about apples, generalize it to food.
            Or month, generalize it to "date and times".

            Example:
            Input: Summary: This chunk is about dates and times that the author talks about
            Output: Date & Times

            Only respond with the new chunk title, nothing else.
            """,
        ),
        (
            "user",
            "Chunk's propositions:\n{proposition}\n\nChunk summary:\n{current_summary}\n\nCurrent chunk title:\n{current_title}",
        ),
    ]
)

update_chunk_summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
            A new proposition was just added to one of your chunks, you should generate a very brief 1-sentence summary which will inform viewers what a chunk group is about.

            A good summary will say what the chunk is about, and give any clarifying instructions on what to add to the chunk.

            You will be given a group of propositions which are in the chunk and the chunks current summary.

            Your summaries should anticipate generalization. If you get a proposition about apples, generalize it to food.
            Or month, generalize it to "date and times".

            Example:
            Input: Proposition: Greg likes to eat pizza
            Output: This chunk contains information about the types of food Greg likes to eat.

            Only respond with the chunk new summary, nothing else.
            """,
        ),
        (
            "user",
            "Chunk's propositions:\n{proposition}\n\nCurrent chunk summary:\n{current_summary}",
        ),
    ]
)

find_relevant_chunk_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Determine whether or not the "Proposition" should belong to any of the existing chunks.

            A proposition should belong to a chunk of their meaning, direction, or intention are similar.
            The goal is to group similar propositions and chunks.

            If you think a proposition should be joined with a chunk, return the chunk id.
            If you do not think an item should be joined with an existing chunk, just return "No chunks"

            Example:
            Input:
                - Proposition: "Greg really likes hamburgers"
                - Current Chunks:
                    - Chunk ID: 2n4l3d
                    - Chunk Name: Places in San Francisco
                    - Chunk Summary: Overview of the things to do with San Francisco Places

                    - Chunk ID: 93833k
                    - Chunk Name: Food Greg likes
                    - Chunk Summary: Lists of the food and dishes that Greg likes
            Output: 93833k
            """,
        ),
        (
            "user",
            "Current Chunks:\n--Start of current chunks--\n{current_chunk_outline}\n--End of current chunks--",
        ),
        (
            "user",
            "Determine if the following statement should belong to one of the chunks outlined:\n{proposition}",
        ),
    ]
)
