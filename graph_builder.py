"""
graph_builder.py
Loads extracted (subject, relation, object) triples into a Neo4j graph.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
USER = os.environ["NEO4J_USER"]
PASSWORD = os.environ["NEO4J_PASSWORD"]


class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def clear_graph(self):
        """Wipe everything - useful while iterating during development."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def add_triple(self, subject: str, relation: str, obj: str):
        query = """
        MERGE (a:Entity {name: $subject})
        MERGE (b:Entity {name: $object})
        MERGE (a)-[r:RELATION {type: $relation}]->(b)
        """
        with self.driver.session() as session:
            session.run(query, subject=subject, object=obj, relation=relation)

    def load_triples(self, triples: list[dict]):
        for t in triples:
            self.add_triple(t["subject"], t["relation"], t["object"])
        print(f"Loaded {len(triples)} triples into Neo4j.")


if __name__ == "__main__":
    from entity_extraction import extract_from_document

    sample = """Tata Consultancy Services was founded by the Tata Group in 1968.
    TCS is headquartered in Mumbai. N. Chandrasekaran is the chairman of Tata Sons,
    which is the parent company of TCS."""

    triples = extract_from_document(sample)

    builder = GraphBuilder()
    builder.load_triples(triples)
    builder.close()