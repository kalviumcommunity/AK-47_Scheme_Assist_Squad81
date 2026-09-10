import os
import sys
import re

from typing import List, Dict, Any, Optional


# ============================================================
# PROJECT IMPORT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


# ============================================================
# IMPORTS
# ============================================================

import chromadb

from src.config import (
    GEMINI_API_KEY,
    EMBED_MODEL,
    VECTOR_DIMENSION,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME
)


# ============================================================
# RETRIEVAL QUALITY GUARDRAILS
# ============================================================

MIN_RETRIEVAL_SCORE = 0.50

WEAK_CONTEXT_MESSAGE = (
    "I don't have enough reliable scheme information "
    "in my knowledge base to answer this question accurately."
)


# ============================================================
# QUERY GUARDRAILS
# ============================================================

SCHEME_KEYWORDS = {
    "scheme",
    "schemes",
    "government",
    "welfare",
    "benefit",
    "benefits",
    "eligible",
    "eligibility",
    "apply",
    "application",
    "pension",
    "scholarship",
    "farmer",
    "farmers",
    "kisan",
    "pm",
    "pm-kisan",
    "ayushman",
    "healthcare",
    "health",
    "housing",
    "awas",
    "employment",
    "subsidy",
    "financial",
    "assistance",
    "government assistance",
    "old age",
    "senior citizen",
    "student",
    "education",
    "loan",
    "dbt",
    "aadhaar",
    "vishwakarma",
    "nmmss",
    "pmay",
    "nsap",
    "ignoaps"
}


# ============================================================
# QUERY EMBEDDING
# ============================================================

