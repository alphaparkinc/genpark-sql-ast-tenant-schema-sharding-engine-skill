"""Example usage for SQL AST Tenant Schema Sharding Engine."""
from client import SqlTenantShardingEngine

if __name__ == "__main__":
    direct = SqlTenantShardingEngine.shard_query("SELECT * FROM invoices WHERE amount > 100", "corp_789")
    print("Direct Shard:", direct)

    scatter = SqlTenantShardingEngine.shard_query("SELECT SUM(amount) FROM invoices", tenant_id=None)
    print("Scatter-Gather:", scatter)
