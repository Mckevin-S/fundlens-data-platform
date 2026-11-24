# Databricks notebook source
# MAGIC %md
# MAGIC # VaR historique par fonds
# MAGIC Lit les rendements quotidiens des fonds (table `marts.fct_nav`), calcule la VaR historique
# MAGIC à 95 % et 99 % sur 250 jours et écrit le résultat dans `marts.fund_var`.

# COMMAND ----------
from risk import historical_var, returns_from_navs

# COMMAND ----------
navs = spark.table("marts.fct_nav").select("fund_id", "as_of", "nav_per_share").orderBy("fund_id", "as_of")

rows = []
for fund_id, group in navs.toPandas().groupby("fund_id"):
    returns = returns_from_navs([float(x) for x in group["nav_per_share"]][-251:])
    if len(returns) >= 20:
        rows.append((fund_id, historical_var(returns, 0.95), historical_var(returns, 0.99), len(returns)))

# COMMAND ----------
result = spark.createDataFrame(rows, "fund_id string, var_95 double, var_99 double, observations int")
result.write.mode("overwrite").saveAsTable("marts.fund_var")
display(result)