def generate_query_embedding(
    query: str
) -> List[float]:
    """
    Generates an embedding for the user's search query.

    Uses the same Gemini embedding model and vector dimension
    used during document indexing.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Query cannot be empty."
        )

    if not GEMINI_API_KEY or not GEMINI_API_KEY.strip():
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    try:

        from google import genai
        from google.genai import types


        print()

        print(
            "[RETRIEVAL LOG] "
            "Generating query embedding..."
        )

        print(
            f"[RETRIEVAL LOG] Query: {query}"
        )

        print(
            f"[RETRIEVAL LOG] Model: {EMBED_MODEL}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Requested Dimension: {VECTOR_DIMENSION}"
        )


        # ----------------------------------------------------
        # CREATE GEMINI CLIENT
        # ----------------------------------------------------

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )


        # ----------------------------------------------------
        # GENERATE EMBEDDING
        # ----------------------------------------------------

        response = client.models.embed_content(

            model=EMBED_MODEL,

            contents=query,

            config=types.EmbedContentConfig(
                output_dimensionality=VECTOR_DIMENSION
            )

        )


        # ----------------------------------------------------
        # EXTRACT VECTOR
        # ----------------------------------------------------

        embedding = list(
            response.embeddings[0].values
        )


        # ----------------------------------------------------
        # VALIDATE DIMENSION
        # ----------------------------------------------------

        if len(embedding) != VECTOR_DIMENSION:

            raise ValueError(

                f"Query embedding dimension mismatch. "

                f"Expected {VECTOR_DIMENSION}, "

                f"received {len(embedding)}."

            )


        print()

        print(
            "[RETRIEVAL SUCCESS] "
            "Query embedding generated."
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Vector Dimension: {len(embedding)}"
        )


        return embedding


    except Exception as error:

        print()

        print(
            "[RETRIEVAL ERROR] "
            "Failed to generate query embedding."
        )

        print(
            f"[RETRIEVAL ERROR] {error}"
        )

        raise


# ============================================================
# KEYWORD TOKENIZER
# ============================================================

def tokenize(
    text: str
) -> List[str]:
    """
    Converts text into lowercase tokens.
    """

    if not text:
        return []

    return re.findall(

        r"[a-zA-Z0-9']+",

        text.lower()

    )


# ============================================================
# KEYWORD SCORE
# ============================================================

def calculate_keyword_score(

    query: str,

    document: str

) -> float:
    """
    Calculates keyword overlap score.

    Score Range:
    0.0 = No keyword match
    1.0 = Complete keyword match
    """

    query_tokens = set(
        tokenize(query)
    )

    document_tokens = set(
        tokenize(document)
    )


    if not query_tokens:
        return 0.0


    overlap = (

        query_tokens

        &

        document_tokens

    )


    score = (

        len(overlap)

        /

        len(query_tokens)

    )


    return round(
        score,
        4
    )


# ============================================================
# CHECK IF QUERY IS SCHEME RELATED
# ============================================================

def is_scheme_related_query(
    query: str
) -> bool:
    """
    Checks whether the user's query appears related
    to government schemes or welfare services.
    """

    if not query or not query.strip():
        return False


    query_lower = query.lower()

    query_tokens = set(
        tokenize(query)
    )


    # --------------------------------------------------------
    # DIRECT KEYWORD MATCH
    # --------------------------------------------------------

    for keyword in SCHEME_KEYWORDS:

        if " " in keyword:

            if keyword in query_lower:
                return True

        elif keyword.lower() in query_tokens:
            return True


    return False


# ============================================================
# GUARDRAIL RESPONSE
# ============================================================

def get_guardrail_response() -> Dict[str, Any]:
    """
    Standard response for unrelated questions.
    """

    return {

        "allowed": False,

        "message": (
            "I can only assist with government welfare schemes, "
            "eligibility, benefits, applications, documents, and "
            "scheme-related information. Please ask a question "
            "related to a government scheme."
        ),

        "results": [],

        "sources": []

    }


# ============================================================
# NORMALIZE VECTOR SCORE
# ============================================================

def normalize_vector_score(
    distance: Optional[float]
) -> float:
    """
    Converts Chroma cosine distance into
    a normalized similarity score.

    0 = Highly similar
    1 = Less similar

    similarity = 1 - distance
    """

    if distance is None:
        return 0.0


    similarity = (

        1.0

        -

        float(distance)

    )


    similarity = max(

        0.0,

        min(
            1.0,
            similarity
        )

    )


    return round(
        similarity,
        4
    )


# ============================================================
# RETRIEVAL QUALITY CHECK
# ============================================================

def is_retrieval_strong(

    results: List[Dict[str, Any]],

    min_score: float = MIN_RETRIEVAL_SCORE

) -> bool:
    """
    Checks whether retrieved results are strong enough
    to be used for AI generation.

    Returns False when:

    - No results are found
    - Top result score is below threshold
    """

    if not results:
        return False


    top_score = results[0].get(

        "hybrid_score",

        0.0

    )


    return top_score >= min_score


# ============================================================
# VECTOR DATABASE RETRIEVER
# ============================================================

class SchemeRetriever:

    """
    Retrieves relevant scheme information from ChromaDB.

    Features:

    1. Semantic vector search
    2. Gemini query embeddings
    3. Metadata filtering
    4. Keyword boosting
    5. Hybrid ranking
    6. Query guardrails
    7. Retrieval quality guardrails
    8. Source information
    9. AI context generation
    """


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(

        self,

        db_dir: str = CHROMA_PERSIST_DIR,

        collection_name: str = COLLECTION_NAME,

        alpha: float = 0.7,

        beta: float = 0.3

    ):


        # ----------------------------------------------------
        # VALIDATE WEIGHTS
        # ----------------------------------------------------

        if alpha < 0 or beta < 0:

            raise ValueError(
                "alpha and beta cannot be negative."
            )


        if alpha == 0 and beta == 0:

            raise ValueError(
                "alpha and beta cannot both be zero."
            )


        total_weight = alpha + beta


        self.alpha = (
            alpha / total_weight
        )

        self.beta = (
            beta / total_weight
        )


        self.db_dir = db_dir

        self.collection_name = collection_name


        # ----------------------------------------------------
        # CHECK DATABASE
        # ----------------------------------------------------

        if not os.path.exists(
            self.db_dir
        ):

            raise RuntimeError(

                f"ChromaDB directory not found: "

                f"{self.db_dir}. "

                f"Run indexing.py first."

            )


        # ----------------------------------------------------
        # INITIALIZE CHROMADB
        # ----------------------------------------------------

        try:

            self.client = (

                chromadb.PersistentClient(

                    path=self.db_dir

                )

            )


            self.collection = (

                self.client.get_collection(

                    name=self.collection_name

                )

            )


        except Exception as error:

            raise RuntimeError(

                f"Failed to connect to "

                f"ChromaDB collection "

                f"'{self.collection_name}'. "

                f"Run indexing.py first. "

                f"Error: {error}"

            )


        # ----------------------------------------------------
        # RECORD COUNT
        # ----------------------------------------------------

        self.record_count = (

            self.collection.count()

        )


        if self.record_count == 0:

            print()

            print(
                "[RETRIEVAL WARNING] "
                "Collection is empty."
            )

            print(
                "[RETRIEVAL WARNING] "
                "Run indexing.py first."
            )


        # ----------------------------------------------------
        # LOGS
        # ----------------------------------------------------

        print()

        print(
            "=" * 75
        )

        print(
            "[RETRIEVAL LOG] "
            "ChromaDB Connected"
        )

        print(
            "=" * 75
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Database: {self.db_dir}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Collection: {self.collection_name}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Available Records: {self.record_count}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Embedding Model: {EMBED_MODEL}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Vector Dimension: {VECTOR_DIMENSION}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Hybrid Weights: "
            f"Vector={self.alpha:.2f}, "
            f"Keyword={self.beta:.2f}"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Minimum Retrieval Score: "
            f"{MIN_RETRIEVAL_SCORE}"
        )

        print(
            "=" * 75
        )


    # ========================================================
    # BASIC VECTOR SEARCH
    # ========================================================

    def vector_search(

        self,

        query: str,

        top_k: int = 5,

        metadata_filter: Optional[
            Dict[str, Any]
        ] = None

    ) -> List[Dict[str, Any]]:


        # ----------------------------------------------------
        # VALIDATE QUERY
        # ----------------------------------------------------

        query = query.strip()


        if not query:
            return []


        # ----------------------------------------------------
        # CHECK COLLECTION
        # ----------------------------------------------------

        current_count = (

            self.collection.count()

        )


        if current_count == 0:

            print()

            print(
                "[RETRIEVAL WARNING] "
                "Vector database is empty."
            )

            return []


        # ----------------------------------------------------
        # SAFE TOP K
        # ----------------------------------------------------

        safe_top_k = min(

            max(
                1,
                top_k
            ),

            current_count

        )


        print()

        print(
            "[RETRIEVAL LOG] "
            "Vector search started."
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Query: '{query}'"
        )

        print(
            f"[RETRIEVAL LOG] "
            f"Requested Results: {safe_top_k}"
        )


        if metadata_filter:

            print(
                f"[RETRIEVAL LOG] "
                f"Metadata Filter: "
                f"{metadata_filter}"
            )


        # ----------------------------------------------------
        # GENERATE QUERY EMBEDDING
        # ----------------------------------------------------

        query_embedding = (

            generate_query_embedding(
                query
            )

        )


        # ----------------------------------------------------
        # PREPARE QUERY PARAMETERS
        # ----------------------------------------------------

        query_params = {

            "query_embeddings": [
                query_embedding
            ],

            "n_results": safe_top_k,

            "include": [

                "documents",

                "metadatas",

                "distances"

            ]

        }


        if metadata_filter:

            query_params[
                "where"
            ] = metadata_filter


        # ----------------------------------------------------
        # QUERY CHROMADB
        # ----------------------------------------------------

        try:

            result = (

                self.collection.query(
                    **query_params
                )

            )


        except Exception as error:

            print()

            print(
                "[RETRIEVAL ERROR] "
                "ChromaDB search failed."
            )

            print(
                f"[RETRIEVAL ERROR] {error}"
            )

            raise


        # ----------------------------------------------------
        # EXTRACT RESULTS
        # ----------------------------------------------------

        matches = []


        ids = result.get(
            "ids",
            [[]]
        )[0] or []


        documents = result.get(
            "documents",
            [[]]
        )[0] or []


        metadatas = result.get(
            "metadatas",
            [[]]
        )[0] or []


        distances = result.get(
            "distances",
            [[]]
        )[0] or []


        # ----------------------------------------------------
        # PROCESS RESULTS
        # ----------------------------------------------------

        for index, record_id in enumerate(ids):


            document = (

                documents[index]

                if index < len(documents)

                else ""

            )


            metadata = (

                metadatas[index]

                if index < len(metadatas)

                else {}

            )


            distance = (

                distances[index]

                if index < len(distances)

                else None

            )


            vector_score = (

                normalize_vector_score(
                    distance
                )

            )


            match = {

                "id":
                record_id,

                "text":
                document,

                "metadata":
                metadata,

                "vector_score":
                vector_score,

                "distance":

                round(
                    float(distance),
                    6
                )

                if distance is not None

                else None

            }


            matches.append(
                match
            )


        print()

        print(
            "[RETRIEVAL SUCCESS] "
            f"Vector search returned "
            f"{len(matches)} result(s)."
        )


        return matches


    # ========================================================
    # HYBRID SEARCH
    # ========================================================

    def search(

        self,

        query: str,

        top_k: int = 3,

        metadata_filter: Optional[
            Dict[str, Any]
        ] = None

    ) -> List[Dict[str, Any]]:


        query = query.strip()


        if not query:
            return []


        print()

        print(
            "=" * 75
        )

        print(
            "[RETRIEVAL LOG] "
            "Starting Hybrid Search"
        )

        print(
            "=" * 75
        )


        # ----------------------------------------------------
        # FETCH EXTRA RESULTS
        # ----------------------------------------------------

        current_count = (

            self.collection.count()

        )


        if current_count == 0:
            return []


        fetch_k = min(

            max(
                top_k * 3,
                10
            ),

            current_count

        )


        # ----------------------------------------------------
        # VECTOR SEARCH
        # ----------------------------------------------------

        vector_results = (

            self.vector_search(

                query=query,

                top_k=fetch_k,

                metadata_filter=metadata_filter

            )

        )


        if not vector_results:

            print()

            print(
                "[RETRIEVAL WARNING] "
                "No matching documents found."
            )

            return []


        # ----------------------------------------------------
        # HYBRID SCORING
        # ----------------------------------------------------

        scored_results = []


        for result in vector_results:


            text = result.get(
                "text",
                ""
            )


            vector_score = result.get(
                "vector_score",
                0.0
            )


            keyword_score = (

                calculate_keyword_score(

                    query,

                    text

                )

            )


            hybrid_score = (

                self.alpha
                *
                vector_score

                +

                self.beta
                *
                keyword_score

            )


            enriched_result = {

                "id":
                result["id"],

                "text":
                text,

                "metadata":
                result.get(
                    "metadata",
                    {}
                ),

                "distance":
                result.get(
                    "distance"
                ),

                "vector_score":

                round(
                    vector_score,
                    4
                ),

                "keyword_score":

                round(
                    keyword_score,
                    4
                ),

                "hybrid_score":

                round(
                    hybrid_score,
                    4
                )

            }


            scored_results.append(
                enriched_result
            )


        # ----------------------------------------------------
        # SORT RESULTS
        # ----------------------------------------------------

        scored_results.sort(

            key=lambda item: (

                item["hybrid_score"],

                item["vector_score"],

                item["keyword_score"]

            ),

            reverse=True

        )


        # ----------------------------------------------------
        # FINAL RESULTS
        # ----------------------------------------------------

        final_results = (

            scored_results[
                :top_k
            ]

        )


        # ----------------------------------------------------
        # ADD RANK
        # ----------------------------------------------------

        for rank, result in enumerate(

            final_results,

            start=1

        ):

            result[
                "rank"
            ] = rank


        print()

        print(
            "[RETRIEVAL SUCCESS] "
            f"Found {len(final_results)} "
            f"relevant chunk(s)."
        )


        return final_results


    # ========================================================
    # SEARCH WITH SOURCES + GUARDRAILS
    # ========================================================

    def search_with_sources(

        self,

        query: str,

        top_k: int = 3,

        metadata_filter: Optional[
            Dict[str, Any]
        ] = None

    ) -> Dict[str, Any]:


        # ----------------------------------------------------
        # QUERY GUARDRAIL
        # ----------------------------------------------------

        if not is_scheme_related_query(query):

            print()

            print(
                "[GUARDRAIL] "
                "Unrelated query blocked."
            )


            return {

                "allowed": False,

                "message": (
                    "I can only assist with government welfare "
                    "schemes, eligibility, benefits, applications, "
                    "documents, and scheme-related information."
                ),

                "query": query,

                "total_results": 0,

                "results": [],

                "sources": []

            }


        # ----------------------------------------------------
        # RETRIEVE RESULTS
        # ----------------------------------------------------

        results = (

            self.search(

                query=query,

                top_k=top_k,

                metadata_filter=metadata_filter

            )

        )


        # ----------------------------------------------------
        # RETRIEVAL QUALITY GUARDRAIL
        # ----------------------------------------------------

        if not is_retrieval_strong(results):


            top_score = (

                results[0].get(
                    "hybrid_score",
                    0.0
                )

                if results

                else 0.0

            )


            print()

            print(
                "[GUARDRAIL] "
                "Weak retrieval results blocked."
            )

            print(
                f"[GUARDRAIL] "
                f"Top Score: {top_score}"
            )

            print(
                f"[GUARDRAIL] "
                f"Minimum Required: "
                f"{MIN_RETRIEVAL_SCORE}"
            )


            return {

                "allowed": False,

                "message":
                WEAK_CONTEXT_MESSAGE,

                "query":
                query,

                "total_results":
                len(results),

                "results":
                [],

                "sources":
                [],

                "top_score":
                top_score

            }


        # ----------------------------------------------------
        # BUILD SOURCES
        # ----------------------------------------------------

        sources = []

        seen_sources = set()


        for result in results:


            metadata = result.get(
                "metadata",
                {}
            )


            source = metadata.get(
                "source",
                "Unknown Source"
            )


            chunk_index = metadata.get(
                "chunk_index",
                "Unknown"
            )


            source_key = (

                source,

                chunk_index

            )


            if source_key not in seen_sources:


                sources.append({

                    "source":
                    source,

                    "chunk_index":
                    chunk_index,

                    "chunk_id":
                    result.get(
                        "id"
                    ),

                    "rank":
                    result.get(
                        "rank"
                    ),

                    "score":
                    result.get(
                        "hybrid_score"
                    )

                })


                seen_sources.add(
                    source_key
                )


        # ----------------------------------------------------
        # SUCCESS RESPONSE
        # ----------------------------------------------------

        return {

            "allowed": True,

            "message":
            "Relevant scheme information found.",

            "query":
            query,

            "total_results":
            len(results),

            "results":
            results,

            "sources":
            sources,

            "top_score":

            results[0].get(
                "hybrid_score",
                0.0
            )

        }


    # ========================================================
    # FILTERED SEARCH BY SOURCE
    # ========================================================

    def search_by_source(

        self,

        query: str,

        source: str,

        top_k: int = 3

    ) -> List[Dict[str, Any]]:


        if not source or not source.strip():

            raise ValueError(
                "Source cannot be empty."
            )


        metadata_filter = {

            "source":
            source.strip()

        }


        print()

        print(
            "[RETRIEVAL LOG] "
            f"Filtering source: {source}"
        )


        return (

            self.search(

                query=query,

                top_k=top_k,

                metadata_filter=metadata_filter

            )

        )


    # ========================================================
    # COMPARE FILTERED VS UNFILTERED
    # ========================================================

    def compare_filtered_unfiltered(

        self,

        query: str,

        metadata_filter: Dict[str, Any],

        top_k: int = 3

    ) -> Dict[str, Any]:


        print()

        print(
            "[RETRIEVAL LOG] "
            "Running filtered search..."
        )


        filtered_results = (

            self.search(

                query=query,

                top_k=top_k,

                metadata_filter=metadata_filter

            )

        )


        print()

        print(
            "[RETRIEVAL LOG] "
            "Running unfiltered search..."
        )


        unfiltered_results = (

            self.search(

                query=query,

                top_k=top_k,

                metadata_filter=None

            )

        )


        filtered_ids = {

            result["id"]

            for result in filtered_results

        }


        unfiltered_ids = {

            result["id"]

            for result in unfiltered_results

        }


        delta_ids = list(

            unfiltered_ids

            -

            filtered_ids

        )


        return {

            "query":
            query,

            "filter":
            metadata_filter,

            "filtered":
            filtered_results,

            "unfiltered":
            unfiltered_results,

            "delta_ids":
            delta_ids

        }


    # ========================================================
    # BUILD CONTEXT FOR AI
    # ========================================================

    def build_context(

        self,

        query: str,

        top_k: int = 3,

        results: Optional[
            List[Dict[str, Any]]
        ] = None

    ) -> str:
        """
        Builds retrieved document context
        that can be sent to OpenAI or Gemini.
        """


        # ----------------------------------------------------
        # USE PROVIDED RESULTS OR SEARCH
        # ----------------------------------------------------

        if results is None:

            results = (

                self.search(

                    query=query,

                    top_k=top_k

                )

            )


        # ----------------------------------------------------
        # NO RESULTS
        # ----------------------------------------------------

        if not results:

            print()

            print(
                "[GUARDRAIL] "
                "No context found."
            )


            return WEAK_CONTEXT_MESSAGE


        # ----------------------------------------------------
        # RETRIEVAL QUALITY CHECK
        # ----------------------------------------------------

        if not is_retrieval_strong(results):

            print()

            print(
                "[GUARDRAIL] "
                "Weak context blocked from AI."
            )

            print(
                f"[GUARDRAIL] "
                f"Top Score: "
                f"{results[0].get('hybrid_score', 0.0)}"
            )


            return WEAK_CONTEXT_MESSAGE


        # ----------------------------------------------------
        # BUILD CONTEXT
        # ----------------------------------------------------

        context_parts = []


        for result in results:


            metadata = result.get(
                "metadata",
                {}
            )


            source = metadata.get(
                "source",
                "Unknown Source"
            )


            chunk_index = metadata.get(
                "chunk_index",
                "Unknown"
            )


            hybrid_score = result.get(
                "hybrid_score",
                0.0
            )


            text = result.get(
                "text",
                ""
            )


            context_parts.append(

                f"""
