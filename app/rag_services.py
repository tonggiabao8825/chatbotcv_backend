import json
import chromadb
from sentence_transformers import SentenceTransformer
import networkx as nx
import redis

class RAGServices:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.kg_collection = self.client.get_or_create_collection(name="kg_nodes")
        self.graph = nx.DiGraph()
        
        try:
            self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis.ping()
            self.use_redis = True
        except:
            self.use_redis = False
            self.memory = {}

        self.load_cv()
        self.load_kg()

    def load_cv(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            chunks = []
            
            # Basic
            chunks.append(f"Info: {data.get('ho_ten')}, {data.get('nam_sinh')}")
            
            # Edu
            if 'hoc_van' in data:
                chunks.append(f"Education: {data['hoc_van']}")
            
            # Skills
            if 'ky_nang_chuyen_mon' in data:
                chunks.append(f"Skills: {data['ky_nang_chuyen_mon']}")
                
            # Projects
            if 'du_an_tieu_bieu' in data:
                chunks.append(f"Projects: {data['du_an_tieu_bieu']}")
            
            # Story
            if 'cau_chuyen_phat_trien' in data:
                chunks.append(f"Story: {data['cau_chuyen_phat_trien']}")

            if 'dich_vu_cung_cap' in data:
                chunks.append(f"Services: {data['dich_vu_cung_cap']}")

            if 'fun_fact' in data:
                chunks.append(f"Fun fact: {data['fun_fact']}")
                
            if 'muc_tieu_nghe_nghiep' in data:
                chunks.append(f"Goal: {data['muc_tieu_nghe_nghiep']}")

            try:
                ids = [str(i) for i in range(len(chunks))]
                embeddings = self.model.encode(chunks).tolist()
                self.collection.upsert(ids=ids, documents=chunks, embeddings=embeddings)
            except Exception as e:
                print(e)
                
        except Exception as e:
            print("Error loading CV:", e)

    def load_kg(self):
        try:
            with open("KG.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            node_texts = []
            node_ids = []
            
            for n in data.get('nodes', []):
                self.graph.add_node(n['id'], **n)
                # Create text representation for embedding
                txt = f"Name: {n.get('name')}, Type: {n.get('label')}"
                if n.get('relation'): txt += f", Relation: {n.get('relation')}"
                if n.get('role'): txt += f", Role: {n.get('role')}"
                node_texts.append(txt)
                node_ids.append(n['id'])
                
            for r in data.get('relationships', []):
                self.graph.add_edge(r['from'], r['to'], **r)

            # Index nodes to ChromaDB
            try:
                embeddings = self.model.encode(node_texts).tolist()
                self.kg_collection.upsert(ids=node_ids, documents=node_texts, embeddings=embeddings)
            except Exception as e:
                print(e)

        except:
            print("Error loading KG")

    def retrieve_cv_info(self, query):
        try:
            vec = self.model.encode(query).tolist()
            res = self.collection.query(query_embeddings=[vec], n_results=5)
            
            out = []
            if res['documents']:
                for doc in res['documents'][0]:
                    out.append({'text': doc})
            return out
        except:
            return []

    def query_kg(self, query):
        try:
            # Semantic search for nodes
            vec = self.model.encode(query).tolist()
            res = self.kg_collection.query(query_embeddings=[vec], n_results=3) # Top 3 relevant nodes
            
            relevant_nodes = []
            relevant_edges = []
            
            if res['ids'] and len(res['ids'][0]) > 0:
                top_node_ids = res['ids'][0]
                
                for node_id in top_node_ids:
                    # Get node data
                    if self.graph.has_node(node_id):
                        relevant_nodes.append(self.graph.nodes[node_id])
                        
                        # Get 1-hop edges
                        # Outgoing
                        for _, v, d in self.graph.out_edges(node_id, data=True):
                            relevant_nodes.append(self.graph.nodes[v])
                            relevant_edges.append({
                                'from': self.graph.nodes[node_id],
                                'to': self.graph.nodes[v],
                                'relationship': d
                            })
                        # Incoming
                        for u, _, d in self.graph.in_edges(node_id, data=True):
                            relevant_nodes.append(self.graph.nodes[u])
                            relevant_edges.append({
                                'from': self.graph.nodes[u],
                                'to': self.graph.nodes[node_id],
                                'relationship': d
                            })
            
            # Remove duplicates
            unique_nodes = {n['id']: n for n in relevant_nodes}.values()
            
            return {
                'nodes': list(unique_nodes)[:10], 
                'relationships': relevant_edges[:10]
            }
        except Exception as e:
            print(e)
            return {'nodes': [], 'relationships': []}

    def get_session_history(self, session_id):
        if self.use_redis:
            d = self.redis.get(f"sess:{session_id}")
            return json.loads(d) if d else []
        return self.memory.get(session_id, [])

    def save_session_history(self, session_id, history):
        if self.use_redis:
            self.redis.set(f"sess:{session_id}", json.dumps(history))
        else:
            self.memory[session_id] = history

    def clear_session(self, session_id):
        if self.use_redis:
            self.redis.delete(f"sess:{session_id}")
        else:
            self.memory.pop(session_id, None)