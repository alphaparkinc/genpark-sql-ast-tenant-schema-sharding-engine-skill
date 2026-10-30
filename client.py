"""SQL AST Tenant Schema Sharding Engine.
100% Python Standard Library.
"""

import hashlib

class SqlTenantShardingEngine:
    """Inspects query tokens to inject tenant isolation predicates and routes cross-shard scatter-gather queries."""

    @staticmethod
    def calculate_shard_id(tenant_id: str, num_shards: int = 4) -> int:
        h = int(hashlib.md5(tenant_id.encode("utf-8")).hexdigest(), 16)
        return h % num_shards

    @classmethod
    def shard_query(cls, sql_statement: str, tenant_id: str = None, num_shards: int = 4) -> dict:
        raw_sql = sql_statement.strip()
        sql_upper = raw_sql.upper()

        if not tenant_id:
            all_shards = [f"shard_{i}" for i in range(num_shards)]
            return {
                "routing_mode": "SCATTER_GATHER",
                "target_shards": all_shards,
                "shards_involved_count": len(all_shards),
                "rewritten_sql": raw_sql,
                "warning": "Cross-shard multi-tenant query requires distributed scatter-gather aggregation"
            }

        shard_idx = cls.calculate_shard_id(tenant_id, num_shards)
        target_shard = f"shard_{shard_idx}"
        has_tenant_filter = "TENANT_ID" in sql_upper

        rewritten = raw_sql
        if not has_tenant_filter:
            if "WHERE" in sql_upper:
                where_pos = sql_upper.find("WHERE") + 5
                rewritten = raw_sql[:where_pos] + f" tenant_id = '{tenant_id}' AND " + raw_sql[where_pos:]
            else:
                rewritten = raw_sql + f" WHERE tenant_id = '{tenant_id}'"

        return {
            "routing_mode": "DIRECT_SHARD",
            "target_shard": target_shard,
            "shard_index": shard_idx,
            "tenant_id": tenant_id,
            "rewritten_sql": rewritten,
            "tenant_predicate_injected": not has_tenant_filter
        }