SOURCE: {source}

CHUNK: {chunk_index}

RELEVANCE SCORE: {hybrid_score}

CONTENT:
{text}
"""

            )


        context = (

            "\n"

            "=============================="

            "\n"

            "RETRIEVED SCHEME CONTEXT"

            "\n"

            "=============================="

            "\n"

            +

            "\n".join(
                context_parts
            )

        )


        print()

        print(
            "[RETRIEVAL SUCCESS] "
            "Strong context prepared for AI."
        )


        return context


# ============================================================
# TEST SINGLE QUERY
# ============================================================

def test_single_query(

    retriever: SchemeRetriever,

    query: str

):


    print()

    print(
        "=" * 75
    )

    print(
        f"QUERY: {query}"
    )

    print(
        "=" * 75
    )


    results = (

        retriever.search_with_sources(

            query=query,

            top_k=3

        )

    )


    # --------------------------------------------------------
    # CHECK GUARDRAIL
    # --------------------------------------------------------

    if not results.get(
        "allowed",
        False
    ):

        print()

        print(
            "[GUARDRAIL RESPONSE]"
        )

        print(
            results.get(
                "message"
            )
        )

        return


    # --------------------------------------------------------
    # DISPLAY TOTAL RESULTS
    # --------------------------------------------------------

    print()

    print(
        f"TOTAL RESULTS: "
        f"{results['total_results']}"
    )


    if not results["results"]:

        print()

        print(
            "No relevant documents found."
        )

        return


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    for result in results[
        "results"
    ]:


        print()

        print(
            "-" * 75
        )

        print(
            f"RANK: {result['rank']}"
        )

        print(
            f"SOURCE: "
            f"{result['metadata'].get('source')}"
        )

        print(
            f"CHUNK: "
            f"{result['metadata'].get('chunk_index')}"
        )

        print(
            f"HYBRID SCORE: "
            f"{result['hybrid_score']}"
        )

        print(
            f"VECTOR SCORE: "
            f"{result['vector_score']}"
        )

        print(
            f"KEYWORD SCORE: "
            f"{result['keyword_score']}"
        )

        print(
            f"DISTANCE: "
            f"{result.get('distance')}"
        )

        print()

        print(
            "TEXT PREVIEW:"
        )

        print(
            result["text"][:500]
        )


    # --------------------------------------------------------
    # DISPLAY SOURCES
    # --------------------------------------------------------

    print()

    print(
        "-" * 75
    )

    print(
        "SOURCES:"
    )


    for source in results[
        "sources"
    ]:

        print(

            f"- {source['source']} "

            f"(Chunk {source['chunk_index']}) "

            f"Score: {source['score']}"

        )


# ============================================================
# TEST RETRIEVAL
# ============================================================

def test_retrieval():


    print()

    print(
        "=" * 75
    )

    print(
        "SCHEMEASSIST RETRIEVAL TEST"
    )

    print(
        "=" * 75
    )


    # --------------------------------------------------------
    # CREATE RETRIEVER
    # --------------------------------------------------------

    retriever = SchemeRetriever()


    # --------------------------------------------------------
    # TEST QUERIES
    # --------------------------------------------------------

    test_queries = [

        "Who is eligible for PM Kisan?",

        "How can senior citizens receive pension?",

        "What are the benefits of Ayushman Bharat?",

        "Who can apply for government scholarships?",

        "How can I get housing assistance under PMAY?",

        "What is the capital of France?"

    ]


    # --------------------------------------------------------
    # RUN TESTS
    # --------------------------------------------------------

    for query in test_queries:

        test_single_query(

            retriever=retriever,

            query=query

        )


    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    print()

    print(
        "=" * 75
    )

    print(
        "RETRIEVAL TEST COMPLETED"
    )

    print(
        "=" * 75
    )


# ============================================================
# INTERACTIVE TEST
# ============================================================

def interactive_test():
    """
    Allows testing custom questions
    directly from the terminal.
    """


    print()

    print(
        "=" * 75
    )

    print(
        "SCHEMEASSIST INTERACTIVE RETRIEVAL"
    )

    print(
        "Type 'exit' to stop."
    )

    print(
        "=" * 75
    )


    retriever = SchemeRetriever()


    while True:


        print()


        query = input(
            "Ask a scheme question: "
        ).strip()


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if query.lower() in [

            "exit",

            "quit",

            "q"

        ]:

            print()

            print(
                "Interactive retrieval stopped."
            )

            break


        # ----------------------------------------------------
        # EMPTY QUERY
        # ----------------------------------------------------

        if not query:

            print(
                "Please enter a question."
            )

            continue


        # ----------------------------------------------------
        # TEST QUERY
        # ----------------------------------------------------

        try:

            test_single_query(

                retriever=retriever,

                query=query

            )


        except Exception as error:

            print()

            print(
                "[RETRIEVAL ERROR] "
                f"{error}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    interactive_test()

    # Uncomment this to run
    # all predefined test queries.

    # test_retrieval()