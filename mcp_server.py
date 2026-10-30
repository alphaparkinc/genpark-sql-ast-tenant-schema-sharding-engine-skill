"""MCP server for SQL AST Tenant Schema Sharding Engine."""
import sys
import json
from client import SqlTenantShardingEngine

def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "shard_query",
                    "description": "Calculate shard mapping and inject tenant isolation predicates into SQL queries",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "sql_statement": {"type": "string"},
                            "tenant_id": {"type": "string"},
                            "num_shards": {"type": "integer", "default": 4}
                        },
                        "required": ["sql_statement"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "shard_query":
            out = SqlTenantShardingEngine.shard_query(
                args.get("sql_statement", ""),
                args.get("tenant_id"),
                int(args.get("num_shards", 4))
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
    return {"error": "Unsupported method or tool"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
