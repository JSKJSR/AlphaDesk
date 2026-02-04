import chromadb
from chromadb.config import Settings

# Optional: Use OpenAI embeddings if available, otherwise use ChromaDB's default
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class FinancialSituationMemory:
    """Memory system for storing and retrieving financial situations and advice.

    Uses ChromaDB for vector storage. If OpenAI is available, uses OpenAI embeddings.
    Otherwise, uses ChromaDB's default embedding function.
    """

    def __init__(self, name, config):
        self.config = config
        self.use_openai_embeddings = OPENAI_AVAILABLE and config.get("backend_url")

        if self.use_openai_embeddings:
            if config.get("backend_url") == "http://localhost:11434/v1":
                self.embedding = "nomic-embed-text"
            else:
                self.embedding = "text-embedding-3-small"
            self.openai_client = OpenAI(base_url=config.get("backend_url"))
        else:
            self.embedding = None
            self.openai_client = None

        # Use ChromaDB with default embeddings when OpenAI not available
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))

        if self.use_openai_embeddings:
            # Create collection without embedding function (we'll provide embeddings manually)
            self.situation_collection = self.chroma_client.create_collection(name=name)
        else:
            # Use ChromaDB's default embedding function
            self.situation_collection = self.chroma_client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )

    def get_embedding(self, text):
        """Get embedding for a text. Uses OpenAI if available, else returns None."""
        if not self.use_openai_embeddings:
            return None

        response = self.openai_client.embeddings.create(
            model=self.embedding, input=text
        )
        return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice.

        Parameter is a list of tuples (situation, recommendation)
        """
        if not situations_and_advice:
            return

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            if self.use_openai_embeddings:
                embeddings.append(self.get_embedding(situation))

        if self.use_openai_embeddings:
            self.situation_collection.add(
                documents=situations,
                metadatas=[{"recommendation": rec} for rec in advice],
                embeddings=embeddings,
                ids=ids,
            )
        else:
            # Let ChromaDB compute embeddings automatically
            self.situation_collection.add(
                documents=situations,
                metadatas=[{"recommendation": rec} for rec in advice],
                ids=ids,
            )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using embeddings."""
        if self.situation_collection.count() == 0:
            return []

        if self.use_openai_embeddings:
            query_embedding = self.get_embedding(current_situation)
            results = self.situation_collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_matches, self.situation_collection.count()),
                include=["metadatas", "documents", "distances"],
            )
        else:
            # Let ChromaDB compute query embedding automatically
            results = self.situation_collection.query(
                query_texts=[current_situation],
                n_results=min(n_matches, self.situation_collection.count()),
                include=["metadatas", "documents", "distances"],
            )

        matched_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                matched_results.append(
                    {
                        "matched_situation": results["documents"][0][i],
                        "recommendation": results["metadatas"][0][i]["recommendation"],
                        "similarity_score": 1 - results["distances"][0][i],
                    }
                )

        return matched_results


if __name__ == "__main__":
    # Example usage
    from tradingagents.default_config import DEFAULT_CONFIG
    matcher = FinancialSituationMemory("test_memory", DEFAULT_CONFIG)

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
