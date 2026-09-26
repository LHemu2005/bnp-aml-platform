import pandas as pd
import networkx as nx
from collections import defaultdict
import datetime

class AMLEngine:
    def __init__(self, data_path="aml_dataset.csv"):
        self.df = pd.read_csv(data_path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.G = self._build_graph()
        self.risk_scores = defaultdict(lambda: {"score": 0, "reasons": []})
        
    def _build_graph(self):
        G = nx.MultiDiGraph()
        for _, row in self.df.iterrows():
            G.add_edge(
                row['sender_account'], 
                row['receiver_account'], 
                amount=row['amount'], 
                txn_id=row['transaction_id'],
                date=row['timestamp'],
                ip=row['ip_address'],
                device=row['device_id'],
                is_crypto=row['is_crypto']
            )
        return G
        
    def detect_structuring(self):
        threshold = 10000
        for sender, receiver, data in self.G.edges(data=True):
            amt = data['amount']
            if amt < threshold:
                self.risk_scores[sender]['score'] += 10
                if "Potential Structuring detected (<10k INR)" not in self.risk_scores[sender]['reasons']:
                    self.risk_scores[sender]['reasons'].append("Potential Structuring detected (<10k INR)")

    def detect_circular_flow(self):
        try:
            # OPTIMIZATION: Only search for cycles up to length 4 to prevent infinite hangs on dense graphs
            simple_G = nx.DiGraph(self.G)
            cycles = list(nx.simple_cycles(simple_G, length_bound=4))
            for cycle in cycles:
                if len(cycle) > 2: # At least A -> B -> C -> A
                    for node in cycle:
                        self.risk_scores[node]['score'] += 50
                        reason = f"Involved in Circular Flow ring: {' -> '.join(cycle)}"
                        if reason not in self.risk_scores[node]['reasons']:
                            self.risk_scores[node]['reasons'].append(reason)
        except Exception as e:
            print("Error in circular flow:", e)

    def detect_crypto_offramp(self):
        for node in self.G.nodes():
            out_edges = self.G.out_edges(node, data=True)
            for u, v, data in out_edges:
                if data.get('is_crypto'):
                    self.risk_scores[u]['score'] += 40
                    reason = f"Crypto off-ramping to {v}"
                    if reason not in self.risk_scores[u]['reasons']:
                        self.risk_scores[u]['reasons'].append(reason)

    def detect_high_value(self):
        for sender, receiver, data in self.G.edges(data=True):
            if data['amount'] > 1000000:
                self.risk_scores[sender]['score'] += 30
                if "High value transaction > 1,000,000" not in self.risk_scores[sender]['reasons']:
                    self.risk_scores[sender]['reasons'].append("High value transaction > 1,000,000")

    def detect_shared_identifiers(self):
        ip_map = defaultdict(set)
        for _, row in self.df.iterrows():
            ip_map[row['ip_address']].add(row['sender_account'])
            
        for ip, accounts in ip_map.items():
            if len(accounts) > 2:
                for acc in accounts:
                    self.risk_scores[acc]['score'] += 20
                    reason = f"Shared IP Address ({ip}) with multiple accounts"
                    if reason not in self.risk_scores[acc]['reasons']:
                        self.risk_scores[acc]['reasons'].append(reason)

    def run_all_rules(self):
        self.detect_structuring()
        self.detect_circular_flow()
        self.detect_crypto_offramp()
        self.detect_high_value()
        self.detect_shared_identifiers()
        
        for acc in self.risk_scores:
            self.risk_scores[acc]['score'] = min(100, self.risk_scores[acc]['score'])
            score = self.risk_scores[acc]['score']
            if score >= 80:
                self.risk_scores[acc]['level'] = 'Critical'
            elif score >= 60:
                self.risk_scores[acc]['level'] = 'High'
            elif score >= 30:
                self.risk_scores[acc]['level'] = 'Medium'
            else:
                self.risk_scores[acc]['level'] = 'Low'

        return self.risk_scores

    def get_graph_data(self):
        suspicious_nodes = {node for node, data in self.risk_scores.items() if data.get('score', 0) >= 30}
        
        nodes_to_include = set(suspicious_nodes)
        for node in suspicious_nodes:
            if self.G.has_node(node):
                nodes_to_include.update(self.G.predecessors(node))
                nodes_to_include.update(self.G.successors(node))

        nodes = []
        edges = []
        
        for u in nodes_to_include:
            score = self.risk_scores.get(u, {}).get('score', 0)
            level = self.risk_scores.get(u, {}).get('level', 'Low')
            nodes.append({"id": u, "label": u, "value": score if score > 0 else 10, "group": level})
            
        for u, v, d in self.G.edges(data=True):
            if u in nodes_to_include and v in nodes_to_include:
                edges.append({
                    "from": u,
                    "to": v,
                    "label": f"{d['amount']}",
                    "arrows": "to"
                })
            
        return {"nodes": nodes, "edges": edges}

    def get_account_timeline(self, account_id):
        user_txns = self.df[(self.df['sender_account'] == account_id) | (self.df['receiver_account'] == account_id)].sort_values('timestamp')
        return user_txns.fillna("").to_dict(orient='records')
